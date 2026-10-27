"""Fine-grained milestones for narrated algorithm steps, not equally spaced guesses."""
from author import CHAPTERS
BY={s['key']:s for c in CHAPTERS for s in c['scenes']}
def moves(key,index,items):
    p=BY[key]['parts'][index];last=0;p['moves']=[]
    for anchor,target,seconds in items:
        assert p['text'].count(anchor)==1,(key,index,anchor)
        assert last<target<=1;last=target;p['moves'].append(dict(anchor=anchor,target=target,seconds=seconds))
moves('os-01-05',0,[('系统调用进入内核',1,1.2)])
moves('os-01-05',1,[('完成服务后再返回',1,1.4)])
moves('os-03-03',0,[('A在零时刻到达',5/9,2.1),('接着从五运行到八',8/9,1.0),('最后C从八到九',1,.8)])
moves('os-03-04',0,[('A在五时刻完成以后',5/9,.6),('非抢占短作业优先选择C',6/9,.9),('随后才是B',1,.9)])
moves('os-03-05',1,[('A先用二',2/9,.9),('B再用二',4/9,.9),('C只需一便完成',5/9,.9),('随后A用二',7/9,.9),('B用剩下一',8/9,.9),('A再用最后一',1,.9)])
moves('os-04-05',1,[('生产者成功放入一个以后',1,1.2)])
moves('os-05-05',0,[('假想它完成后',1,2.4)])
moves('os-05-05',1,[('完成再释放原有一',.5,1.2),('也能完成',1,1.2)])
moves('os-07-02',0,[('再访问二',1/3,.9),('接着访问零命中',2/3,.9),('继续访问三时',1,.9)])
moves('os-09-02',1,[('五十先到四十三',1/7,.9),('再到二十四、十六',3/7,1.4),('然后转向八十二',1,3.2)])
moves('os-09-03',0,[('本题先向编号增大方向',.5,2.5),('也继续到边界一百九十九',5/8,.9),('再折返服务另一侧',1,1.6)])
moves('os-09-03',1,[('到当前方向最远请求一百九十',4/7,1.2),('即可回头',1,1.3)])
BY['os-01-03']['parts'][0]['focus']=[1];BY['os-01-03']['parts'][0]['show']=1
BY['os-01-03']['parts'][1]['focus']=[2,3]
for s in BY.values():s['narration']=''.join(p['text'] for p in s['parts'])
