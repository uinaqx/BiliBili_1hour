"""Offline verified subtitles: final PCM + aligned whole tokens + CFR before ASS."""
from pathlib import Path
from subtitle_workflow import build, burn
ROOT=Path(__file__).resolve().parents[1]
DEL=ROOT/'out'
SOURCE=DEL/'一小时讲完汇编语言_8086基础.mp4'
TARGET=DEL/'一小时讲完汇编语言_8086基础_字幕同步修正版.mp4'
BUILD=ROOT/'build/subtitles-verified'

def main():
    build(ROOT,SOURCE,BUILD)
    burn(BUILD/'subtitle-plan.json',TARGET)
    print('SUBTITLED_VIDEO_DONE',TARGET,flush=True)

if __name__=='__main__':main()
