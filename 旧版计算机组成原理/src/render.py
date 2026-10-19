"""Render the same browser SVG to a real H.264 file.

--mode keyframes holds a deterministic picture until the next step (fast full course).
--mode smooth captures at output FPS for short motion previews.
No voice generation or audio processing is performed.
"""
import argparse
import asyncio
import json
import math
import shutil
import subprocess
import tempfile
import time
import uuid
from pathlib import Path
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]

def probe(path):
    result=subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-show_chapters','-of','json',str(path)],capture_output=True,text=True,check=True)
    if result.stderr.strip():raise RuntimeError('ffprobe reported media errors: '+result.stderr.strip())
    return json.loads(result.stdout)

async def capture(args,frames):
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path=shutil.which('chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
        page=await browser.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1)
        await page.set_content((ROOT/'output/index.html').read_text(),wait_until='load')
        await page.evaluate("document.body.classList.add('export')")
        await page.evaluate('document.fonts.ready')
        if args.mode=='smooth':
            count=round(args.duration*args.fps)
            times=[args.start+i/args.fps for i in range(count)]
        else:
            # Add scene/beat/caption/diagram changes to regular teaching holds.
            relative={0.0,args.duration}
            for x in range(math.floor(args.start/120),math.ceil((args.start+args.duration)/120)):
                offsets={0,12,31,40,45,50,55,57,60,65,69,75,80,87,90,102,110,119}
                if x+1 in (25,30,39):offsets.update(12+i*78/24 for i in range(24))
                if x+1 in (51,52,53,55):offsets.update(12+i*15 for i in range(5))
                if x+1==10:offsets.update(12+i*10 for i in range(8))
                if x+1 in (40,42,43,58):offsets.update(12+i*75/14 for i in range(15))
                for off in offsets:
                    r=x*120+off-args.start
                    if 0<r<args.duration:relative.add(float(r))
            cues=await page.evaluate('window.captionCues')
            for i,group in enumerate(cues):
                for cue in group:
                    r=i*120+cue['start']-args.start
                    if 0<r<args.duration:relative.add(float(r))
            for i in range(1,math.ceil(args.duration/args.hold)):
                relative.add(min(args.duration,float(i*args.hold)))
            # Quantize to the output frame grid so MP4 length is exact.
            relative={round(r*args.fps)/args.fps for r in relative}
            times=[args.start+r for r in sorted(relative) if r<args.duration]
        count=len(times);entries=[]
        for i,t in enumerate(times):
            await page.evaluate('(t)=>window.renderAt(t)',t)
            filename=frames/f'{i:06d}.png'
            await page.locator('#stage').screenshot(path=str(filename),animations='disabled')
            nxt=times[i+1] if i+1<count else args.start+args.duration
            entries.append((filename,nxt-t))
            if i%100==0 or i+1==count:print(f'Captured {i+1}/{count} states',flush=True)
        await browser.close()
    return entries

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--start',type=float,default=0)
    parser.add_argument('--duration',type=float,default=30)
    parser.add_argument('--mode',choices=['keyframes','smooth'],default='keyframes')
    parser.add_argument('--hold',type=float,default=8,help='maximum teaching hold in seconds')
    parser.add_argument('--fps',type=int,default=30)
    parser.add_argument('--output',default='output/silent_preview.mp4')
    parser.add_argument('--keep-frames',action='store_true')
    parser.add_argument('--reuse-frames',type=Path,help='reuse an existing matching frames.txt cache instead of capturing again')
    args=parser.parse_args()
    if args.start<0 or args.duration<=0 or args.start+args.duration>7200 or args.hold<=0:parser.error('invalid range or hold')
    target=Path(args.output).resolve();target.parent.mkdir(parents=True,exist_ok=True)
    staged=target.with_name(target.stem+'.rendering-'+uuid.uuid4().hex[:8]+'.mp4')
    temp=args.reuse_frames.resolve() if args.reuse_frames else Path(tempfile.mkdtemp(prefix='course-render-',dir=ROOT/'output'))
    began=time.monotonic()
    try:
        if args.reuse_frames:
            entries=[];filename=None
            for line in (temp/'frames.txt').read_text().splitlines():
                if line.startswith('file '):filename=Path(line[6:-1])
                elif line.startswith('duration '):entries.append((filename,float(line.split()[1])))
            if not entries or abs(sum(d for _,d in entries)-args.duration)>.01:raise ValueError('cached frame durations do not match requested duration')
        else:entries=asyncio.run(capture(args,temp))
        listing=temp/('vfr_frames.txt' if args.reuse_frames else 'frames.txt')
        if args.mode=='smooth':
            source=['-framerate',str(args.fps),'-i',str(temp/'%06d.png')]
        else:
            # Explicitly timestamp the final displayed frame so VFR ends exactly
            # at the requested duration instead of ending at the last state change.
            if entries[-1][1]>1/args.fps:
                last,duration=entries.pop();entries.extend([(last,duration-1/args.fps),(last,1/args.fps)])
            listing.write_text(''.join(f"file '{p.as_posix()}'\nduration {d:.9f}\n" for p,d in entries)+f"file '{entries[-1][0].as_posix()}'\n")
            source=['-f','concat','-safe','0','-i',str(listing)]
        metadata=(['-i',str(ROOT/'output/chapters.ffmetadata'),'-map','0:v:0','-map_metadata','1']
                  if args.start==0 and args.duration==7200 else ['-map','0:v:0','-metadata','title=计算机组成原理 静音样片'])
        timing=(['-vf',f'fps={args.fps}'] if args.mode=='smooth' else
                ['-fps_mode','vfr','-enc_time_base',f'1:{args.fps}','-g','15'])
        cmd=['ffmpeg','-hide_banner','-loglevel','error','-y',*source,*metadata,*timing,
             '-t',str(args.duration),'-c:v','libx264','-preset','ultrafast','-crf','24',
             '-pix_fmt','yuv420p','-threads','4','-movflags','+faststart',str(staged)]
        print('Encoding H.264…',flush=True)
        subprocess.run(cmd,check=True)
        info=probe(staged)
        staged.replace(target)
        info['format']['filename']=str(target)
        report=dict(file=str(target.relative_to(ROOT)) if target.is_relative_to(ROOT) else str(target),
                    mode=args.mode,start=args.start,duration=args.duration,states=len(entries),
                    elapsed_seconds=round(time.monotonic()-began,1),actual=info)
        target.with_suffix('.metadata.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
        print(json.dumps({k:v for k,v in report.items() if k!='actual'},ensure_ascii=False),flush=True)
    finally:
        staged.unlink(missing_ok=True)
        if not args.keep_frames and not args.reuse_frames:shutil.rmtree(temp)

if __name__=='__main__':main()
