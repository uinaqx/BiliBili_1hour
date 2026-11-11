"""Persistent source selections and real instruction states, driven by authored phrases."""
import functools,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
@functools.lru_cache(1)
def traces():return json.loads((ROOT/'build/execution-data.json').read_text(encoding='utf8'))
def resolve_state(s,h):
    states=traces()[s['visual']['trace']]['snapshots']
    if 'stateIndex' in h:assert 0<=h['stateIndex']<len(states);return h['stateIndex']
    if h.get('afterLine') is None:return None
    matches=[x for x in states if x['line']==h['afterLine']];occ=h.get('occurrence',1);assert 1<=occ<=len(matches),(s['key'],h,len(matches));state=matches[occ-1]
    if h.get('completion')=='call-return':
        assert state['instruction'].startswith('call ') and state['writes'];return_ip=state['writes'][-1]['value'];previous_sp=states[state['step']-1]['registers']['sp'];found=[x for x in states[state['step']+1:] if x['instruction'].startswith('ret') and x['registers']['ip']==return_ip and x['registers']['sp']==previous_sp];assert found,(s['key'],h);state=found[0]
    return state['step']
def selection(s,frame):
    begun=[u for u in s['units'] if u['begin']<=frame];u=begun[-1] if begun else s['units'][0];p=s['parts'][u['index']];lines=p['codeLines'];snapshot=u.get('initialState')
    for h in u.get('highlights',[]):
        if h['begin']>frame:break
        lines=h['codeLines']
        if h['stateIndex'] is not None:snapshot=h['stateIndex']
    return lines,snapshot
