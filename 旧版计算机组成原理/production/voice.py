"""Credentials are accepted only in memory and never written to the project."""
import argparse,concurrent.futures,json,os,pathlib,sys
import tts_base
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parents[1]
tts_base.ROOT=ROOT
tts_base.AUDIO=ROOT/'production/audio_original'
def main():
    p=argparse.ArgumentParser();p.add_argument('--scenes');p.add_argument('--workers',type=int,default=3);p.add_argument('--dry-run',action='store_true');p.add_argument('--from-env',action='store_true');args=p.parse_args()
    plan=json.loads((ROOT/'production/plan.json').read_text(encoding='utf-8'))
    clips=plan['clips']
    if args.scenes:
        selected=set(args.scenes.split(','));clips=[c for c in clips if c['scene'] in selected]
    if args.dry_run:print(f'{len(clips)} clips, {sum(len(c["narration"]) for c in clips)} characters; no requests');return
    credentials=dict(api_key=os.environ['DASHSCOPE_API_KEY'],workspace_id=os.environ['SFM_WORKSPACE_ID'],model=tts_base.MODEL) if args.from_env else json.loads(sys.stdin.readline())
    def work(c):
        result=tts_base.synth(c,credentials,.88)
        print(f'{result[0]}: {result[1]:.3f}s ({result[2]})',flush=True)
        return result
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        results=list(pool.map(work,clips))
    print(f'VOICE_BATCH_DONE {len(results)} clips / {sum(r[1] for r in results):.3f}s',flush=True)
if __name__=='__main__':main()
