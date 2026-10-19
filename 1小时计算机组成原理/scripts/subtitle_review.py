"""Review ASR edge estimates and refine clear sentence starts from frozen PCM."""
import hashlib, pathlib, sys, wave
import numpy as np
from subtitle_calibrate import ROOT, BUILD, BACKUP, load, save
sys.stdout.reconfigure(encoding='utf-8')

def main():
    timeline=load(BACKUP/'timeline.json');records=[];refined=[];unresolved=[];independent=[]
    for scene in timeline['scenes']:
        key=scene['key'];path=BUILD/'subtitle-asr'/f'{key}.json';data=load(path)
        audio=ROOT/'public/audio'/f'{key}.wav'
        assert data['audioSha256']==hashlib.sha256(audio.read_bytes()).hexdigest()
        with wave.open(str(audio),'rb') as f:
            rate=f.getframerate();signal=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(float)/32768
        hop=round(rate*.005)
        rms=np.sqrt(np.mean(signal[:len(signal)//hop*hop].reshape(-1,hop)**2,axis=1))
        threshold=max(.001,float(np.percentile(rms,90))*.025)
        active=rms>threshold
        other=load(BUILD/'subtitle-fa'/f'{key}.json')['captions']
        for i,c in enumerate(data['captions']):
            if c.get('noAnchors'):unresolved.append(dict(scene=key,index=i,reason='no semantic anchors',text=c['text']))
            if not c['startExact'] and c['firstMatchedChar'] is not None and c['firstMatchedChar']-c['firstChar']>3:
                if abs(c['onset']-other[i]['onset'])>.15:
                    unresolved.append(dict(scene=key,index=i,reason='long unmatched prefix without independent onset agreement',text=c['text']))
                else:c['edgeReviewResolution']='Independent acoustic onset agrees within 150 ms; recognized following words anchor the phrase'
            start=c['onset'];k=round(start/.005)
            # Only move starts that sit in demonstrable silence. Starts within
            # continuous speech remain at their recognized character boundary.
            if not np.any(active[max(0,k-6):min(len(active),k+10)]):
                end=min(len(active),k+100)
                candidates=[j for j in range(k,end-3) if np.count_nonzero(active[j:j+4])>=3]
                if candidates:
                    onset=candidates[0]*.005
                    if onset-start>.045:
                        refined.append(dict(scene=key,index=i,text=c['text'],oldOnset=start,acousticOnset=onset))
                        c['unrefinedOnset']=start;c['onset']=onset;c['waveformRefined']=True
            if abs(c['onset']-other[i]['onset'])>.3:
                independent.append(dict(scene=key,index=i,text=c['text'],semanticOnset=c['onset'],countPredictionOnset=other[i]['onset'],reason='known-text count model may drift on spoken numbers/Latin tokens; semantic ASR and PCM retained'))
            if i+1<len(data['captions']) and c['offset']>data['captions'][i+1]['onset']+.05:
                assert not c['endExact'],(key,i,'matched tail crosses next phrase')
                c['unrefinedOffset']=c['offset']
                c['offset']=min(other[i]['offset'],data['captions'][i+1]['onset']-.01)
                c['edgeReviewResolution']='An unmatched tail crossed into the next phrase; independent acoustic tail retained'
            block=next((b for b in data['matchingBlocks'] if b['expected']<=c['firstChar']<b['expected']+b['length']),None)
            kind=block['kind'] if block else 'deleted-syllable estimate'
            records.append(dict(scene=key,index=i,startDirectlyRecognized=kind in ['exact','phonetic'],startAligned=c['startExact'],startKind=kind,endAligned=c['endExact'],alignedFraction=c['matchedFraction'],onset=c['onset'],offset=c['offset']))
        assert all(a['onset']<b['onset'] for a,b in zip(data['captions'],data['captions'][1:])),key
        save(path,data)
    assert not unresolved,unresolved
    assert len(records)==len(timeline['captions'])==1396
    report=dict(complete=True,scenes=len(timeline['scenes']),captions=len(records),directlyRecognizedStarts=sum(r['startDirectlyRecognized'] for r in records),substitutedAsrStarts=sum(r['startKind']=='substitution' for r in records),estimatedShortPrefixes=sum(not r['startAligned'] for r in records),waveformOnsetRefinements=refined,unresolved=unresolved,independentCountModelOutliers=independent,records=records,scope='semantic character alignment plus waveform silence checks; not a claim of full human listening')
    save(BUILD/'subtitle-review.json',report)
    print('CAPTION_REVIEW_READY',report['captions'],'direct starts',report['directlyRecognizedStarts'],'short prefixes',report['estimatedShortPrefixes'],'silence corrections',len(refined),'unresolved',len(unresolved),flush=True)
if __name__=='__main__':main()
