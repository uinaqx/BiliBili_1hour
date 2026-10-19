"""Update the existing editable archive with V2 timing, without model weights."""
import pathlib,shutil,zipfile
from package import ROOT,DEL,scan

def main():
    paths=list((ROOT/'scripts').glob('*.py'))
    paths.extend(ROOT/p for p in ['README.md','requirements-subtitles.txt','public/timeline.json','build/subtitle-audit-v2.json'])
    paths.extend((ROOT/'public/audio').glob('*.json'))
    for folder in ['subtitle-ctc','subtitle-ctc-phonetic']:
        paths.extend((ROOT/'build'/folder).glob('*.json'))
    paths.extend(p for p in (ROOT/'build/subtitle-sync-v2').iterdir() if p.suffix in {'.json','.srt','.ass'})
    updates={('计组一小时制作工程/'+p.relative_to(ROOT).as_posix()):p for p in paths}
    for p in paths:scan(p)
    archive=DEL/'计算机组成原理视频工程.zip';staged=DEL/'计算机组成原理视频工程_V2.packaging.zip'
    with zipfile.ZipFile(archive) as old,zipfile.ZipFile(staged,'w',zipfile.ZIP_DEFLATED,compresslevel=5) as new:
        for info in old.infolist():
            if info.filename in updates:continue
            with old.open(info) as src,new.open(info,'w') as dest:shutil.copyfileobj(src,dest,1024*1024)
        for name,p in sorted(updates.items()):new.write(p,name)
    with zipfile.ZipFile(staged) as z:
        assert z.testzip() is None
        assert len(z.namelist())==len(set(z.namelist()))
        assert not any('/subtitle-model/' in n for n in z.namelist())
    staged.replace(archive)
    print('V2_SOURCE_ARCHIVE_READY',len(updates),'updated entries',archive.stat().st_size,flush=True)
if __name__=='__main__':main()
