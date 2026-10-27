import concurrent.futures,json,os,pathlib,sys
import audio as provider
ROOT=pathlib.Path(__file__).resolve().parents[1];provider.ROOT=ROOT;provider.AUDIO=ROOT/'public/audio_original'
provider.INSTRUCTION='你是一位耐心、讲解清晰的大学数学老师，正在给初学者讲高等数学下的期末基础题。用沉稳亲切、平实自然的普通话男声，保持正常且前后一致的语速。把偏导数、二重积分、曲面法向、收敛半径和傅里叶级数自然准确读出。数学字母与数字结合上下文朗读，不机械逐字符拼读。不要突然加速，不夸张拖音。逗号连贯，句间自然停顿。'
def generate(credentials,test=False):
    clips=[dict(key='voice-test',narration='欢迎来到一小时学完高等数学下。先看偏导数：对谁求导，其他自变量暂时当常数。计算二重积分时，先画区域，再写上下限；换成极坐标以后，面积元还要乘半径。曲面积分要分清法向，幂级数算完收敛半径以后，两个端点仍要分别检查。我们逐题练步骤，把容易漏掉的条件一起写清楚。')] if test else [dict(key=s['key']+f'-p{i:02}',narration=p['text']) for c in json.loads((ROOT/'public/course.json').read_text(encoding='utf8'))['chapters'] for s in c['scenes'] for i,p in enumerate(s['parts'])]
    def work(clip):
        r=provider.synth(clip,credentials,1.0);print('VOICE',r[0],round(r[1],3),r[2],flush=True);return r
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(work,clips))
    print('VOICE_DONE',len(results),round(sum(r[1] for r in results),3),flush=True)
if __name__=='__main__' and '--dry-run' in sys.argv:
    course=json.loads((ROOT/'public/course.json').read_text(encoding='utf8'));pages=[s for c in course['chapters'] for s in c['scenes']]
    print('VOICE_DRY_RUN',len(pages),'pages',sum(len(s['parts']) for s in pages),'parts; synthesis rate 1.0; no credentials or network used');raise SystemExit(0)

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf8');generate(dict(api_key=os.environ.get('DASHSCOPE_API_KEY',''),workspace_id=os.environ.get('SFM_WORKSPACE_ID',''),model=provider.MODEL),'--test' in sys.argv)
