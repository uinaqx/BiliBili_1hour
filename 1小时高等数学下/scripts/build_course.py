import pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'content'))
import chapters_a,chapters_b,chapters_c,chapters_d,chapters_e
from author import write
write()
