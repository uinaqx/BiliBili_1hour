"""Check object relationships across inputs; no undefined-behavior demonstrations."""
import json,pathlib,subprocess,sys
sys.stdout.reconfigure(encoding='utf-8');ROOT=pathlib.Path(__file__).resolve().parents[1];folder=ROOT/'build/properties';folder.mkdir(parents=True,exist_ok=True)
source=r'''#include <cassert>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
std::vector<int> order;
struct Part { int id; Part(int n):id(n){order.push_back(n);} ~Part(){order.push_back(-id);} };
struct Composite { Part a,b; Composite():a(1),b(2){order.push_back(3);} ~Composite(){order.push_back(-3);} };
struct A { A(){order.push_back(1);} ~A(){order.push_back(-1);} };
struct B { B(){order.push_back(2);} ~B(){order.push_back(-2);} };
struct Multiple: A,B { Multiple():A(),B(){order.push_back(3);} ~Multiple(){order.push_back(-3);} };
struct Base { virtual int read() const{return 10;} virtual ~Base()=default; };
struct Derived:Base { int read() const override{return 20;} };
struct Abstract { virtual int area() const=0; virtual ~Abstract()=default; };
struct Square:Abstract { int n; explicit Square(int side):n(side){} int area()const override{return n*n;} };
struct Point {int x,y; Point operator+(const Point& b)const{return {x+b.x,y+b.y};}};
int twice(int x){return x*2;}
double twice(double x){return x*2;}
double divide(double a,double b){if(b==0)throw std::invalid_argument("zero");return a/b;}
struct Guard {~Guard(){order.push_back(7);}};
void fail(){Guard g; throw std::runtime_error("failure");}
int main(){
 int groups=0;
 for(int a=-2;a<=2;++a)for(int b=-2;b<=2;++b){int x=a,y=b;int& r=x;r=y;y=9;assert(x==b&&r==b&&y==9);++groups;}
 order.clear();{Composite c;}assert((order==std::vector<int>{1,2,3,-3,-2,-1}));++groups;
 order.clear();{Multiple m;}assert((order==std::vector<int>{1,2,3,-3,-2,-1}));++groups;
 Derived d;Base& ref=d;Base copy=d;assert(ref.read()==20&&copy.read()==10);++groups;
 const Base& readonly=d;assert(readonly.read()==20);++groups;
 for(int side=0;side<=10;++side){Square s(side);const Abstract& shape=s;assert(shape.area()==side*side);++groups;}
 for(int x=-2;x<=2;++x)for(int y=-2;y<=2;++y){Point a{x,y},b{3,-1};Point c=a+b;assert(c.x==x+3&&c.y==y-1&&a.x==x&&a.y==y);Point r=b+a;assert(r.x==c.x&&r.y==c.y);++groups;}
 assert(twice(3)==6&&twice(3.5)==7.0);++groups;
 for(int n=-3;n<=3;++n){bool caught=false;try{double value=divide(12,n);assert(n!=0&&value==12.0/n);}catch(const std::invalid_argument&){caught=true;}assert(caught==(n==0));++groups;}
 int route=0;try{throw std::invalid_argument("bad");}catch(const std::invalid_argument&){route=1;}catch(const std::exception&){route=2;}assert(route==1);++groups;
 order.clear();try{fail();}catch(const std::exception&){order.push_back(8);}assert((order==std::vector<int>{7,8}));++groups;
 std::cout<<groups<<'\n';
}'''
(folder/'checks.cpp').write_text(source,encoding='utf-8')
compiled=subprocess.run(['g++','-std=c++14','-Wall','-Wextra','-Werror','-pedantic','checks.cpp','-o','checks.exe'],cwd=folder,capture_output=True,text=True)
assert compiled.returncode==0,compiled.stderr
ran=subprocess.run([str(folder/'checks.exe')],cwd=folder,capture_output=True,text=True,timeout=5);assert ran.returncode==0,ran.stderr
groups=int(ran.stdout);assert groups==75,groups
report=dict(allPassed=True,assertionGroups=groups,categories=['references stay bound across assignments','member construction and reverse destruction','multiple base order','virtual dispatch and value slicing','const virtual dispatch','abstract interface across side lengths','operator returns a new point without changing operands','overload selection','normal and exceptional divide routes','specific catch first','destruction during exception propagation'])
(ROOT/'build/property-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('CPP_RELATIONSHIPS_PASSED',groups)
