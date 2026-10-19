"""Bailian narration; credentials are received through stdin or process environment only."""
import argparse,concurrent.futures,json,os,pathlib,sys
import audio as provider
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parents[1]
provider.ROOT=ROOT;provider.AUDIO=ROOT/'public/audio_original'
provider.INSTRUCTION='你是一位擅长循序渐进讲解的大学老师，正在为从未接触编程的零基础学生讲Java语言。使用清晰沉稳、亲切平实的普通话男声，保持自然一致的语速。先说具体例子，再解释原因；不要突然加速，不要为了强调而拖长语句。句间自然停顿，逗号处保持连贯。自然读英文术语，不要机械地逐字符念程序。'
def main():
    p=argparse.ArgumentParser();p.add_argument('--test',action='store_true');p.add_argument('--workers',type=int,default=3);p.add_argument('--from-env',action='store_true');p.add_argument('--limit',type=int);p.add_argument('--start',type=int,default=0);p.add_argument('--dry-run',action='store_true');args=p.parse_args()
    if args.dry_run:
        data=json.loads((ROOT/'public/course.json').read_text(encoding='utf-8'));clips=[s for c in data['chapters'] for s in c['scenes']];print('DRY_RUN',len(clips),'scenes;',sum(len(s['narration']) for s in clips),'characters; no credentials or network used');return
    if args.from_env:credentials=dict(api_key=os.environ['DASHSCOPE_API_KEY'],workspace_id=os.environ['SFM_WORKSPACE_ID'],model=provider.MODEL)
    else:
        print('READY_FOR_CREDENTIALS',flush=True);credentials=json.loads(sys.stdin.readline())
    clips=[dict(key='voice-test',narration='同学们好，这一小时，我们从第一行Java程序开始。先让屏幕显示一句话，再用变量保存成绩，用条件作判断，用循环重复步骤。每次只认识一个新写法，先看结果，再解释原因。类和对象会在这些基础之后慢慢介绍。')] if args.test else [s for c in json.loads((ROOT/'public/course.json').read_text(encoding='utf-8'))['chapters'] for s in c['scenes']]
    clips=clips[args.start:]
    if args.limit:clips=clips[:args.limit]
    def work(s):
        result=provider.synth(s,credentials,1.0);print(f'VOICE {s["key"]} {result[1]:.3f}s {result[2]}',flush=True);return result
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:results=list(pool.map(work,clips))
    print('VOICE_DONE',len(results),round(sum(r[1] for r in results),3),flush=True)
if __name__=='__main__':main()
