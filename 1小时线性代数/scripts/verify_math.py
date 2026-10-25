"""Exact arithmetic for teaching examples, theorem conditions and graphic endpoints."""
import json,pathlib,itertools
import sympy as s
ROOT=pathlib.Path(__file__).resolve().parents[1];checks=[]
def check(name,condition):
    good=bool(condition);checks.append(dict(name=name,passed=good));assert good,name
def M(x):return s.Matrix(x)
def main():
    check('向量相加',M([2,1])+M([1,2])==M([3,3]))
    check('组合方程解',M([[1,1],[2,1]])*M([1,3])==M([4,5]))
    check('共线目标不可达',M([[1,2],[2,4]]).row_join(M([1,0])).rank()>1)
    A=M([[1,2,0],[0,1,1]]);B=M([[1,0],[2,1],[0,3]])
    check('行乘列',A*B==M([[5,2],[2,4]]))
    D=M([[2,0],[0,1]]);H=M([[1,1],[0,1]])
    check('复合顺序反例',D*H==M([[2,2],[0,1]]) and H*D==M([[2,1],[0,1]]))
    X=M([[1,2],[3,4]]);S=(X+X.T)/2;K=(X-X.T)/2
    check('对称反对称分解',S+K==X and S.T==S and K.T==-K)
    A=M([[1,2,0],[0,3,1],[2,0,1]])
    check('三阶定义展开',A.det()==7 and A.cofactor(0,1)==2)
    for i in range(3):
        for k in range(3):check(f'展开及异行余子式{i}-{k}',sum(A[i,j]*A.cofactor(k,j) for j in range(3))==(7 if i==k else 0))
    check('消元行列式',M([[1,2,1],[2,5,3],[1,0,2]]).det()==3)
    check('范德蒙',M([[1,1,1],[1,2,4],[1,4,16]]).det()==6)
    check('克莱默解',M([[1,1],[1,-1]])*M([2,1])==M([3,1]))
    for a in [[[2,1],[0,1]],[[1,1],[2,3]],[[1,1],[0,1]]]:
        A=M(a);check('逆矩阵'+str(a),A*A.inv()==s.eye(2) and A*A.adjugate()==A.det()*s.eye(2))
    check('增广消元逆',M([[1,1],[2,3]]).inv()==M([[3,-1],[-2,1]]))
    A=M([[1,2,3],[2,4,6]])
    check('极大无关组',A.rank()==1 and A.rref()[1]==(0,))
    A=M([[1,1,1],[0,1,1]]);h=M([0,-1,1]);p=M([1,1,0]);b=M([2,1])
    check('基础解系',A*h==s.zeros(2,1) and len(A.nullspace())==1)
    check('特解与齐次方向',A*p==b and A*(p+7*h)==b)
    A=M([[2,1],[1,2]]);v1=M([1,1]);v2=M([1,-1]);P=s.Matrix.hstack(v1,v2);Q=P/s.sqrt(2)
    check('特征向量三',A*v1==3*v1);check('特征向量一',A*v2==v2)
    check('迹与行列式',A.trace()==4 and A.det()==3)
    check('相似对角化',P.inv()*A*P==s.diag(3,1))
    check('正交矩阵',Q.T*Q==s.eye(2));check('实对称对角化',Q.T*A*Q==s.diag(3,1))
    J=M([[1,1],[0,1]]);check('缺陷矩阵不可对角化',len((J-s.eye(2)).nullspace())==1 and not J.is_diagonalizable())
    u=M([1,1]);v=M([1,0]);proj=(u.dot(v)/u.dot(u))*u;res=v-proj
    check('投影与残差',proj==M([s.Rational(1,2),s.Rational(1,2)]) and u.dot(res)==0)
    check('未单位化反例',P.T*P==2*s.eye(2))
    x,y,k=s.symbols('x y k',real=True);z=M([x,y]);f=(z.T*A*z)[0]
    check('二次型矩阵',s.expand(f)==2*x*x+2*x*y+2*y*y)
    check('正交标准形',s.expand(((Q*z).T*A*(Q*z))[0])==3*x*x+y*y)
    C=s.diag(1/s.sqrt(3),1);check('规范形与合同',C.T*s.diag(3,1)*C==s.eye(2))
    check('交叉项平分',s.expand((z.T*M([[1,2],[2,3]])*z)[0])==x*x+4*x*y+3*y*y)
    check('顺序主子式正定',A[0,0]>0 and A.det()>0 and A.is_positive_definite)
    check('正行列式非充分',(-s.eye(2)).det()>0 and not (-s.eye(2)).is_positive_definite)
    check('半正定不能只看顺序非负',s.diag(0,-1).det()==0 and not s.diag(0,-1).is_positive_semidefinite)
    F=M([[1,2],[2,1]]);check('正对角线非充分',F.det()==-3 and (v2.T*F*v2)[0]==-2)
    # Independent geometry check: polygon shoelace area equals absolute determinant.
    for a in [[[2,1],[0,1]],[[1,2],[1,2]],[[2,1],[0,3]],[[1,0],[0,-1]]]:
        T=M(a);u=T[:,0];v=T[:,1];pts=[M([0,0]),u,u+v,v]
        area=abs(sum(pts[i][0]*pts[(i+1)%4][1]-pts[i][1]*pts[(i+1)%4][0] for i in range(4)))/2
        check('几何面积'+str(a),area==abs(T.det()))
    course=json.loads((ROOT/'public/course.json').read_text(encoding='utf8'))
    check('十章与十道题',len(course['chapters'])==10 and sum(x['kind']=='question' for c in course['chapters'] for x in c['scenes'])==10)
    check('每页有知识标签',all(x['tags'] for c in course['chapters'] for x in c['scenes']))
    report=dict(allPassed=True,method='SymPy exact arithmetic plus independent area formula',checks=len(checks),results=checks)
    (ROOT/'build/math-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print('MATH_VERIFICATION_PASS',len(checks),flush=True)
if __name__=='__main__':main()
