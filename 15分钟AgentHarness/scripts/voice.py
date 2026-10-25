import concurrent.futures,json,os,pathlib,sys
import audio as provider
ROOT=pathlib.Path(__file__).resolve().parents[1];provider.ROOT=ROOT;provider.AUDIO=ROOT/'public/audio_original'
provider.INSTRUCTION='你是一位擅长讲清底层机制的大学老师，正在讲智能体运行时Agent Harness。使用清晰沉稳、亲切平实的普通话男声，自然适中、前后一致的语速。把模型、工具调用、上下文、权限、检查点和幂等讲清楚。英文术语自然读出，不机械逐字符拼读。不要突然加速，不夸张拖音。逗号连贯，句间自然停顿。'
def generate(credentials,test=False):
    clips=[dict(key='voice-test',narration='欢迎来到十五分钟讲清 Agent Harness 底层原理。模型提出下一步，运行时负责组装上下文、检查权限、执行工具，再把结果送回循环。超时不一定表示操作没有发生，断点恢复也不自动保证副作用只执行一次。我们用动态图和可重复的本地案例，把这些机制逐层拆开。')] if test else [dict(key=s['key']+f'-p{i:02}',narration=p['text']) for c in json.loads((ROOT/'public/course.json').read_text(encoding='utf8'))['chapters'] for s in c['scenes'] for i,p in enumerate(s['parts'])]
    def work(clip):
        r=provider.synth(clip,credentials,1.0);print('VOICE',r[0],round(r[1],3),r[2],flush=True);return r
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(work,clips))
    print('VOICE_DONE',len(results),round(sum(r[1] for r in results),3),flush=True)
if __name__=='__main__' and '--dry-run' in sys.argv:
    c=json.loads((ROOT/'public/course.json').read_text(encoding='utf8'));scenes=[s for c in c['chapters'] for s in c['scenes']];parts=[p for s in scenes for p in s['parts']]
    print('VOICE_DRY_RUN',len(scenes),'pages',len(parts),'parts; rate 1.0; no credentials or network used');raise SystemExit(0)

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf8');generate(dict(api_key=os.environ['DASHSCOPE_API_KEY'],workspace_id=os.environ['SFM_WORKSPACE_ID'],model=provider.MODEL),'--test' in sys.argv)
