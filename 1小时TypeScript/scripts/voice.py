import concurrent.futures,json,pathlib,sys
import audio as provider
ROOT=pathlib.Path(__file__).resolve().parents[1]
provider.AUDIO=ROOT/'public/audio_original'

def generate(credentials,limit=None):
    credentials={**credentials,'model':provider.MODEL}
    clips=[dict(key=s['key']+f'-p{i:02}',narration=p['text']) for c in json.loads((ROOT/'public/course.json').read_text(encoding='utf8'))['chapters'] for s in c['scenes'] for i,p in enumerate(s['parts'])]
    if limit:clips=clips[:limit]
    def work(clip):
        result=provider.synth(clip,credentials,1.05)
        print('VOICE',result[0],round(result[1],3),result[2],flush=True)
        return result
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(work,clips))
    print('VOICE_DONE',len(results),round(sum(x[1] for x in results),3),flush=True)

if __name__=='__main__':
    import os
    generate(dict(api_key=os.environ.get('DASHSCOPE_API_KEY',''),workspace_id=os.environ.get('SFM_WORKSPACE_ID','')))
