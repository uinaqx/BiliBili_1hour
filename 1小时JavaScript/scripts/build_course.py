import pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
for directory in ('public', 'build', 'out'): (ROOT / directory).mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'content'))
import chapters_a,chapters_b,chapters_c,chapters_d,chapters_e
from author import write
write()
