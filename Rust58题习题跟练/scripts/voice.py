"""Bailian narration with account data supplied only in process memory."""
import concurrent.futures,json,os,pathlib,sys
import audio as provider
ROOT=pathlib.Path(__file__).resolve().parents[1];provider.ROOT=ROOT;provider.AUDIO=ROOT/'public/audio_original'
provider.INSTRUCTION='你是一位耐心、擅长循序渐进讲清楚的大学老师，正在带零基础学生做Rust语言习题。使用清晰沉稳、亲切平实的普通话男声，语速自然适中、前后一致。像课堂上解释具体代码那样讲解，不要突然加速，不要夸张拖音。句号有自然停顿，逗号连贯。所有权、借用、泛型、特征、生命周期这些术语清楚读出。英文标识自然读出，不机械逐字符拼读整段代码。'
def generate(credentials,test=False):
    if test:clips=[dict(key='voice-test',narration='同学们好，欢迎来到 Rust 五十八题习题跟练。先读题，再暂停自己动手，最后一起修改并运行验证。所有权决定谁拥有数据，可变借用允许在合适的范围内修改数据。生命周期标注说明引用之间的关系，不会延长对象的寿命。我们每次看清当前高亮的几行，再把它们连成完整程序。')]
    else:clips=[dict(key=s['key']+f'-p{i:02}',narration=p['text']) for c in json.loads((ROOT/'public/course.json').read_text(encoding='utf8'))['chapters'] for s in c['scenes'] for i,p in enumerate(s['parts'])]
    def work(clip):
        r=provider.synth(clip,credentials,1.0);print('VOICE',r[0],round(r[1],3),r[2],flush=True);return r
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(work,clips))
    print('VOICE_DONE',len(results),round(sum(r[1] for r in results),3),flush=True)
if __name__=='__main__' and '--dry-run' in sys.argv:
    c=json.loads((ROOT/'public/course.json').read_text(encoding='utf8'));scenes=[s for c in c['chapters'] for s in c['scenes']];parts=[p for s in scenes for p in s['parts']]
    print('VOICE_DRY_RUN',len(scenes),'pages',len(parts),'parts; rate 1.0; no credentials or network used');raise SystemExit(0)

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf8');generate(dict(api_key=os.environ['DASHSCOPE_API_KEY'],workspace_id=os.environ['SFM_WORKSPACE_ID'],model=provider.MODEL),'--test' in sys.argv)
