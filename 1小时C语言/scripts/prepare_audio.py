"""Use one whole-course tempo, then align actual audio and keep every phrase visible."""
import json,pathlib,statistics,sys,time
import audio_timing as engine
sys.stdout.reconfigure(encoding='utf-8');ROOT=pathlib.Path(__file__).resolve().parents[1]
course=json.loads((ROOT/'public/course.json').read_text(encoding='utf-8'));scenes=[s for c in course['chapters'] for s in c['scenes']]
def main():
    import torch,whisper
    from whisper.tokenizer import get_tokenizer
    while True:
        missing=[s['key'] for s in scenes if not (ROOT/'public/audio_original'/(s['key']+'.json')).exists()]
        if not missing:break
        print('WAITING_FOR_VOICE',len(missing),flush=True);time.sleep(5)
    raw=[engine.load(ROOT/'public/audio_original'/(s['key']+'.json')) for s in scenes]
    total=sum(m['duration'] for m in raw);pauses=sum(len(engine.old.boundaries(m)) for m in raw)
    fixed=len(scenes)*.4+sum(s['hold'] for s in scenes)+.1*(len(scenes)-1)+.1*pauses
    predicted=total+fixed
    pace=1.0 if 3000<=predicted<=4160 else total/(3800-fixed)
    assert .90<=pace<=1.12,('Revise useful content instead of unnatural speech pacing',pace,total,fixed)
    engine.PACE=pace;engine.VERSION=f'c-acoustic-v1-tempo={pace:.9f}'
    engine.save(ROOT/'build/audio-settings.json',dict(wholeCourseTempo=pace,serviceRate=1.0,rawSeconds=total,predictedFixedSeconds=fixed,targetSeconds=3600,allowedMinSeconds=3000,allowedMaxSeconds=4200,predictedSeconds=predicted,sentencePauseSeconds=.1))
    print('UNIFORM_TEMPO',round(pace,6),'raw seconds',round(total,3),'sentence pauses',pauses,flush=True)
    torch.set_num_threads(4);model=whisper.load_model('base',device='cpu');tokenizer=get_tokenizer(True,language='zh',task='transcribe')
    records=[]
    for i,s in enumerate(scenes,1):
        aligned,cached=engine.align_part(s,model,tokenizer);data=engine.clip(s)
        for j,c in enumerate(data['captions']):c['end']=data['captions'][j+1]['start'] if j+1<len(data['captions']) else data['duration']
        assert all(c['end']>c['start'] for c in data['captions'])
        clean=lambda text:''.join(ch for ch in text if ch.isalnum())
        assert clean(''.join(c['text'] for c in data['captions']))==clean(''.join(w['text'] for w in data['words']))
        engine.save(ROOT/'public/audio'/(s['key']+'.json'),data)
        records.append(dict(key=s['key'],seconds=data['duration'],captions=len(data['captions']),onsetsRefined=len(data['captionOnsetRefinements']),providerDeltaP95=aligned['providerDeltaP95']))
        print('AUDIO_ALIGNED',f'{i}/{len(scenes)}',s['key'],round(data['duration'],3),flush=True)
    engine.save(ROOT/'build/audio-alignment.json',dict(clips=len(records),wholeCourseTempo=pace,method='known-transcript acoustic alignment on actual final-tempo audio, waveform onset refinement, subtitles held until next cue',results=records))
    print('AUDIO_PREPARATION_DONE',round(sum(r['seconds'] for r in records),3),flush=True)
if __name__=='__main__':main()
