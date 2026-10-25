"""Narration units follow manually authored teaching targets; no account data is saved."""
import concurrent.futures,json,os,pathlib,sys
import audio as provider
ROOT=pathlib.Path(__file__).resolve().parents[1]
provider.ROOT=ROOT;provider.AUDIO=ROOT/'public/audio_original'
provider.INSTRUCTION='你是一位擅长循序渐进讲解的大学老师，正在为没有学过线性代数的大学生讲数学。使用清晰沉稳、亲切平实的普通话男声，自然适中且前后一致的语速。先讲具体例子，再解释原因。不要忽然加速，不要夸张拖音。逗号连贯，句间自然停顿。数学术语和数字清楚准确，不机械逐字拼读公式。'
def generate(credentials,test=False):
    clips=[dict(key='voice-test',narration='同学们好，欢迎来到一小时学习线性代数。两支不共线的向量，可以组合出平面上任意一点。矩阵让整个网格一起变化，行列式的绝对值告诉我们面积放大多少倍。如果一个非零向量变换后，只是原来的三倍，那么三就是对应的特征值。先看清图形变化，再理解公式。')] if test else [dict(key=s['key']+f'-p{i:02}',narration=p['text']) for c in json.loads((ROOT/'public/course.json').read_text(encoding='utf8'))['chapters'] for s in c['scenes'] for i,p in enumerate(s['parts'])]
    def work(clip):
        r=provider.synth(clip,credentials,1.0);print('VOICE',r[0],round(r[1],3),r[2],flush=True);return r
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(work,clips))
    print('VOICE_DONE',len(results),round(sum(r[1] for r in results),3),flush=True)
if __name__=='__main__' and '--dry-run' in sys.argv:
    c=json.loads((ROOT/'public/course.json').read_text(encoding='utf8'));scenes=[s for c in c['chapters'] for s in c['scenes']];parts=[p for s in scenes for p in s['parts']]
    print('VOICE_DRY_RUN',len(scenes),'pages',len(parts),'parts; rate 1.0; no credentials or network used');raise SystemExit(0)

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf8')
    generate(dict(api_key=os.environ['DASHSCOPE_API_KEY'],workspace_id=os.environ['SFM_WORKSPACE_ID'],model=provider.MODEL),'--test' in sys.argv)
