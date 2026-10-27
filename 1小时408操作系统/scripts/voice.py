import concurrent.futures,json,os,pathlib,sys
import audio as provider
ROOT=pathlib.Path(__file__).resolve().parents[1];provider.ROOT=ROOT;provider.AUDIO=ROOT/'public/audio_original'
provider.INSTRUCTION='你是一位耐心、讲解清晰的大学老师，正在给初学者讲操作系统。使用沉稳亲切、清楚自然的普通话男声，以正常且前后一致的语速讲解。逗号连贯，句间自然停顿。只朗读正文，不朗读提示词。'
def generate(credentials,test=False):
    credentials={**credentials,'model':provider.MODEL}
    clips=[dict(key='voice-test',narration='欢迎来到一小时学完四零八操作系统。进程获得处理器，从就绪进入运行。等待磁盘数据时，进程可能进入阻塞；设备完成后，先回到就绪，再等待调度。P操作申请许可，V操作释放许可。快表没有命中，不表示页面一定不在内存；还要继续检查页表。我们用时间线、状态图和逐步计算，把这些区别讲清楚。')] if test else [dict(key=s['key']+f'-p{i:02}',narration=p['text']) for c in json.loads((ROOT/'public/course.json').read_text(encoding='utf8'))['chapters'] for s in c['scenes'] for i,p in enumerate(s['parts'])]
    def work(clip):
        r=provider.synth(clip,credentials,1.05);print('VOICE',r[0],round(r[1],3),r[2],flush=True);return r
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(work,clips))
    print('VOICE_DONE',len(results),round(sum(r[1] for r in results),3),flush=True)
if __name__=='__main__' and '--dry-run' in sys.argv:
    course=json.loads((ROOT/'public/course.json').read_text(encoding='utf8'));pages=[s for c in course['chapters'] for s in c['scenes']]
    print('VOICE_DRY_RUN',len(pages),'pages',sum(len(s['parts']) for s in pages),'parts; synthesis rate 1.05; no credentials or network used');raise SystemExit(0)

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf8');generate(dict(api_key=os.environ.get('DASHSCOPE_API_KEY',''),workspace_id=os.environ.get('SFM_WORKSPACE_ID',''),model=provider.MODEL),'--test' in sys.argv)
