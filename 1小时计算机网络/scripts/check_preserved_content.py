"""Bind this voice replacement to the original authored content and drawing logic."""
import hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    provenance=json.loads((ROOT/'docs/换声版本来源.json').read_text(encoding='utf8'))
    course=json.loads((ROOT/'public/course.json').read_text(encoding='utf8'))
    chapter_hash=hashlib.sha256(json.dumps(course['chapters'],ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    assert chapter_hash==provenance['chapterContentSha256'],'The original lesson or authored visual cues changed'
    expected_files=provenance.get('publicSourceFiles',provenance['preservedFiles'])
    for name,expected in expected_files.items():
        actual=hashlib.sha256((ROOT/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest() if 'publicSourceFiles' in provenance else sha(ROOT/name)
        assert actual==expected,('Original source changed',name)
    assert course['synthesisRate']==1.05 and course['speechTempo']==1.0
    report=dict(allPassed=True,chapterContentSha256=chapter_hash,filesCompared=len(provenance['preservedFiles']),narrationExamplesLayoutAndPersistentHighlightLogicUnchanged=True,courseSha256=sha(ROOT/'public/course.json'))
    (ROOT/'build/preserved-content-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(report,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
