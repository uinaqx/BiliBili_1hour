"""Public source-only allowlist; narration and private originals remain local."""
import pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
def includes():
 return ['README.md','LICENSE','.gitignore','.env.example','requirements.txt','requirements.lock.txt','content','docs','scripts','review','public/course.json','public/timeline.json','public/slides']
def files(allow_missing=False):
 return sorted(f for name in includes() for f in ((ROOT/name).rglob('*') if (ROOT/name).is_dir() else [ROOT/name]) if f.is_file() and '__pycache__' not in f.parts)
