"""Narration units follow manually authored teaching targets; no account data is saved."""
import concurrent.futures,json,os,pathlib,sys
import audio as provider
ROOT=pathlib.Path(__file__).resolve().parents[1]
provider.ROOT=ROOT;provider.AUDIO=ROOT/'public/audio_original'
provider.INSTRUCTION='你是一位擅长循序渐进讲解的大学老师，正在为完全没有接触编程的学生讲Kotlin。使用清晰沉稳、亲切平实的普通话男声，自然适中且前后一致的语速。先讲具体例子，再解释原因。不要忽然加速，不要夸张拖音。逗号连贯，句间自然停顿。英文术语自然读出，不机械逐字符朗读代码。'
def generate(credentials,test=False,workers=3):
    clips=[dict(key='voice-test',narration='同学们好，欢迎来到一小时学习 Kotlin。这节课，我们从一个学生成绩的小需求开始。先让程序显示一句话，再保存分数、判断是否及格，最后把这些步骤连起来。Kotlin 的变量有 val 和 var 两种常见写法。先看它们各自能做什么，再记住名称。')] if test else [dict(key=s['key']+f'-p{i:02}',narration=p['text']) for c in json.loads((ROOT/'public/course.json').read_text(encoding='utf8'))['chapters'] for s in c['scenes'] for i,p in enumerate(s['parts'])]
    def work(clip):
        r=provider.synth(clip,credentials,1.0);print('VOICE',r[0],round(r[1],3),r[2],flush=True);return r
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:results=list(pool.map(work,clips))
    print('VOICE_DONE',len(results),round(sum(r[1] for r in results),3),flush=True)
if __name__=='__main__':
    import argparse
    sys.stdout.reconfigure(encoding='utf8')
    parser=argparse.ArgumentParser();parser.add_argument('--test',action='store_true');parser.add_argument('--dry-run',action='store_true');parser.add_argument('--workers',type=int,default=3);args=parser.parse_args()
    assert 1<=args.workers<=6
    if args.dry_run:
        course=json.loads((ROOT/'public/course.json').read_text(encoding='utf8'));pages=[s for c in course['chapters'] for s in c['scenes']]
        print('VOICE_DRY_RUN',len(pages),'pages',sum(len(s['parts']) for s in pages),'narration units; no account read and no request sent')
    else:
        if not os.environ.get('DASHSCOPE_API_KEY') or not os.environ.get('SFM_WORKSPACE_ID'):raise SystemExit('Set your own DASHSCOPE_API_KEY and SFM_WORKSPACE_ID in the process environment')
        generate(dict(api_key=os.environ['DASHSCOPE_API_KEY'],workspace_id=os.environ['SFM_WORKSPACE_ID'],model=provider.MODEL),args.test,args.workers)
