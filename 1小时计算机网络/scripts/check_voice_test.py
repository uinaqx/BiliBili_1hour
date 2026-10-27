import json,pathlib,torch,whisper
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
    torch.set_num_threads(4);model=whisper.load_model(str(pathlib.Path.home()/'.cache/whisper/base.pt'),device='cpu')
    path=ROOT/'public/audio_original/voice-test.mp3';r=model.transcribe(str(path),language='zh',fp16=False,temperature=0,initial_prompt='计算机网络。TCP，IP地址，子网掩码，路由器。')
    meta=json.loads(path.with_suffix('.json').read_text(encoding='utf8'));assert meta['rate']==1.05 and meta['model']=='qwen-audio-3.1-tts-plus' and meta['voice']=='xunanchuan_v3.1'
    report=dict(model=meta['model'],voice=meta['voice'],synthesisRate=meta['rate'],reference=meta['narration'],transcript=r['text'],scope='local ASR of the internal voice test; homophones and letters may be mistranscribed, not a full-course listening claim')
    (ROOT/'build/voice-test-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
