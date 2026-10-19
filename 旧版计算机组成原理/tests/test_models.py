import json
from pathlib import Path
import random
import unittest
from src.experiments import *

ROOT=Path(__file__).resolve().parents[1]

class RepresentationTests(unittest.TestCase):
    def test_all_8bit_additions(self):
        for a in range(256):
            for b in range(256):
                got=add_n(a,b)
                sa=a if a<128 else a-256; sb=b if b<128 else b-256
                self.assertEqual(got['result'],(a+b)%256)
                self.assertEqual(got['carry'],int(a+b>=256))
                self.assertEqual(got['overflow'],not -128<=sa+sb<=127)

    def test_encoding_and_specials(self):
        self.assertEqual(to_unsigned(-5,8),251)
        self.assertEqual(to_signed(128,8),-128)
        self.assertEqual(float_record(5.75)['hex'],'0x40B80000')
        self.assertEqual(float_record(-6.5)['hex'],'0xC0D00000')
        self.assertEqual(binary32(2**24+1),2**24)
        self.assertEqual(float_record(2**-149)['category'],'subnormal')
        for bits in (0,-1,1.5):
            with self.assertRaises(ValueError):to_unsigned(1,bits)

    def test_unsigned_algorithms(self):
        for n in range(16):
            for d in range(1,16):
                r=divide(n,d)
                self.assertEqual((r['quotient'],r['remainder']),divmod(n,d))
                self.assertEqual(multiply(n,d)['result'],n*d)
        with self.assertRaises(ZeroDivisionError):divide(3,0)

class CacheTests(unittest.TestCase):
    def test_fields(self):
        c=Cache(4096,16)
        self.assertEqual((c.tag_bits,c.index_bits,c.offset_bits),(20,8,4))
        self.assertEqual(c.fields(0x12345678),dict(tag=0x12345,index=0x67,offset=8))
        c=Cache(8192,32,4)
        self.assertEqual(c.fields(0x12345678),dict(tag=0x2468A,index=0x33,offset=0x18))

    def test_conflicts_and_dirty_lru(self):
        for ways,expected in [(1,[False]*4),(2,[False,False,True,True])]:
            c=Cache(16,4,ways)
            self.assertEqual([c.access(a)['hit'] for a in (0,16,0,16)],expected)
        c=Cache(16,4,2)
        c.access(0);c.access(8,'write',0x12345678,size=4);c.access(0)
        eviction=c.access(16)
        self.assertEqual(eviction['writeback']['base'],8)
        self.assertEqual([c.memory[8+i] for i in range(4)],[0x78,0x56,0x34,0x12])
        self.assertEqual(c.access(8,size=4)['value'],0x12345678)

    def test_random_byte_model_against_reference(self):
        rng=random.Random(42);c=Cache(32,8,2);reference=bytearray(128)
        for _ in range(500):
            a=rng.randrange(32)*4
            if rng.random()<.5:
                v=rng.randrange(1<<32);c.access(a,'write',v,size=4)
                reference[a:a+4]=v.to_bytes(4,'little')
            else:self.assertEqual(c.access(a,size=4)['value'],int.from_bytes(reference[a:a+4],'little'))

    def test_reject_invalid(self):
        for args in [(15,4,1),(16,3,1),(16,4,0)]:
            with self.assertRaises(ValueError):Cache(*args)
        with self.assertRaises(ValueError):Cache(16,4).access(3,size=4)

class CPUAndPipelineTests(unittest.TestCase):
    def test_sum_trace(self):
        result=sum_program()
        self.assertEqual((result['result'],result['retired']),(24,24))
        self.assertEqual(result['branches'],[True,True,True,False])
        self.assertEqual(result['registers'][:5],[0,272,24,0,9])
        self.assertEqual([e['memory_access']['value'] for e in result['events'] if e['instruction'][0]=='lw'],[3,5,7,9])

    def test_negative_array_and_x0(self):
        c=CPU()
        for i,v in enumerate([-2,4,-6,8]):c.store(256+i*4,v)
        c.run(PROGRAM,36)
        self.assertEqual(c.load(512),4)
        c=CPU();c.run({0:('addi',0,0,99),4:('addi',1,0,-1)},8)
        self.assertEqual(c.registers[:2],[0,0xFFFFFFFF])

    def test_cpu_errors(self):
        c=CPU()
        for a in (1,1024,-4):
            with self.assertRaises(ValueError):c.load(a)
        for prog in ({0:('bad',1,2,3)},{0:('addi',32,0,1)},{0:('addi',1,0,2048)}):
            with self.assertRaises(ValueError):CPU().run(prog,4)
        with self.assertRaises(RuntimeError):CPU().run({0:('addi',1,0,1),4:('bne',1,0,4)},8,max_steps=20)

    def test_pipeline_dependency_timing(self):
        e=experiments()['pipeline']
        self.assertEqual(e['independent']['cycles'],14)
        self.assertEqual(e['forward']['cycles'],6)
        self.assertEqual(e['load_use']['cycles'],7)
        self.assertEqual(e['original']['cycles'],8)
        self.assertEqual(e['scheduled']['cycles'],7)
        self.assertEqual([tuple(r['instruction'][:2]) for r in e['original']['rows']],
                         [('lw',4),('add',2),('addi',1)])
        for case in e.values():
            self.assertEqual(case['rows'][0]['stages']['1'],'IF')
            available={}
            for row in case['rows']:
                op,rd,r1,r2=row['instruction']
                for r in (r1,r2):
                    if r:self.assertGreater(row['ex'],available.get(r,0))
                if rd:available[rd]=row['ex']+(op=='lw')

class CourseTests(unittest.TestCase):
    def test_course_complete(self):
        c=json.loads((ROOT/'data/course.json').read_text(encoding='utf-8'))
        self.assertEqual((len(c['scenes']),c['duration']),(60,7200))
        self.assertEqual(sum(x['duration'] for x in c['chapters']),7200)
        for i,s in enumerate(c['scenes']):
            self.assertEqual((s['id'],s['start'],s['duration']),(f'S{i+1:02d}',120*i,120))
            self.assertGreater(s['narration_chars'],300)
            self.assertTrue(s['visual'] and s['question'] and s['answer'])
            self.assertEqual(sum(b['duration'] for b in s['beats']),120)

    def test_integration_observation_layers(self):
        e=experiments()['cache']
        self.assertEqual((e['read_hit_rate'],e['total_hit_rate']),(.75,.6))
        self.assertEqual((e['cache_result'],e['backing_result']),(24,0))
        self.assertIsNone(e['integrated'][-1]['writeback'])

if __name__=='__main__':unittest.main()
