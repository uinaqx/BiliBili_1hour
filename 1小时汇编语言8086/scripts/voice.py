import concurrent.futures,json,os,pathlib,sys
import audio as provider
ROOT=pathlib.Path(__file__).resolve().parents[1];provider.ROOT=ROOT;provider.AUDIO=ROOT/'public/audio_original'
def generate(credentials,test=False):
 credentials={**credentials,'model':provider.MODEL}
 clips=[dict(key='voice-test',narration='欢迎来到一小时讲完汇编语言。这节课使用八零八六的基础指令。我们先看寄存器和内存，再逐条执行传送、加法和条件跳转。A X是一个十六位寄存器，高八位与低八位共用这一份存储。读代码时，先找数据在哪里，再看执行以后哪个位置改变。遇到调用和返回，还要一起检查栈顶指针。')] if test else [dict(key=s['key']+f'-p{i:02}',narration=p['text']) for c in json.loads((ROOT/'public/course.json').read_text(encoding='utf8'))['chapters'] for s in c['scenes'] for i,p in enumerate(s['parts'])]
 def work(clip):
  r=provider.synth(clip,credentials,1.05);print('VOICE',r[0],round(r[1],3),r[2],flush=True);return r
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(work,clips))
 print('VOICE_DONE',len(results),round(sum(r[1] for r in results),3),flush=True)
if __name__=='__main__':
 sys.stdout.reconfigure(encoding='utf8');generate(dict(api_key=os.environ.get('DASHSCOPE_API_KEY',''),workspace_id=os.environ.get('SFM_WORKSPACE_ID','')),'--test' in sys.argv)
