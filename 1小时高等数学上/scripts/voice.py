import concurrent.futures,json,os,pathlib,sys
import audio as provider
ROOT=pathlib.Path(__file__).resolve().parents[1];provider.ROOT=ROOT;provider.AUDIO=ROOT/'public/audio_original'
provider.INSTRUCTION='你是一位耐心、讲解清楚的大学数学老师，正在给零基础大学生讲高等数学上册的期末考试题型。使用清晰沉稳、亲切平实的普通话男声，自然适中且前后一致的语速。先讲题型和条件，再按步骤讲计算与答案，不讲证明。数学术语、正负号、分数、上下限和变量读准确。不要突然加速，不要夸张拖音，逗号连贯，句间自然停顿。'
def generate(credentials,test=False):
    clips=[dict(key='voice-test',narration='欢迎来到一小时学完高等数学上。我们先看题型，再按步骤计算。x趋于零时，正弦x与x等价，一减余弦x与二分之x的平方等价。洛必达先检查零比零或无穷比无穷。积分换元以后，微分和上下限要一起换。二阶方程先解特征根，再按三种情形写通解。') ] if test else [dict(key=s['key']+f'-p{i:02}',narration=p['text']) for c in json.loads((ROOT/'public/course.json').read_text(encoding='utf8'))['chapters'] for s in c['scenes'] for i,p in enumerate(s['parts'])]
    def work(clip):
        r=provider.synth(clip,credentials,1.0);print('VOICE',r[0],round(r[1],3),r[2],flush=True);return r
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(work,clips))
    print('VOICE_DONE',len(results),round(sum(r[1] for r in results),3),flush=True)
if __name__=='__main__' and '--dry-run' in sys.argv:
    c=json.loads((ROOT/'public/course.json').read_text(encoding='utf8'));scenes=[s for c in c['chapters'] for s in c['scenes']];parts=[p for s in scenes for p in s['parts']]
    print('VOICE_DRY_RUN',len(scenes),'pages',len(parts),'parts; rate 1.0; no credentials or network used');raise SystemExit(0)

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf8');generate(dict(api_key=os.environ['DASHSCOPE_API_KEY'],workspace_id=os.environ['SFM_WORKSPACE_ID'],model=provider.MODEL),'--test' in sys.argv)
