import concurrent.futures,json,os,pathlib,sys
import audio as provider
ROOT=pathlib.Path(__file__).resolve().parents[1];provider.ROOT=ROOT;provider.AUDIO=ROOT/'public/audio_original'
def generate(credentials,test=False):
 credentials={**credentials,'model':provider.MODEL}
 clips=[dict(key='voice-test',narration='欢迎来到一小时讲完数字电子技术。我们先把零和一、逻辑门与真值表弄清楚，再用触发器保存状态，用计数器按节拍更新。看波形时，先找到时钟的有效边沿，再判断数据什么时候被采样。建立时间与保持时间，是输入在边沿前后需要稳定的要求。先看图，再写规则，最后用例题核对。')] if test else [dict(key=s['key']+f'-p{i:02}',narration=p['text']) for c in json.loads((ROOT/'public/course.json').read_text(encoding='utf8'))['chapters'] for s in c['scenes'] for i,p in enumerate(s['parts'])]
 def work(clip):
  r=provider.synth(clip,credentials,1.05);print('VOICE',r[0],round(r[1],3),r[2],flush=True);return r
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(work,clips))
 print('VOICE_DONE',len(results),round(sum(r[1] for r in results),3),flush=True)
if __name__=='__main__':
 sys.stdout.reconfigure(encoding='utf8');generate(dict(api_key=os.environ.get('DASHSCOPE_API_KEY',''),workspace_id=os.environ.get('SFM_WORKSPACE_ID','')),'--test' in sys.argv)
