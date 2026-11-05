import concurrent.futures,json,os,pathlib,sys
import audio as provider
ROOT=pathlib.Path(__file__).resolve().parents[1]
provider.ROOT=ROOT;provider.AUDIO=ROOT/'public/audio_original'
INTRO='这套课程从计算机怎样执行一段程序开始，逐步讲到数据表示、算术运算、总线、存储器、输入输出、指令系统、处理器和控制单元。我们会沿着课件里的图、公式和题目逐步分析。遇到计算题，先整理条件，再选择公式，最后核对数值和单位。涉及二进制、补码、浮点数和流水线时，会把中间步骤写在画面上。你可以按章节学习，也可以通过知识点目录直接找到对应的题目。'
def generate(credentials,test=False):
 credentials={**credentials,'model':provider.MODEL};clips=[]
 if test:clips=[dict(key='m01-001-p00',narration=INTRO)]
 else:
  for f in sorted((ROOT/'content').glob('module_*.json')):
   m=json.loads(f.read_text(encoding='utf8'))
   chosen=os.environ.get('COURSE_VOICE_MODULES','')
   if chosen and m['key'] not in chosen.split(','):continue
   for s in m['scenes']:
    clips.extend(dict(key=s['id']+f'-p{i:02}',narration=b['text']) for i,b in enumerate(s['beats']))
 def work(clip):
  r=provider.synth(clip,credentials,1.05);print('VOICE',r[0],round(r[1],3),r[2],flush=True);return r
 with concurrent.futures.ThreadPoolExecutor(max_workers=int(os.environ.get('COURSE_VOICE_WORKERS','2'))) as pool:results=list(pool.map(work,clips))
 print('VOICE_DONE',len(results),round(sum(x[1] for x in results),3),flush=True)
if __name__=='__main__':generate(dict(api_key=os.environ.get('DASHSCOPE_API_KEY',''),workspace_id=os.environ.get('SFM_WORKSPACE_ID','')),'--test' in sys.argv)
