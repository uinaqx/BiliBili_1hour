"""Generate source coverage and exercise notes using the final, unchanged timestamps."""
import json,pathlib,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out'
SECTIONS=[
('1.1','行列式的概念','逆序数、奇偶排列、n 阶行列式定义及定义计算'),
('1.2','行列式的性质','转置、交换及推论、行因子及推论、按一行可加、倍加不变'),
('1.3','行列式的展开','余子式、代数余子式、按行列展开及异行配对为零'),
('1.4','行列式的计算','消元为三角形、对角线乘积、范德蒙结构'),
('1.5','克莱默法则','替换列、非零分母条件、齐次方阵的零解与非零解判据'),
('2.1','矩阵的概念','行列尺寸、元素下标、零矩阵、方阵、对角矩阵、单位矩阵'),
('2.2','矩阵的运算','加法、数乘、乘法与次序、幂与多项式、转置、对称与反对称、分块、方阵行列式运算律'),
('2.3','逆矩阵','定义、可逆条件、伴随矩阵、二阶公式、可逆运算性质'),
('2.4','矩阵的初等变换','三类行列变换、初等矩阵、左右乘对应、矩阵等价与标准形、增广表求逆'),
('2.5','矩阵的秩','非零子式、行列秩、取值范围、行满秩与列满秩、阶梯形求秩'),
('3.1','向量组及线性组合','n 维向量、加法数乘、线性组合与表示、向量组等价、方程组向量形式'),
('3.2','向量组的线性相关性','相关与无关定义、判定例子、子组扩充定理、维数上界'),
('3.3','向量组的秩','极大无关组、秩、主元列返回原矩阵、拼接/求和/乘积秩不等式'),
('4.1','线性方程组的可解性','矩阵形式、增广矩阵、齐次和非齐次秩判据'),
('4.2','齐次线性方程组解的结构','封闭性、自由变量、基础解系、向量个数 n-r、通解'),
('4.3','非齐次线性方程组解的结构','特解、齐次通解、两个非齐次解之差、通解结构'),
('5.1','相似矩阵的定义及性质','可逆换基、相似关系及保持特征值/迹/行列式/秩等性质'),
('5.2','方阵的特征值及特征向量','不变直线、非零向量、特征方程、求解、和积及独立性等性质'),
('5.3','方阵可对角化的条件','独立实特征向量数、互异特征值的充分条件、重根反例、对角化与幂'),
('5.4','实对称矩阵的对角化','内积、长度、投影、施密特正交化、单位正交组、正交矩阵、实对称谱分解'),
('6.1','二次型的概念','齐次二次表达式、对称矩阵、交叉项平分、矩阵合同'),
('6.2','标准形及规范形','正交变换步骤、标准形、规范形、正负惯性指数、合同判定'),
('6.3','正定二次型','正定及半正定/不定/负定比较、特征值及顺序主子式判据、常见错误推论'),
]
def stamp(t):
    h,s=divmod(int(t),3600);m,s=divmod(s,60);return f'{h:02}:{m:02}:{s:02}'
def main():
    t=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf8'));assert t['scope']=='complete-course';DEL.mkdir(parents=True,exist_ok=True)
    rows=['# 知识点覆盖表','','依据四页《线性代数知识点.pdf》，保留原有 23 个编号小节。视频重新按概念依赖安排为十章；下列时间来自最终音频时间轴，定位到页面开头。','',
          '原提纲的“性质 2～5”及“两个秩不等式”未列具体公式，本课使用常见明确版本，详见课程契约。覆盖表示介绍并配例子，不表示完整证明原课程的全部定理。','',
          '| PDF 小节 | 本课涵盖内容 | 对应讲解位置 |','| --- | --- | --- |']
    for section,title,scope in SECTIONS:
        hits=[s for s in t['scenes'] if any(tag.startswith(section+'-') for tag in s['tags'])]
        assert hits,section
        locations='<br>'.join(stamp(s['startFrame']/30)+' '+s['chapter']+'：'+s['title'] for s in hits)
        rows.append(f'| {section} {title} | {scope} | {locations} |')
    rows+=['','## 详细标记索引','', '| 知识点标记 | 时间 | 页面 |', '| --- | --- | --- |']
    for s in t['scenes']:
        for tag in s['tags']:rows.append(f"| {tag} | {stamp(s['startFrame']/30)} | {s['key']} {s['title']} |")
    (ROOT/'docs/知识点覆盖表.md').write_text('\n'.join(rows)+'\n',encoding='utf8')
    answers=['# 习题与答案','','每章一题，题目旁白结束后四秒思考，答案在下一页。下列时间是题目和答案页的原始起点。','']
    for c in t['chapters']:
        for i,s in enumerate(c['scenes']):
            if s['kind']!='question':continue
            a=c['scenes'][i+1]
            answers+=['## '+c['title'],'',f"题目：{stamp(s['startFrame']/30)}；答案：{stamp(a['startFrame']/30)}",'',s['narration'],'','**答案：** '+s['answer'],'','**解析：**','',a['narration'],'']
    (ROOT/'docs/习题与答案.md').write_text('\n'.join(answers),encoding='utf8')
    chapters='\n'.join(stamp(c['startFrame']/30)+' '+c['title'] for c in t['chapters'])+'\n'
    (ROOT/'docs/章节目录.txt').write_text(chapters,encoding='utf8');(DEL/'章节目录.txt').write_text(chapters,encoding='utf8')
    for name in ['知识点覆盖表.md','习题与答案.md','制作说明.md']:shutil.copyfile(ROOT/'docs'/name,DEL/name)
    shutil.copyfile(ROOT/'content/完整讲稿.md',DEL/'完整讲稿.md')
    print('DOCUMENTS_READY',len(SECTIONS),'PDF subsections',flush=True)
if __name__=='__main__':main()
