import sys,pathlib,importlib
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'content'))
for directory in ('public', 'build', 'out'): (ROOT / directory).mkdir(exist_ok=True)
for name in ['chapters_a','chapters_b','chapters_c','chapters_d']:
 if (ROOT/'content'/(name+'.py')).exists():importlib.import_module(name)
from author import write
write()
