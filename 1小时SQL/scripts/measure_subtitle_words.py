"""Measure pause-adjacent word edges on final PCM and bind reviewed revisions."""
import bisect
import json
import pathlib
import sys

import numpy as np

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'00_skills/code-course-video/scripts'))
from subtitle_sync import (authored_words, build_project, load, mapped_words,
                           normalized_words, pause_schedule, pcm_file, sha)

def spans(mask):
    return np.flatnonzero(np.diff(np.r_[False,mask,False])).reshape(-1,2)

def quiet_runs(raw, rate):
    hop=rate//100
    signal=np.frombuffer(raw,dtype='<i2')
    frames=signal[:len(signal)//hop*hop].reshape(-1,hop).astype(np.float32)
    rms=np.sqrt(np.mean(frames**2,axis=1))/32768
    voice=rms>max(.00065,float(np.percentile(rms,90))*.02)
    for a,b in spans(voice):
        if b-a<3:
            voice[a:b]=False
    for a,b in spans(~voice):
        if a and b<len(voice) and b-a<7:
            voice[a:b]=True
    return rms,[(a/100,b/100) for a,b in spans(~voice) if b-a>=8],spans(voice)

def inverse(final,cuts,pauses):
    delta=0.
    for cut,amount in zip(cuts,pauses):
        if final<cut+delta:
            break
        if final<=cut+delta+amount:
            return cut
        delta+=amount
    return final-delta

def main():
    dest=ROOT/'build/subtitle-word-revisions.json'
    draft=build_project(ROOT,font_size=56,max_chars=24,use_revisions=False)
    timeline=load(ROOT/'public/timeline.json')
    aliases=load(ROOT/'content/subtitle-aliases.json')
    terms=load(ROOT/'content/subtitle-terms.json')
    report=load(ROOT/'build/audio-preparation.json')
    offsets={(c['scene'],c['part']):[] for c in draft['cues']}
    for cue in draft['cues']:
        offsets[cue['scene'],cue['part']].append(cue)
    edits={}
    for scene in timeline['scenes']:
        wav=ROOT/'public'/scene['audio']
        meta=wav.with_suffix('.json')
        m=load(meta)
        pcm,fmt=pcm_file(wav)
        rate=fmt[0]
        assert fmt[1:]==(1,2) and rate%100==0
        for i,part in enumerate(m['parts']):
            key=part['rawKey']
            path=ROOT/'build/alignment'/f'{key}.json'
            pre=ROOT/'public/audio'/f'{key}.scaled.wav'
            words=normalized_words(load(path)['words'])
            cuts,pauses=pause_schedule(m,part,i,(report,))
            mapped=mapped_words(words,cuts,pauses,rate)
            located=authored_words(mapped,part['cue'],aliases,terms)
            origin=(scene['startFrame']+scene['leadFrames'])/timeline['fps']+part['start']
            a,b=(round(part[name]*rate) for name in ('start','end'))
            raw=pcm[a*2:b*2]
            rms,quiet,voice=quiet_runs(raw,rate)
            items=offsets[scene['key'],i]
            revised={}
            evidence=[]
            index={w['token']:n for n,w in enumerate(located)}
            def patch(token,field,value):
                revised.setdefault(str(token),{})[field]=round(inverse(value,cuts,pauses),6)
            for left,right in zip(items,items[1:]):
                raw_end=left['spokenEnd']-origin
                raw_start=right['start']-origin
                # Include all valid words contributing to the left envelope.
                left_last=max(left['tokens'],key=lambda j:mapped[j]['end'])
                right_first=right['tokens'][0]
                if right_first<=left_last:
                    continue
                lower=left['start']-origin+.33
                upper=right['spokenEnd']-origin-.2
                if upper<=lower:
                    continue
                # A physical pause is used only close to both lexical anchors.
                # Prioritize verified inserted silence for sentence boundaries.
                candidates=[]
                for a,b in quiet:
                    if (a<lower or b>upper or a<raw_end-.19 or a>raw_end+.48
                        or b<raw_end-.03 or b>raw_start+.23):
                        continue
                    inserted=any(a-.02<=cut+sum(pauses[:j])<=b+.02
                                 for j,cut in enumerate(cuts))
                    rank=abs(a-raw_end)*.75 + abs(b-raw_start)*.55 - min(b-a,.4)*.23
                    if b-a>.42 and (rms[int(round(a*100)):int(round(b*100))]>.0012).any():
                        continue
                    if inserted and left['text'].endswith(('。','？','！','；')):
                        rank-=.22
                    candidates.append((rank,a,b,inserted))
                if candidates:
                    _,end,start,inserted=min(candidates)
                    evidence.append([left_last,right_first,'pcm-quiet',round(end,3),round(start,3),inserted])
                else:
                    # With no measured pause, a joint cut is supported only
                    # where the existing two anchors already enclose sound.
                    lo=max(0,int(np.ceil(max(lower,raw_end-.035)*100)))
                    hi=min(len(rms),int(np.floor(min(upper,raw_start+.025)*100))+1)
                    if hi<=lo or raw_start-raw_end<.13:
                        continue
                    space=np.arange(lo,hi)
                    energy=rms[space]
                    if (energy>.0015).mean()<.35:
                        continue
                    mid=raw_end+(raw_start-raw_end)*.48
                    # Blend weak lexical evidence with a measured low-energy
                    # point. This estimates a word boundary, not caption hold.
                    score=abs(space/100-mid)+energy/max(energy.max(),.001)*.11
                    end=start=float(space[score.argmin()])/100
                    evidence.append([left_last,right_first,'pcm-continuous',end,start,False])
                # Keep token ranges strictly positive and avoid moving an
                # interior token beyond the following timed token.
                if end>mapped[left_last]['start']+.015:
                    patch(left_last,'end',end)
                if start<mapped[right_first]['end']-.015:
                    patch(right_first,'start',start)
            first=items[0]['tokens'][0]
            last=max(items[-1]['tokens'],key=lambda j:mapped[j]['end'])
            if len(voice):
                first_sound,last_sound=voice[0,0]/100,voice[-1,1]/100
                if abs(first_sound-mapped[first]['start'])<=.35 and first_sound<mapped[first]['end']-.015:
                    patch(first,'start',first_sound)
                if abs(last_sound-mapped[last]['end'])<=.45 and last_sound>mapped[last]['start']+.015:
                    patch(last,'end',last_sound)
            if revised:
                edits[key]=dict(alignmentSha256=sha(path),audioSha256=sha(wav),metadataSha256=sha(meta),
                                prePausePcmSha256=sha(pre),words=revised,observations=evidence)
    dest.write_text(json.dumps(edits,ensure_ascii=False,indent=2),encoding='utf8')
    print('WORD_REVISIONS',len(edits),sum(len(s['words']) for s in edits.values()),flush=True)

if __name__=='__main__':main()
