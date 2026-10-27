import concurrent.futures,json,os,pathlib,sys
import audio as provider
ROOT=pathlib.Path(__file__).resolve().parents[1];provider.ROOT=ROOT;provider.AUDIO=ROOT/'public/audio_original'
def generate(credentials,test=False,workers=2):
    credentials={**credentials,'model':provider.MODEL}
    clips=[dict(key='voice-test',narration='欢迎来到一小时学完计算机网络。浏览器发出请求后，数据要先经过传输层封装成报文段，再由网络层加上IP地址，最后由链路层封装成帧发送出去。路由器逐跳转发，到达目的主机后再一层层解封装。TCP用序号和确认保证可靠，收到三个重复确认就快重传。')] if test else [dict(key=s['key']+f'-p{i:02}',narration=p['text']) for c in json.loads((ROOT/'public/course.json').read_text(encoding='utf8'))['chapters'] for s in c['scenes'] for i,p in enumerate(s['parts'])]
    def work(clip):
        result=provider.synth(clip,credentials,1.05);print('VOICE',result[0],round(result[1],3),result[2],flush=True);return result
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:results=list(pool.map(work,clips))
    print('VOICE_DONE',len(results),round(sum(r[1] for r in results),3),flush=True)
if __name__=='__main__' and '--dry-run' in sys.argv:
    course=json.loads((ROOT/'public/course.json').read_text(encoding='utf8'));pages=[s for c in course['chapters'] for s in c['scenes']]
    print('VOICE_DRY_RUN',len(pages),'pages',sum(len(s['parts']) for s in pages),'parts; synthesis rate 1.05; no credentials or network used');raise SystemExit(0)

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf8');generate(dict(api_key=os.environ.get('DASHSCOPE_API_KEY',''),workspace_id=os.environ.get('SFM_WORKSPACE_ID','')),'--test' in sys.argv)
