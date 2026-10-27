"""Audit native voice settings, full stops and authored anchors against new acoustic timing."""
import argparse,hashlib,json,pathlib
from timeline import anchor_seconds,spoken_phrase
ROOT=pathlib.Path(__file__).resolve().parents[1]
def load(p):return json.loads(p.read_text(encoding='utf8'))
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--available',action='store_true');args=parser.parse_args()
    course=load(ROOT/'public/course.json');records=[];anchors=[]
    def phrase_start(data,phrase):
        chars=[];times=[]
        for word in data['words']:
            for char in word['text']:
                if not char.isspace():chars.append(char.lower());times.append(word['begin_time']/1000)
        index=''.join(chars).find(''.join(phrase.split()).lower())
        assert index>=0,('Missing authored phrase in native or aligned words',phrase)
        return times[index]
    for c in course['chapters']:
        for s in c['scenes']:
            page=ROOT/'public/audio'/(s['key']+'.json')
            if not page.exists() and args.available:continue
            meta=load(page)
            for i,p in enumerate(s['parts']):
                key=s['key']+f'-p{i:02}';native=load(ROOT/'public/audio_original'/(key+'.json'));aligned=load(ROOT/'build/alignment'/(key+'.json'))
                assert native['model']=='qwen-audio-3.1-tts-plus' and native['voice']=='xunanchuan_v3.1' and native['rate']==1.05
                assert native['narration']==aligned['narration']==p['text']
                pauses=[r for r in meta['pauseRefinements'] if r['part']==i]
                assert len(pauses)==p['text'].count('。')-int(p['text'].endswith('。'))
                ordered=[w['begin_time'] for w in aligned['words'] if any(x.isalnum() for x in w['text'])]
                assert all(a<=b+40 for a,b in zip(ordered,ordered[1:])),('Acoustic alignment is not ordered',key)
                records.append(dict(key=key,seconds=native['duration'],internalFullStops=len(pauses),largestPauseRefinement=max([abs(r['alignedSeconds']-r['acousticSeconds']) for r in pauses] or [0]),overlapAgreementP95=aligned['overlapAgreementP95']))
                for move in p['moves']:
                    seconds=anchor_seconds(s,i,move['anchor'],meta)
                    assert meta['parts'][i]['start']<=seconds<meta['parts'][i]['end']
                    spoken=spoken_phrase(s,i,move['anchor'])
                    provider=phrase_start(native,spoken);dtw=phrase_start(aligned,spoken)
                    anchors.append(dict(key=key,phrase=move['anchor'],spokenPhrase=spoken,pageAudioSeconds=seconds,nativeSeconds=provider,acousticSeconds=dtw,providerVsAcousticDifference=dtw-provider))
    report=dict(allPassed=True,scope='available-pages' if args.available else 'complete-course',clips=len(records),authoredAnchors=len(anchors),courseSha256=hashlib.sha256((ROOT/'public/course.json').read_bytes()).hexdigest(),records=records,anchors=anchors)
    report['maxAnchorProviderVsAcousticDifference']=max([abs(a['providerVsAcousticDifference']) for a in anchors] or [0])
    report['anchorComparisonScope']='Native provider and independent acoustic timing agreement; not a claim of independent phoneme-level ground truth.'
    (ROOT/'build/alignment-quality.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in report.items() if k not in ['records','anchors']},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
