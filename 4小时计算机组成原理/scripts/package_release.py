"""Package the anonymous completed lecture without dependency/render/private caches."""
import json,pathlib
from safe_delivery import pack
from release_files import ROOT,includes
DEL=ROOT/'out'
def main():
 path=DEL/'计算机组成原理课件精讲_可编辑工程.zip';report=pack(ROOT,includes(),path)
 (DEL/'工程安全检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');assert report['allPassed'];print('RELEASE_PACKAGED',report['filesScanned'],path.stat().st_size,flush=True)
if __name__=='__main__':main()
