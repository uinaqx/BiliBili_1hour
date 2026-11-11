"""Bailian clips for the modern course. Account configuration is never cached."""
import concurrent.futures,json,os,pathlib,sys
import audio as provider
ROOT=pathlib.Path(__file__).resolve().parents[1]
provider.ROOT=ROOT;provider.AUDIO=ROOT/'public/audio_original'

def generate(credentials,limit=None):
 credentials={**credentials,'model':provider.MODEL}
 course=json.loads((ROOT/'public/course.json').read_text(encoding='utf8'))
 clips=[dict(key=s['key']+f'-p{i:02}',narration=p['text']) for c in course['chapters'] for s in c['scenes'] for i,p in enumerate(s['parts'])]
 if limit:clips=clips[:limit]
 def work(clip):
  result=provider.synth(clip,credentials,1.05);print('VOICE',result[0],round(result[1],3),result[2],flush=True);return result
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(work,clips))
 print('VOICE_DONE',len(results),round(sum(r[1] for r in results),3),flush=True)

if __name__=='__main__':
 generate(dict(api_key=os.environ.get('DASHSCOPE_API_KEY',''),workspace_id=os.environ.get('SFM_WORKSPACE_ID','')),int(sys.argv[sys.argv.index('--limit')+1]) if '--limit' in sys.argv else None)
