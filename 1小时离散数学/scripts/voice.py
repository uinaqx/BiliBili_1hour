import concurrent.futures,json,os,pathlib,sys
import audio as provider
ROOT=pathlib.Path(__file__).resolve().parents[1];provider.ROOT=ROOT;provider.AUDIO=ROOT/'public/audio_original'
def generate(credentials,test=False):
 credentials={**credentials,'model':provider.MODEL}
 clips=[dict(key='voice-test',narration='欢迎来到一小时学完离散数学。我们从能判断真假的句子开始，用真值表检查逻辑，用圆圈表示集合，用箭头表示关系。排列要考虑顺序，组合只关心选了谁。图中的边连接顶点，树则是连通而且没有回路的图。先跟着例子看清楚，再记住名字。')] if test else [dict(key=s['key']+f'-p{i:02}',narration=p['text']) for c in json.loads((ROOT/'public/course.json').read_text(encoding='utf8'))['chapters'] for s in c['scenes'] for i,p in enumerate(s['parts'])]
 def work(clip):
  r=provider.synth(clip,credentials,1.05);print('VOICE',r[0],round(r[1],3),r[2],flush=True);return r
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(work,clips))
 print('VOICE_DONE',len(results),round(sum(r[1] for r in results),3),flush=True)
if __name__=='__main__':
 sys.stdout.reconfigure(encoding='utf8');generate(dict(api_key=os.environ.get('DASHSCOPE_API_KEY',''),workspace_id=os.environ.get('SFM_WORKSPACE_ID','')),'--test' in sys.argv)
