"""Local ASR spot check on actual delivered AAC; not a full-course listening claim."""
import json,pathlib,subprocess,sys
import torch,whisper
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
    torch.set_num_threads(4);model=whisper.load_model(str(pathlib.Path.home()/'.cache/whisper/base.pt'),device='cpu')
    t=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf8'));by={s['key']:s for s in t['scenes']};video=ROOT/'out/一小时学习Kotlin_零基础.mp4';out=ROOT/'build/speech-qa';out.mkdir(parents=True,exist_ok=True);records=[]
    for key,part in [('kt-01-01',0),('kt-06-04',1),('kt-10-08',0)]:
        s=by[key];meta=json.loads((ROOT/'public'/s['audio'].replace('.wav','.json')).read_text(encoding='utf8'));start=(s['startFrame']+s['leadFrames'])/30+meta['parts'][part]['start'];path=out/(key+'.wav')
        subprocess.run(['ffmpeg','-y','-v','error','-ss',f'{start:.9f}','-i',str(video),'-t','18','-vn','-ar','16000','-ac','1',str(path)],check=True)
        result=model.transcribe(str(path),language='zh',task='transcribe',fp16=False,temperature=0,condition_on_previous_text=False,initial_prompt='Kotlin 编程基础。')
        record=dict(key=key,start=start,seconds=18,transcript=result['text']);records.append(record);print(json.dumps(record,ensure_ascii=False),flush=True)
    (ROOT/'build/speech-spotcheck.json').write_text(json.dumps(dict(scope='54 seconds sampled from beginning, middle and end of actual AAC',samples=records),ensure_ascii=False,indent=2),encoding='utf8')
if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf8');main()
