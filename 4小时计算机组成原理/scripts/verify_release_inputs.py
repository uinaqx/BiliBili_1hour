"""Bind the completed lecture to its reviewed, anonymous assets and coverage ledger."""
import hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
def load(p):return json.loads(p.read_text(encoding='utf8'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 c=load(ROOT/'public/course.json');p=load(ROOT/'build/visual-privacy-review.json');coverage=load(ROOT/'build/coverage.json')
 assert c['scope']=='complete' and c['subtitles'] is False
 assert p['allPassed'] and p['unresolvedCount']==0 and p['courseSha256']==digest(ROOT/'public/course.json'),'Privacy review does not match current course'
 assert coverage['sourceSlides']==coverage['accountedFor']==920 and not coverage['uncovered']
 ids={s['id'] for ch in c['chapters'] for s in ch['scenes']};assets=c['sourceAssets']
 for key,item in assets.items():
  path=ROOT/'public'/item['file'];assert path.is_relative_to(ROOT/'public') and digest(path)==item['sha256'],key
 for ch in c['chapters']:
  for s in ch['scenes']:
   for b in s['beats']:
    if not b.get('board'):assert b['page'] in assets
 for items in coverage['items'].values():
  for item in items:assert set(item.get('sceneIds',[]))<=ids
 verification=[]
 for name in ['arithmetic-verification.json','data-example-verification.json','hardware-content-checks.json']:
  report=load(ROOT/'build'/name);assert report['allPassed']
  for file,h in report.get('moduleSha256',{}).items():assert digest(ROOT/'content'/file)==h
  verification.append(dict(report=name,checks=report['checks']))
 out=dict(allPassed=True,courseSha256=digest(ROOT/'public/course.json'),sourceSlides=920,chapters=len(c['chapters']),scenes=len(ids),beats=sum(len(s['beats']) for ch in c['chapters'] for s in ch['scenes']),sourceAssetsVerified=len(assets),privacyReviewSha256=digest(ROOT/'build/visual-privacy-review.json'),verification=verification,scope='Exact previously reviewed anonymous image assets, complete coverage ledger and matching numerical checks; final encoded video is checked separately.')
 (ROOT/'build/release-inputs.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print('RELEASE_INPUTS_VERIFIED',len(assets),len(ids),sum(x['checks'] for x in verification),flush=True)
if __name__=='__main__':main()
