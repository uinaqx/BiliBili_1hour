"""Local ASR sample of actual final AAC. This is not a full-course listening claim."""
import hashlib,json,pathlib,subprocess
import torch,whisper
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
    torch.set_num_threads(4);model=whisper.load_model(str(pathlib.Path.home()/'.cache/whisper/base.pt'),device='cpu')
    t=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf8'));by={s['key']:s for s in t['scenes']}
    video=ROOT/'out/一小时学完408操作系统_基础考点与解题步骤.mp4';out=ROOT/'build/speech-qa';out.mkdir(exist_ok=True);records=[]
    for key,part in [('os-01-05',0),('os-06-04',1),('os-10-02',1)]:
        s=by[key];meta=json.loads((ROOT/'public'/s['audio']).with_suffix('.json').read_text(encoding='utf8'));start=(s['startFrame']+s['leadFrames'])/30+meta['parts'][part]['start'];path=out/(key+'.wav')
        subprocess.run(['ffmpeg','-y','-v','error','-ss',f'{start:.9f}','-i',str(video),'-t','18','-vn','-ar','16000','-ac','1',str(path)],check=True)
        result=model.transcribe(str(path),language='zh',task='transcribe',fp16=False,temperature=0,condition_on_previous_text=False,initial_prompt='操作系统。进程，内核态，页框，地址变换，DMA。')
        record=dict(key=key,part=part,start=start,seconds=18,reference=s['parts'][part]['text'],transcript=result['text']);records.append(record);print(json.dumps(record,ensure_ascii=False),flush=True)
    report=dict(scope='54 seconds sampled from beginning, middle and end of final AAC; ASR is approximate and needs human interpretation',videoSha256=hashlib.sha256(video.read_bytes()).hexdigest(),samples=records)
    (ROOT/'build/speech-spotcheck.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
if __name__=='__main__':main()
