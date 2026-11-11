import pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'content'))
for directory in ('public', 'build', 'out'): (ROOT / directory).mkdir(exist_ok=True)
import chapters_a
try:import chapters_b,chapters_c,chapters_d,chapters_e
except ModuleNotFoundError as e:
    if '--draft' not in sys.argv:raise
from author import write
write()
