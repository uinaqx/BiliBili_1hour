import pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'content'))
for directory in ('public', 'build', 'out'): (ROOT / directory).mkdir(exist_ok=True)
import chapters_a,chapters_b,chapters_c,chapters_d
from author import write,CHAPTERS
from focus import refine
refine(CHAPTERS)
write()
