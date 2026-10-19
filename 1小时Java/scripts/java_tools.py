import os,pathlib,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1]
def command(name):
    found=shutil.which(name)
    if found:return found
    if os.environ.get('JAVA_HOME'):
        p=pathlib.Path(os.environ['JAVA_HOME'])/'bin'/(name+'.exe' if os.name=='nt' else name)
        if p.exists():return str(p)
    for p in (ROOT/'build/toolchain').glob('*/bin/'+name+'.exe'):
        return str(p)
    raise RuntimeError('Install JDK 21 or set JAVA_HOME; missing '+name)
