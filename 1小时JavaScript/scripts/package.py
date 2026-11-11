import json,pathlib,shutil,zipfile
from safe_delivery import pack
ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out'
def main():
    report=json.loads((ROOT/'build/final-verification.json').read_text(encoding='utf8'));assert report['allPassed']
    includes=['README.md','.gitignore','.env.example','requirements.txt','content','scripts','docs','examples','public/course.json','public/timeline.json','public/audio_original','public/audio','build/alignment','build/final-verification.json','build/example-verification.json','build/audio-preparation.json']
    result=pack(ROOT,includes,DEL/'JavaScript一小时_可编辑工程.zip')
    (DEL/'工程安全检查.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');assert result['allPassed']
    with zipfile.ZipFile(DEL/'JavaScript配套示例.zip','w',zipfile.ZIP_DEFLATED) as z:
        for f in sorted((ROOT/'examples').rglob('*')):
            if f.is_file():z.write(f,f.relative_to(ROOT/'examples'))
    print('DELIVERY_PACKAGED',result['filesScanned'],flush=True)
if __name__=='__main__':main()
