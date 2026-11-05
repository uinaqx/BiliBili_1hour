"""Stream secret scans and explicit-include ZIP packaging; never echo matching values."""
import argparse,json,os,pathlib,re,sys,tempfile,zipfile
if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')

PATTERNS=[('api-key-like',re.compile(rb'sk-[A-Za-z0-9_.-]{24,}')),('workspace-id-like',re.compile(rb'llm-[A-Za-z0-9]{10,}'))]
SKIP_PARTS={'.git','node_modules','__pycache__','.cache'}

def secrets_from_env(names):return [(name,os.environ[name].encode()) for name in names if os.environ.get(name)]
def safe_name(text,known):
    for _,value in known:
        decoded=value.decode(errors='ignore')
        if decoded:text=text.replace(decoded,'[redacted]')
    for _,pattern in PATTERNS:text=pattern.sub(b'[redacted]',text.encode('utf-8')).decode('utf-8',errors='replace')
    return text
def forbidden_env(name):
    base=pathlib.PurePosixPath(name.replace('\\','/')).name.lower()
    return (base=='.env' or base.startswith('.env.')) and base not in {'.env.example','.env.template'}
def unsafe_zip_name(name):
    p=pathlib.PurePosixPath(name.replace('\\','/'))
    return p.is_absolute() or '..' in p.parts or any(':' in part for part in p.parts)
def stream_issues(stream,name,known):
    found=set();tail=b'';overlap=max([4096]+[len(v)+1 for _,v in known])
    while True:
        chunk=stream.read(1024*1024)
        if not chunk:break
        data=tail+chunk
        for label,pattern in PATTERNS:
            if pattern.search(data):found.add(label)
        for env_name,value in known:
            if value in data:found.add('configured-secret:'+env_name)
        tail=data[-overlap:]
    return [{'file':safe_name(name,known),'reason':reason} for reason in sorted(found)]
def scan(path,known=()):
    path=pathlib.Path(path).resolve();issues=[];count=0
    if not path.exists():raise ValueError('scan target does not exist')
    if path.is_file() and zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            seen=set()
            for info in z.infolist():
                name=info.filename
                if info.is_dir():continue
                count+=1
                if name in seen:issues.append({'file':safe_name(name,known),'reason':'duplicate-archive-entry'})
                seen.add(name)
                if unsafe_zip_name(name):issues.append({'file':safe_name(name,known),'reason':'unsafe-archive-path'})
                if forbidden_env(name):issues.append({'file':safe_name(name,known),'reason':'real-env-file'})
                if info.flag_bits&1:issues.append({'file':safe_name(name,known),'reason':'encrypted-entry-not-inspected'});continue
                with z.open(info) as f:issues.extend(stream_issues(f,name,known))
        # Reading each entire entry verifies its CRC as well.
    else:
        root=path.resolve() if path.is_dir() else path.parent.resolve()
        files=sorted(path.rglob('*')) if path.is_dir() else [path]
        for file in files:
            if file.is_symlink():issues.append({'file':safe_name(str(file),known),'reason':'symlink-not-inspected'});continue
            if not file.is_file() or any(x in SKIP_PARTS for x in file.relative_to(root).parts):continue
            count+=1;name=str(file.relative_to(root))
            if forbidden_env(name):issues.append({'file':safe_name(name,known),'reason':'real-env-file'})
            with file.open('rb') as f:issues.extend(stream_issues(f,name,known))
    return {'allPassed':not issues,'filesScanned':count,'issues':issues,'scope':'patterns plus configured secret environment values; not a universal credential detector'}

def pack(root,includes,output,known=()):
    root=pathlib.Path(root).resolve();output=pathlib.Path(output).resolve();selected=set()
    if not includes:raise ValueError('supply explicit include paths')
    for include in includes:
        path=(root/include).resolve()
        if not path.is_relative_to(root):raise ValueError('include escapes project root')
        if not path.exists():raise ValueError('include does not exist')
        candidates=path.rglob('*') if path.is_dir() else [path]
        for file in candidates:
            if file.is_symlink():raise ValueError('symlink in include; choose explicit real files')
            if not file.is_file():continue
            if not file.resolve().is_relative_to(root):raise ValueError('included file escapes project root')
            rel=file.relative_to(root)
            if any(x in SKIP_PARTS for x in rel.parts) or forbidden_env(str(rel)):continue
            if file.resolve()==output:continue
            selected.add(file)
    if not selected:raise ValueError('no files selected')
    issues=[]
    for file in sorted(selected):
        with file.open('rb') as f:issues.extend(stream_issues(f,str(file.relative_to(root)),known))
    if issues:return {'allPassed':False,'filesScanned':len(selected),'issues':issues}
    if output.exists():raise ValueError('output already exists; use a new version name')
    output.parent.mkdir(parents=True,exist_ok=True)
    fd,staged_name=tempfile.mkstemp(prefix='course-package-',suffix='.zip',dir=output.parent);os.close(fd);staged=pathlib.Path(staged_name)
    try:
        with zipfile.ZipFile(staged,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as z:
            for file in sorted(selected):z.write(file,root.name+'/'+file.relative_to(root).as_posix())
        report=scan(staged,known)
        if not report['allPassed']:return report
        staged.replace(output);report['archive']=str(output);return report
    finally:
        if staged.exists():staged.unlink()

def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='mode',required=True)
    p=sub.add_parser('scan');p.add_argument('path');p.add_argument('--secret-env',nargs='*',default=[]);p.add_argument('--output')
    p=sub.add_parser('pack');p.add_argument('--root',required=True);p.add_argument('--include',nargs='+',required=True);p.add_argument('--output',required=True);p.add_argument('--secret-env',nargs='*',default=[])
    args=parser.parse_args();known=secrets_from_env(args.secret_env)
    report=scan(args.path,known) if args.mode=='scan' else pack(args.root,args.include,args.output,known)
    text=json.dumps(report,ensure_ascii=False,indent=2)
    if args.mode=='scan' and args.output:pathlib.Path(args.output).write_text(text+'\n',encoding='utf-8')
    print(text);return 0 if report['allPassed'] else 1
if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError,zipfile.BadZipFile) as exc:
        # Errors can contain unsafe names; scrub before printing.
        print('DELIVERY_ERROR:',safe_name(str(exc),secrets_from_env(sys.argv[sys.argv.index('--secret-env')+1:] if '--secret-env' in sys.argv else [])),file=sys.stderr);sys.exit(2)
