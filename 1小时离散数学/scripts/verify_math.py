"""Independent finite enumerations and cross-checks for the original examples."""
import hashlib,itertools,json,math,pathlib,sys,heapq
import examples as E,diagrams
ROOT=pathlib.Path(__file__).resolve().parents[1];checks=[];data={}
def check(name,actual,expected):
 assert actual==expected,(name,actual,expected);checks.append(dict(name=name,actual=actual,expected=expected))
def main():
 for p,q in itertools.product([False,True],repeat=2):
  check(f'implication-{p}-{q}',E.implies(p,q),not(p and not q))
  check(f'demorgan-and-{p}-{q}',not(p and q),not p or not q)
  check(f'demorgan-or-{p}-{q}',not(p or q),not p and not q)
  check(f'equiv-dnf-{p}-{q}',p==q,(p and q) or (not p and not q))
 check('affirm-consequent-counterexample',E.implies(False,True) and True and not False,True)
 grades=[72,85,48,91];check('all-pass',all(x>=60 for x in grades),False);check('some-pass',any(x>=60 for x in grades),True)
 for bits in itertools.product([False,True],repeat=4):check('quantifier-negation-'+str(bits),not all(bits),any(not b for b in bits))
 A={1,2,3};B={3,4};U=set(range(1,6))
 for name,act,exp in [('union',A|B,{1,2,3,4}),('intersection',A&B,{3}),('difference',A-B,{1,2}),('reverse-difference',B-A,{4}),('complement',U-A,{4,5}),('de-morgan',(U-(A|B)),(U-A)&(U-B))]:check(name,sorted(act),sorted(exp))
 check('empty-subset',set()<=A,True);check('empty-size',len(set()),0);check('singleton-empty',len({frozenset()}),1)
 check('powerset-two',sum(math.comb(2,k) for k in range(3)),4);check('product-two-two',len(list(itertools.product([1,2],['a','b']))),4)
 check('sports-union',18+15-7,26);check('sports-none',30-26,4);check('q3-union',22+17-8,31);check('q3-none',40-31,9)
 R={(1,1),(2,2),(3,3),(1,2),(2,3)};props=E.relation_properties({1,2,3},R)
 for key,value in dict(reflexive=True,symmetric=False,antisymmetric=True,transitive=False).items():check('relation-'+key,props[key],value)
 check('transitive-closure',sorted(E.closure(R)),sorted(R|{(1,3)}))
 Q={(a,b) for a in range(6) for b in range(6) if a%3==b%3};props=E.relation_properties(set(range(6)),Q)
 for k in ['reflexive','symmetric','transitive']:check('congruence-'+k,props[k],True)
 check('partition',[[x for x in range(6) if x%3==i] for i in range(3)],[[0,3],[1,4],[2,5]])
 S={1,2,3,6};D={(a,b) for a in S for b in S if b%a==0};props=E.relation_properties(S,D)
 for k in ['reflexive','antisymmetric','transitive']:check('divisibility-'+k,props[k],True)
 check('incomparable-2-3',(2,3) not in D and (3,2) not in D,True)
 f={1:'a',2:'b',3:'a'}
 for k,val in dict(function=True,injective=False,surjective=True).items():check('q5-'+k,E.function_properties([1,2,3],['a','b'],f)[k],val)
 check('composition',2*(3+1),8);check('reverse-composition',2*3+1,7)
 funcs=list(itertools.product(range(2),repeat=3));check('all-functions-3-to-2',len(funcs),8);check('injective-3-to-2',sum(len(set(x))==3 for x in funcs),0)
 check('injections-3-to-4',len(list(itertools.permutations(range(4),3))),24);check('birthday-guarantee',math.ceil(25/12),3)
 check('outfits',len(list(itertools.product(range(3),range(2)))),6);check('permutation-5-3',len(list(itertools.permutations(range(5),3))),60);check('combination-5-3',len(list(itertools.combinations(range(5),3))),10)
 check('binary-length-3',len(list(itertools.product([0,1],repeat=3))),8);check('binary-two-ones',sum(sum(b)==2 for b in itertools.product([0,1],repeat=3)),3)
 check('required-person',sum(0 in g for g in itertools.combinations(range(5),3)),6);check('at-least-one-of-two',sum(0 in g or 1 in g for g in itertools.combinations(range(5),3)),9)
 check('q6-group',math.comb(6,2),15);check('q6-roles',math.perm(6,2),30)
 a=[2]
 for _ in range(8):a.append(2*a[-1]+1)
 for i,x in enumerate(a):check('recurrence-'+str(i),x,3*2**i-1)
 F=[0,1]
 for _ in range(5):F.append(F[-1]+F[-2])
 check('fibonacci',F,[0,1,1,2,3,5,8]);check('q7-fourth',1+3*3,10)
 for n in range(1,21):check('sum-formula-'+str(n),sum(range(1,n+1)),n*(n+1)//2)
 names=list(diagrams.VERTICES);edges=diagrams.EDGES;check('graph-edges',len(edges),5);check('graph-degrees',[sum(a in e for e in edges) for a in names],[3,2,3,2]);check('graph-connected',E.connected(names,edges),True)
 route=list('ABCDAC');check('euler-uses-all-edges',sorted(tuple(sorted(e)) for e in zip(route,route[1:])),sorted(tuple(sorted(e)) for e in edges));check('euler-endpoints',[route[0],route[-1]],['A','C'])
 weighted=diagrams.WEIGHTS;trees=[]
 for es in itertools.combinations(edges,3):
  if E.is_tree(names,es):trees.append(sum(weighted[e] for e in es))
 check('mst-minimum',min(trees),6);check('selected-tree',E.is_tree(names,edges[:3]),True)
 paths=[]
 for count in range(3):
  for mids in itertools.permutations(['B','C'],count):
   path=['A',*mids,'D'];total=0
   for a,b in zip(path,path[1:]):
    edge=(a,b) if (a,b) in weighted else (b,a)
    if edge not in weighted:break
    total+=weighted[edge]
   else:paths.append(total)
 check('shortest-A-D',min(paths),6)
 check('q9-tree-edges',8-1,7);check('valid-prefix',E.prefix_free(['0','10','11']),True);check('invalid-prefix',E.prefix_free(['0','01','11']),False)
 heap=[5,2,1];heapq.heapify(heap);cost=0
 while len(heap)>1:s=heapq.heappop(heap)+heapq.heappop(heap);cost+=s;heapq.heappush(heap,s)
 check('huffman-cost',cost,11)
 Z=range(4)
 for a,b,c in itertools.product(Z,repeat=3):check('mod4-assoc-'+str((a,b,c)),((a+b)%4+c)%4,(a+(b+c)%4)%4)
 check('mod4-inverses',[next(b for b in Z if (a+b)%4==0) for a in Z],[0,3,2,1]);check('mod4-unit',all((a+0)%4==a==(0+a)%4 for a in Z),True)
 data.update(sets=dict(A=sorted(A),B=sorted(B),U=sorted(U)),relation=sorted(R),equivalenceClasses=[[0,3],[1,4],[2,5]],graph=dict(vertices=names,edges=edges,degrees=[3,2,3,2],eulerRoute=route,mstWeight=6),huffmanCost=11)
 (ROOT/'build/verified-examples.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
 report=dict(allPassed=True,checks=len(checks),courseSha256=hashlib.sha256((ROOT/'public/course.json').read_bytes()).hexdigest(),scope='finite enumerations, counterexamples and independent numeric checks; does not claim all abstract theorems formally proved',results=checks)
 (ROOT/'build/examples-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('MATH_EXAMPLES_PASS',len(checks),flush=True)
if __name__=='__main__':main()
