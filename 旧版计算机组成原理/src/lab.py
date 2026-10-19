"""Small reproducible experiments. Run `python -m src.lab --help`."""
import argparse
import json
from .experiments import CPU,PROGRAM,Cache,add_n,float_record,pipeline,to_signed

def integer(s):return int(s,0)
def integers(s):return [integer(v.strip()) for v in s.split(',')]

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='experiment',required=True)
    a=sub.add_parser('add');a.add_argument('a',type=integer);a.add_argument('b',type=integer);a.add_argument('--bits',type=int,default=8)
    f=sub.add_parser('float');f.add_argument('value',type=float)
    c=sub.add_parser('cache');c.add_argument('--capacity',type=int,default=16);c.add_argument('--block',type=int,default=4);c.add_argument('--ways',type=int,default=1);c.add_argument('--addresses',type=integers,default=[0,16,0,16])
    s=sub.add_parser('sum');s.add_argument('--array',type=integers,default=[3,5,7,9])
    sub.add_parser('pipeline')
    args=p.parse_args()
    if args.experiment=='add':result=add_n(args.a,args.b,args.bits)
    elif args.experiment=='float':result=float_record(args.value)
    elif args.experiment=='cache':
        cache=Cache(args.capacity,args.block,args.ways)
        events=[cache.access(a) for a in args.addresses]
        result=dict(events=events,hits=sum(e['hit'] for e in events),accesses=len(events))
    elif args.experiment=='sum':
        if not 1<=len(args.array)<=32:p.error('array length must be 1…32 for this memory layout')
        cpu=CPU();program=dict(PROGRAM);program[8]=('addi',3,0,len(args.array))
        for i,v in enumerate(args.array):cpu.store(256+4*i,v)
        events=cpu.run(program,36)
        result=dict(input=args.array,result_u32=cpu.load(512),result_signed=to_signed(cpu.load(512),32),retired=len(events),events=events)
    else:result=pipeline([('lw',4,1,0),('add',2,2,4),('addi',1,1,0)])
    print(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))

if __name__=='__main__':main()
