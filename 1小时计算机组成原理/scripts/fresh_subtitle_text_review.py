"""Independent lexical review helpers for fresh ASR only; never reads old captions."""
from pathlib import Path
import argparse, json, re

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'build/fresh-subtitles-20261019'
ASR = BASE / 'asr'
OUT = BASE / 'text'

def chunks():
    return sorted(ASR.glob('chunk-[0-9][0-9][0-9].json'))

def main():
    p=argparse.ArgumentParser(); p.add_argument('--from-chunk', type=int, default=0)
    p.add_argument('--to-chunk', type=int, default=999); p.add_argument('--words', action='store_true')
    a=p.parse_args(); OUT.mkdir(parents=True,exist_ok=True)
    lines=[]
    for path in chunks():
        n=int(path.stem.split('-')[-1])
        if not a.from_chunk<=n<=a.to_chunk: continue
        data=json.loads(path.read_text(encoding='utf-8'))
        for si,seg in enumerate(data['segments']):
            words=seg.get('words',[])
            line=f"{path.name} s{si} {seg['start']:.2f}-{seg['end']:.2f} "+''.join(w['word'] for w in words if w.get('accepted',True))
            lines.append(line)
            if a.words:
                lines.append(' '.join(f"{wi}:{w['word']}" for wi,w in enumerate(words) if w.get('accepted',True)))
    print('\n'.join(lines))

if __name__=='__main__': main()
