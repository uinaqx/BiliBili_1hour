import textwrap
CHAPTERS=[];CHECKS=[]
HEADERS='''#include <iostream>
#include <vector>
#include <string>
#include <queue>
#include <stack>
#include <unordered_map>
#include <unordered_set>
#include <algorithm>
#include <functional>
#include <stdexcept>
#include <utility>
#include <cassert>
using namespace std;
'''
NODE='struct Node { int value; Node* next; };\n'
CLEAR='void clear(Node* p) { while(p) { Node* next=p->next; delete p; p=next; } }\n'
TREE='''struct Tree { int value; Tree* left; Tree* right; };
void inorder(Tree* p) { if(!p) return; inorder(p->left); cout << p->value << " "; inorder(p->right); }
void preorder(Tree* p) { if(!p) return; cout << p->value << " "; preorder(p->left); preorder(p->right); }
void postorder(Tree* p) { if(!p) return; postorder(p->left); postorder(p->right); cout << p->value << " "; }
'''
TREE_BUILD='''Tree a{2,nullptr,nullptr}, b{6,nullptr,nullptr};
Tree c{10,nullptr,nullptr}, d{14,nullptr,nullptr};
Tree l{4,&a,&b}, r{12,&c,&d}, root{8,&l,&r};
'''
GRAPH='vector<vector<int>> g{{1,2},{0,3},{0,3},{1,2,4},{3}};\n'
def chapter(key,title,english,minutes):
    c=dict(key=key,title=title,english=english,targetMinutes=minutes,scenes=[]);CHAPTERS.append(c);return c
def scene(c,key,title,narration,code='',output=None,notes=None,diagram='overview',kind='lesson',focus=None,context='',runner=None,full=None):
    code=textwrap.dedent(code).strip('\n');narration=''.join(narration.strip().splitlines())
    if key.endswith('-a'):kind='answer'
    row=dict(key=key,section=key,title=title,narration=narration,sourceNarration=narration,code=code,output=output,notes=notes or [],diagram=diagram,kind=kind,focus=focus or [],error=None,panic=False,testFailed=False,filename='main.cpp',excerpt=bool(context or runner),panels=[],hold=4 if kind=='question' else 1.2)
    if code:
        program=full or HEADERS+context+'\n'+(code+'\nint main(){\n'+runner+'\n}\n' if runner is not None else 'int main(){\n'+code+'\n}\n')
        CHECKS.append(dict(key=key,source=program,expected='' if output is None else output,question=kind=='question'))
    c['scenes'].append(row);return row
