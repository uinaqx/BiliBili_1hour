"""Approximate local ASR samples from final AAC, independent of the known script."""
import hashlib,json,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]
from render_spoken import FINAL
def main():
 import torch,whisper
 torch.set_num_threads(4);model=whisper.load_model(str(pathlib.Path.home()/'.cache/whisper/base.pt'),device='cpu');t=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf8'));out=ROOT/'build/final-review';records=[]
 for key,part in [('ma-02-01',1),('ma-07-05',1),('ma-10-03',1)]:
  s=next(s for s in t['scenes'] if s['key']==key);start=(s['startFrame']+s['parts'][part]['begin'])/30;path=out/(key+'-asr.wav')
  subprocess.run(['ffmpeg','-y','-v','error','-ss',str(start),'-i',str(FINAL),'-vn','-t','15','-ar','16000','-ac','1',str(path)],check=True)
  r=model.transcribe(str(path),language='zh',task='transcribe',fp16=False,temperature=0,condition_on_previous_text=False,initial_prompt='现代汇编，x86-64，AArch64，寄存器，调用，返回，位宽，数组，指针。')
  item=dict(scene=key,start=start,seconds=15,reference=s['parts'][part]['text'],transcript=r['text']);records.append(item);print(json.dumps(item,ensure_ascii=False),flush=True)
 (ROOT/'build/speech-spotcheck.json').write_text(json.dumps(dict(scope='45 seconds sampled from final AAC; approximate local ASR, not a full-course listening claim',videoSha256=hashlib.sha256(FINAL.read_bytes()).hexdigest(),samples=records),ensure_ascii=False,indent=2),encoding='utf8')
if __name__=='__main__':main()
