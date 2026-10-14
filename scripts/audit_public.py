"""Audit tracked publication files without printing matched secret values."""
import pathlib,re,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
patterns=[rb'sk-[A-Za-z0-9._-]{24,}',rb'llm-[A-Za-z0-9]{10,}',rb'AKIA[A-Z0-9]{16}',rb'gh[pousr]_[A-Za-z0-9]{20,}',rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',rb'[A-Za-z]:[\\/]Users[\\/]']
try:
    tracked=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).split(b'\0')
    files=[ROOT/p.decode('utf-8') for p in tracked if p]
    if not files:raise ValueError('No tracked files')
except (subprocess.CalledProcessError,ValueError):
    files=[]
    for p in ROOT.rglob('*'):
        rel=p.relative_to(ROOT)
        if set(rel.parts)&{'node_modules','build','out','.git','__pycache__','public'}:continue
        if p.is_file():files.append(p)
failed=[]
for p in files:
    rel=p.relative_to(ROOT).as_posix()
    if p.suffix.lower() in {'.mp3','.wav','.aac','.mp4','.zip','.exe','.pyc'} or rel.startswith(('public/audio/','public/audio_original/','public/stills/')) or p.name.startswith('.env') and p.name!='.env.example':
        failed.append(rel);continue
    data=p.read_bytes()
    if any(re.search(pattern,data) for pattern in patterns):failed.append(rel)
if failed:
    print('Publication audit failed for paths:',*failed,sep='\n');sys.exit(1)
print(f'Publication audit passed: {len(files)} source/document files; no credentials, workspace IDs, user paths or media.')
