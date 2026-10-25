import pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];[(ROOT/d).mkdir(parents=True,exist_ok=True) for d in ['public','build','out','docs']];sys.path.insert(0,str(ROOT/'content'))
import course
from author import write
write()
