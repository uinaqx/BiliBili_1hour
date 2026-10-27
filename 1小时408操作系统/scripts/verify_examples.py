"""Independent expected schedules and counts plus invariants for teaching models."""
import hashlib,json,pathlib
from fractions import Fraction
import examples as e
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
    data=e.all_examples();checks=[]
    def check(name,actual,expected):
        assert actual==expected,(name,actual,expected);checks.append(dict(name=name,actual=str(actual),expected=str(expected),passed=True))
    expected={'fcfs':[('A',0,5),('B',5,8),('C',8,9)],'sjf':[('A',0,5),('C',5,6),('B',6,9)],'srtf':[('A',0,1),('B',1,2),('C',2,3),('B',3,5),('A',5,9)]}
    for name,seq in data['schedules'].items():
        check(name+' timeline',[(x['name'],x['start'],x['end']) for x in seq],expected[name])
        for n,arrival,service in e.JOBS:
            check(name+' '+n+' service conservation',sum(x['end']-x['start'] for x in seq if x['name']==n),service)
            check(name+' '+n+' starts after arrival',all(x['start']>=arrival for x in seq if x['name']==n),True)
    check('FCFS mean turnaround',sum(Fraction(end-arrival) for end,arrival in zip([5,8,9],[0,1,2]))/3,Fraction(19,3))
    check('HRRN B',Fraction(4+3,3),Fraction(7,3));check('HRRN C',Fraction(3+1,1),4)
    check('RR main timeline',[(x['name'],x['start'],x['end']) for x in data['rr']],[('A',0,2),('B',2,4),('C',4,5),('A',5,7),('B',7,8),('A',8,9)])
    check('RR question completion',{n:max(x['end'] for x in data['rrQuestion'] if x['name']==n) for n in ['A','B']},{'A':5,'B':4});check('RR mean turnaround',Fraction(5+4,2),Fraction(9,2))
    for k,want in [('fifo',10),('lru',9),('opt',7)]:
        states=data['replacements'][k];check(k+' faults',states[-1]['faults'],want)
        for i,x in enumerate(states):
            check(f'{k} {i} resident unique',len(set(x['frames'])),len(x['frames']))
            check(f'{k} {i} demand present',x['page'] in x['frames'],True)
            check(f'{k} {i} capacity',len(x['frames'])<=3,True)
            check(f'{k} {i} miss counter',x['faults'],sum(int(y['fault']) for y in states[:i+1]))
    check('FIFO Belady three',data['belady']['3'][-1]['faults'],9);check('FIFO Belady four',data['belady']['4'][-1]['faults'],10)
    check('LRU question faults',data['lruQuestion'][-1]['faults'],5);check('LRU victim at 4',data['lruQuestion'][4]['victim'],2)
    check('banker safe',data['banker']['safe'],True);check('banker sequence',[x['process'] for x in data['banker']['steps']],[1,0,2]);check('banker Work sequence',[x['after'] for x in data['banker']['steps']],[5,6,7]);check('banker unsafe trial',data['unsafeTrial']['safe'],False);check('banker trial Need',data['unsafeTrial']['need'],[2,3,2]);check('banker resources conserved',data['banker']['work'],3+1+2+1)
    for address,page,frame,offset,physical in [(2500,2,5,452,5572),(3500,3,7,428,7596)]:
        check('page quotient '+str(address),address//1024,page);check('page remainder '+str(address),address%1024,offset);check('physical '+str(address),frame*1024+offset,physical)
    check('page bits',2**10,1024);check('16bit pages',2**(16-10),64);check('frames bits',2**5,32)
    check('single-level table bytes',2**20*4,4*1024**2);check('subtable bytes',2**10*4,4096)
    check('TLB expected ns',Fraction(9,10)*110+Fraction(1,10)*210,120)
    check('segment valid address',4000+800,4800);check('segment invalid',1300<1200,False)
    check('fault expected ns',Fraction(999,1000)*100+Fraction(1,1000)*8000000,Fraction(80999,10))
    check('file logical block',10000//4096,2);check('file block offset',10000%4096,1808)
    check('index entries 4K',4096//4,1024);check('index question entries',1024//4,256);check('index question KiB',4+256,260)
    for k,want in [('fcfs',642),('sstf',208),('scan',332),('look',314),('cscan',391),('clook',341)]:
        check('disk '+k+' total',e.distance(data['disks'][k]),want)
        check('disk '+k+' covers requests',set(e.DISK)<=set(data['disks'][k]),True)
    check('SCAN question',e.distance(e.disk_order('scan',50,[20,80])),328);check('LOOK question',e.distance(e.disk_order('look',50,[20,80])),90)
    check('7200RPM revolution ms',Fraction(60000,7200),Fraction(25,3));check('mean rotational ms',Fraction(60000,7200)/2,Fraction(25,6))
    check('bitmap bytes',(1000+7)//8,125);check('bitmap blocks',(125+4095)//4096,1)
    check('single buffer stable interval',max(10,6)+2,12);check('double buffer stable interval',max(10,6+2),10)
    # Concrete read/modify/write interleaving and semaphore deadlock scenario.
    count=0;a=count;b=count;a+=1;b+=1;count=a;count=b;check('lost update race',count,1)
    mutex=1;full=0;mutex-=1;check('consumer holds mutex',mutex,0);check('consumer waits full',full==0,True);check('producer blocked on mutex',mutex==0,True)
    course=ROOT/'public/course.json';r=dict(allPassed=True,checks=len(checks),courseSha256=hashlib.sha256(course.read_bytes()).hexdigest(),scope='deterministic scheduling, replacement, deadlock safety, address, disk and capacity examples; stated teaching models, not production OS measurements',records=checks)
    (ROOT/'build/examples.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8');(ROOT/'build/examples-verification.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print('EXAMPLES_VERIFIED',len(checks),flush=True)
if __name__=='__main__':main()
