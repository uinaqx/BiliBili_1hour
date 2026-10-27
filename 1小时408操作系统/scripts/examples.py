"""Deterministic teaching models, not traces of a particular production OS."""
import collections
JOBS=[('A',0,5),('B',1,3),('C',2,1)]
REFS=[7,0,1,2,0,3,0,4,2,3,0,3,2]
BELADY=[1,2,3,4,1,2,5,1,2,3,4,5]
DISK=[82,170,43,140,24,16,190]
def schedule(jobs,kind='fcfs',quantum=2):
    jobs=[dict(name=n,arrival=a,service=b,remaining=b) for n,a,b in jobs];t=0;out=[];queue=collections.deque();pending=sorted(jobs,key=lambda j:j['arrival'])
    if kind=='rr':
        while pending or queue:
            while pending and pending[0]['arrival']<=t:queue.append(pending.pop(0))
            if not queue:t=pending[0]['arrival'];continue
            j=queue.popleft();dt=min(quantum,j['remaining']);out.append(dict(name=j['name'],start=t,end=t+dt));j['remaining']-=dt;t+=dt
            while pending and pending[0]['arrival']<=t:queue.append(pending.pop(0))
            if j['remaining']:queue.append(j)
    else:
        while any(j['remaining'] for j in jobs):
            ready=[j for j in jobs if j['arrival']<=t and j['remaining']]
            if not ready:t=min(j['arrival'] for j in jobs if j['remaining']);continue
            key=(lambda j:(j['arrival'],j['name'])) if kind=='fcfs' else (lambda j:(j['remaining'],j['arrival'],j['name']))
            j=min(ready,key=key);dt=1 if kind=='srtf' else j['remaining']
            if out and kind=='srtf' and out[-1]['name']==j['name']:out[-1]['end']+=dt
            else:out.append(dict(name=j['name'],start=t,end=t+dt))
            j['remaining']-=dt;t+=dt
    return out
def replacement(refs,capacity,kind):
    frames=[];queue=[];recent={};states=[];faults=0
    for at,page in enumerate(refs):
        fault=page not in frames;victim=None
        if fault:
            faults+=1
            if len(frames)<capacity:frames.append(page)
            else:
                if kind=='fifo':victim=queue.pop(0)
                elif kind=='lru':victim=min(frames,key=lambda p:recent[p])
                else:
                    def next_use(p):
                        try:return refs.index(p,at+1)
                        except ValueError:return float('inf')
                    victim=max(frames,key=next_use)
                frames[frames.index(victim)]=page
            if kind=='fifo':queue.append(page)
        recent[page]=at
        states.append(dict(index=at,page=page,frames=frames.copy(),fault=fault,faults=faults,victim=victim))
    return states
def safe_sequence(available,allocation,maximum):
    need=[m-a for m,a in zip(maximum,allocation)];work=available;done=set();records=[]
    while len(done)<len(need):
        candidates=[i for i,n in enumerate(need) if i not in done and n<=work]
        if not candidates:break
        i=candidates[0];before=work;work+=allocation[i];done.add(i);records.append(dict(process=i,need=need[i],before=before,release=allocation[i],after=work))
    return dict(safe=len(done)==len(need),need=need,steps=records,work=work)
def disk_order(kind,head=50,requests=DISK,maximum=199):
    todo=list(requests);path=[head]
    if kind=='fcfs':path+=todo
    elif kind=='sstf':
        while todo:
            p=min(todo,key=lambda r:(abs(r-path[-1]),r));path.append(p);todo.remove(p)
    else:
        high=sorted(r for r in todo if r>=head);low=sorted(r for r in todo if r<head)
        if kind=='scan':path+=high+[maximum]+list(reversed(low))
        elif kind=='look':path+=high+list(reversed(low))
        elif kind=='cscan':path+=high+[maximum,0]+low
        elif kind=='clook':path+=high+low
        else:raise ValueError(kind)
    return path
def distance(path):return sum(abs(b-a) for a,b in zip(path,path[1:]))
def all_examples():
    return dict(schedules={k:schedule(JOBS,k) for k in ['fcfs','sjf','srtf']},rr=schedule([('A',0,5),('B',0,3),('C',0,1)],'rr'),rrQuestion=schedule([('A',0,3),('B',0,2)],'rr',1),replacements={k:replacement(REFS,3,k) for k in ['fifo','lru','opt']},belady={str(n):replacement(BELADY,n,'fifo') for n in [3,4]},lruQuestion=replacement([1,2,3,1,4,2],3,'lru'),banker=safe_sequence(3,[1,2,1],[6,5,3]),unsafeTrial=safe_sequence(0,[4,2,1],[6,5,3]),disks={k:disk_order(k) for k in ['fcfs','sstf','scan','look','cscan','clook']})
