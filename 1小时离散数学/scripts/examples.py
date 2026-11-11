"""Finite reference operations, also useful for changing course examples."""
import itertools
def implies(p,q):return not p or q
def relation_properties(A,R):
 return dict(reflexive=all((a,a) in R for a in A),symmetric=all((b,a) in R for a,b in R),antisymmetric=all(a==b or (b,a) not in R for a,b in R),transitive=all((a,c) in R for a,b in R for bb,c in R if b==bb))
def closure(R):
 out=set(R)
 while True:
  more={(a,c) for a,b in out for bb,c in out if b==bb}
  if more<=out:return out
  out|=more
def function_properties(A,B,f):
 return dict(function=set(f)==set(A) and set(f.values())<=set(B),injective=len(set(f.values()))==len(A),surjective=set(f.values())==set(B))
def connected(vertices,edges):
 seen={vertices[0]}
 while True:
  found=seen|{b for a,b in edges if a in seen}|{a for a,b in edges if b in seen}
  if found==seen:return seen==set(vertices)
  seen=found
def is_tree(vertices,edges):return len(edges)==len(vertices)-1 and connected(vertices,edges)
def prefix_free(words):return all(not b.startswith(a) for a,b in itertools.permutations(words,2))
