"""Scan exactly the staged source bytes, never printing a matched credential."""
import json,pathlib,re,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parent
PATTERNS=[rb'\bsk-[A-Za-z0-9._-]{20,}',rb'\bllm-[A-Za-z0-9]{10,}',rb'\bAKIA[A-Z0-9]{16}\b',rb'\bgh[pousr]_[A-Za-z0-9]{20,}',rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',rb'[A-Za-z]:[\\/]Users[\\/]']
BLOCK={'node_modules','build','out','output','__pycache__','audio','audio_original','stills','.git','alignment','repair_sync','revision_121','subtitle_hold','no_subtitles'}
def staged():
    raw=subprocess.check_output(['git','ls-files','--stage','-z'],cwd=ROOT);entries=[]
    for line in raw.split(b'\0'):
        if not line:continue
        prefix,name=line.split(b'\t',1);mode,sha,stage=prefix.decode().split();assert stage=='0'
        entries.append((name.decode('utf-8'),mode,sha))
    shas=list(dict.fromkeys(e[2] for e in entries));process=subprocess.run(['git','cat-file','--batch'],input=('\n'.join(shas)+'\n').encode(),cwd=ROOT,capture_output=True,check=True)
    data=process.stdout;pos=0;blobs={}
    for sha in shas:
        end=data.index(b'\n',pos);header=data[pos:end].decode().split();assert header[0]==sha and header[1]=='blob'
        size=int(header[2]);pos=end+1;blobs[sha]=data[pos:pos+size];pos+=size+1
    return entries,blobs
def audit():
    entries,blobs=staged();bad=[]
    for name,mode,sha in entries:
        p=pathlib.PurePosixPath(name);data=blobs[sha]
        if mode not in {'100644','100755'} or set(p.parts)&BLOCK or p.suffix.lower() in {'.mp3','.wav','.aac','.mp4','.zip','.exe','.pyc','.log','.pt','.bin','.safetensors'} or p.name.startswith('.env') and p.name!='.env.example':bad.append((name,'private/generated file'));continue
        if any(re.search(pattern,data) for pattern in PATTERNS):bad.append((name,'credential or personal path pattern'));continue
        if p.suffix=='.json':
            try:
                obj=json.loads(data)
                def walk(value):
                    if isinstance(value,dict):
                        for k,v in value.items():
                            if k.lower() in {'api_key','workspace_id','access_token','refresh_token','authorization'} and v and not str(v).startswith(('YOUR_','<')):raise ValueError()
                            walk(v)
                    elif isinstance(value,list):
                        for x in value:walk(x)
                walk(obj)
            except ValueError:bad.append((name,'invalid JSON or account field'))
    if bad:
        for name,reason in bad:print(name+': '+reason)
        raise SystemExit('PUBLICATION_AUDIT_FAILED')
    print('PUBLICATION_AUDIT_PASSED',len(entries),'tracked source/document files; no account credentials, user paths, audio or generated caches')
    return entries,blobs
if __name__=='__main__':audit()
