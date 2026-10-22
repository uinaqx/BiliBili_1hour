"""Resolve an installed toolchain; local cache fallback never enters the source package."""
import hashlib,json,os,pathlib,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1]
def java():
    if shutil.which('java'):return shutil.which('java')
    if os.environ.get('JAVA_HOME'):
        p=pathlib.Path(os.environ['JAVA_HOME'])/'bin/java.exe'
        if p.exists():return str(p)
    for root in [ROOT/'build/toolchain',ROOT/'build/toolchain']:
        for p in root.glob('*/bin/java.exe'):return str(p)
    raise RuntimeError('Install JDK 21 and set JAVA_HOME')
def libraries():
    home=pathlib.Path(os.environ.get('KOTLIN_HOME',str(ROOT/'build/toolchain/kotlinc')))
    jars=list((home/'lib').glob('*.jar'))
    if not jars:
        cache=pathlib.Path.home()/'.gradle/caches/modules-2/files-2.1'
        specs=[('org.jetbrains.kotlin','kotlin-compiler-embeddable','2.0.21'),('org.jetbrains.kotlin','kotlin-stdlib','2.0.21'),('org.jetbrains.kotlin','kotlin-script-runtime','2.0.21'),('org.jetbrains.kotlin','kotlin-reflect','1.6.10'),('org.jetbrains.intellij.deps','trove4j',None),('org.jetbrains.kotlinx','kotlinx-coroutines-core-jvm',None),('org.jetbrains','annotations',None)]
        for group,name,version in specs:
            base=cache/group/name
            versions=[base/version] if version else sorted(base.glob('*'),reverse=True)
            found=[]
            for v in versions:
                found=[p for p in v.glob('*/*.jar') if not any(t in p.name for t in ['sources','javadoc'])]
                if found:break
            if found:jars.append(found[0])
        out=ROOT/'build/toolchain';out.mkdir(parents=True,exist_ok=True)
        (out/'provenance.json').write_text(json.dumps([dict(name=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in jars],indent=2),encoding='utf8')
    if not any('compiler' in p.name for p in jars):raise RuntimeError('Install Kotlin 2.0.21 and set KOTLIN_HOME')
    return jars
def commands():
    jars=libraries();cp=os.pathsep.join(map(str,jars));runtime=os.pathsep.join(str(p) for p in jars if 'stdlib' in p.name or p.name.startswith('annotations-'))
    return [java(),'-cp',cp,'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler'],runtime
