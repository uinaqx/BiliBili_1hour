"""Check teaching claims at boundaries and across changed data, without online services."""
import json,math,pathlib,sys
sys.stdout.reconfigure(encoding='utf-8');ROOT=pathlib.Path(__file__).resolve().parents[1];groups=0
def check(condition):
    global groups
    assert condition, 'Property group '+str(groups+1);groups+=1
def within(spent,budget=30):return spent<=budget
def total_to(n):
    total=0
    for number in range(1,n+1):total+=number
    return total
def add_fee(amount):amount+=2;return amount
def route(text):
    result=['A']
    try:int(text);result.append('B')
    except ValueError:result.append('C')
    result.append('D');return result
def require_amount(amount):
    if amount<0:raise ValueError('negative amount')
    return amount
a=12;b=a;a=20;check((a,b)==(20,12))
check(12+8==20 and '12'+'8'=='128')
check(7/2==3.5 and 7//2==3 and 7%2==1)
check(-7//2==-4 and -7==(-7//2)*2+(-7%2))
check(2**3==8 and (2+3)*4==20)
check(int('12')+8==20 and int(' 12\n')==12)
for text in ('abc','12.5',''):
    rejected=False
    try:int(text)
    except ValueError:rejected=True
    check(rejected)
check(within(29) and within(30) and not within(31))
check(not within(35) and within(35,40))
check((25>=0 and 25<=30) and not (35>=0 and 35<=30))
check(list(range(1,4))==[1,2,3] and list(range(1,3))==[1,2])
check(total_to(0)==0 and total_to(1)==1 and total_to(3)==6 and total_to(100)==5050)
n=3;shown=[]
while n>0:shown.append(n);n-=1
check(shown==[3,2,1] and n==0)
shown=[]
for n in range(1,6):
    if n==4:break
    shown.append(n)
check(shown==[1,2,3])
shown=[]
for n in range(1,6):
    if n==3:continue
    shown.append(n)
check(shown==[1,2,4,5])
expenses=[12,8,5];check(len(expenses)==3 and expenses[0]==12 and expenses[-1]==5)
check(expenses[1:3]==[8,5] and expenses[:2]==[12,8])
check(expenses[100:]==[] and expenses[:100]==expenses)
failed=False
try:expenses[len(expenses)]
except IndexError:failed=True
check(failed)
empty=[];last=empty[-1] if len(empty)>0 else None;check(last is None)
expenses[1]=10;expenses.append(6);last=expenses.pop();check(expenses==[12,10,5] and last==6)
a=[12];b=a;b.append(8);check(a==[12,8] and a is b)
c=a.copy();c.append(5);check(a==[12,8] and c==[12,8,5] and c is not a)
check(sum([12,8,5])==25 and sum([])==0)
word='Python';check(len(word)==6 and word[0]=='P' and word[-1]=='n' and word[0:2]=='Py')
text=' Tea ';clean=text.strip().lower();check(text==' Tea ' and clean=='tea')
text='tea';text.upper();check(text=='tea' and text.upper()=='TEA')
items='tea,bread,tea'.split(',');check(items==['tea','bread','tea'] and ' | '.join(items)=='tea | bread | tea')
prices={'tea':8};prices['tea']=10;prices['bread']=12;check(len(prices)==2 and prices['tea']==10)
check('cake' not in prices and prices.get('cake') is None and prices.get('cake',0)==0 and 'cake' not in prices)
prices['free']=0;check('free' in prices and prices.get('free',0)==0)
del prices['bread'];check(len(prices)==2 and 'bread' not in prices)
point=(3,5);failed=False
try:point[0]=4
except TypeError:failed=True
check(failed and point[0]==3)
check(len({'tea','bread','tea'})==2 and 'tea' in {'tea','bread'} and len(set())==0)
spent=12;add_fee(spent);check(spent==12);spent=add_fee(spent);check(spent==14)
check(math.sqrt(9)==3.0 and math.ceil(12.3)==13)
folder=(ROOT/'build/properties').resolve();folder.mkdir(parents=True,exist_ok=True);file=folder/'expenses.txt';assert file.parent==folder
file.write_text('12\n',encoding='utf-8')
with file.open('w',encoding='utf-8') as f:f.write('8\n')
check(file.read_text(encoding='utf-8')=='8\n')
file.write_text('12\n',encoding='utf-8')
with file.open('a',encoding='utf-8') as f:f.write('8\n')
check(file.read_text(encoding='utf-8')=='12\n8\n')
with file.open(encoding='utf-8') as f:total=sum(int(line.strip()) for line in f)
check(total==20)
check(require_amount(0)==0 and require_amount(12)==12)
failed=False
try:require_amount(-1)
except ValueError:failed=True
check(failed)
check(route('abc')==['A','C','D'] and route('12')==['A','B','D'])
report=dict(allPassed=True,assertionGroups=groups,scope='numeric and range boundaries, container identity and changes, string return values, lookup absence, function results, file modes and exception routes')
(ROOT/'build/property-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('PYTHON_PROPERTIES_PASSED',groups,flush=True)
