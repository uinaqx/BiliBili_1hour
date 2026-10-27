"""Measured teaching index and portable study materials, derived from this course."""
import importlib.metadata,json,pathlib,shutil
import draw
ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def stamp(t):
    h,s=divmod(int(t),3600);m,s=divmod(s,60);return f'{h:02}:{m:02}:{s:02}'
def rows(s):
    out=[]
    for r in s['rows']:out+=['**'+r['label']+'**','',f"$${r['math']}$$" if r['math'] else r['text'],'']
    return out
def main():
    t=load(ROOT/'public/timeline.json');assert t['scope']=='complete-course';DEL.mkdir(exist_ok=True)
    index=['# 逐页考点定位','','时间是正式成片的原始时间，不按整分钟估算。','','| 章节 | 考点 | 视频起点 |','| --- | --- | --- |']
    formulas=['# 公式与题型速查','','公式须与条件一起使用。以下按实际教学顺序整理，详解见完整讲稿。','']
    practice=['# 十章练习与答案','','每章一题；先独立完成，之后再核对参考答案。','','## 练习题',''];answers=['## 参考答案','']
    for c in t['chapters']:
        formulas+=['## '+c['title'],'']
        for i,s in enumerate(c['scenes']):
            index.append(f"| {c['title']} | {s['title']} | {stamp(s['startFrame']/30)} |")
            if s['kind']=='lesson':
                formulas+=['### '+s['title'],'',f"视频起点：{stamp(s['startFrame']/30)}",'']+rows(s)
                formulas+=['检查：'+'；'.join(dict.fromkeys(n for p in s['parts'] for n in p['notes'])),'']
            if s['kind']=='question':
                practice+=['### '+c['key']+' '+c['title'],'',f"题目：{stamp(s['startFrame']/30)}",'']+rows(s)+[p['text'] for p in s['parts']]+['']
                a=c['scenes'][i+1];assert a['kind']=='answer'
                answers+=['### '+c['key']+' '+c['title'],'',f"答案：{stamp(a['startFrame']/30)}",'']+rows(a)+[p['text'] for p in a['parts']]+['']
    for name,text in [('考点定位.md','\n'.join(index)),('公式与题型速查.md','\n'.join(formulas)),('十章练习与答案.md','\n'.join(practice+answers))]:(ROOT/'docs'/name).write_text(text+'\n',encoding='utf8')
    checklist='''# 考前解题步骤清单

1. **向量、平面与直线**：先分清点、方向向量和法向量。夹角用数量积除以模长乘积；先确认向量非零。面积用叉积的模，体积用混合积的绝对值。平面用法向量写点法式；直线用方向向量写参数式，方向分量为零时不要写零作分母。直线与平面位置关系先看方向向量与法向量的数量积，平行时还要检查直线上的点是否在平面上。
2. **定义域与二元极限**：根号内非负、对数真数正、分母非零，取交集。两条路径得到不同值可直接说明极限不存在；有限条路径相同不能证明存在。证明存在可找绝对值上界并夹逼。连续还必须把极限与点值比较。
3. **偏导与全微分**：对谁求导，其余自变量先当常数。先求导，再代入指定点。混合偏导数要沿依赖关系逐层求；交换求导顺序先有相应充分条件。全微分是两个偏导系数分别乘dx、dy，不漏微分符号；线性近似要有可微等前提。
4. **复合与隐函数**：先画依赖树，每条从结果到目标变量的路径分别连乘，再把路径相加。抽象函数下标表示对哪个位置求偏导，代值使用内部变量的对应点。由F(x,y,z)=0解z时，公式带负号，分母Fz须非零并满足隐函数定理条件。梯度方向求导先把给定方向单位化。
5. **极值与最值**：先求驻点，再算A=fxx、B=fxy、C=fyy、D=AC-B²。连续二阶偏导条件下，D>0配A正负，D<0为鞍点，D=0不能下结论。约束极值先列拉格朗日方程，普通正则约束还要检查约束梯度；有端点、边界或奇点时另列候选。闭区域最值比较内部与边界的所有候选，结果代回原函数。
6. **二重积分**：先画区域，选切片方向，再写外层常数区间和内层变量区间。内层先积，外层变量暂作常数。交换次序要重画同一区域，不能只换dx、dy。极坐标把被积函数、范围和dA=r dr dθ一起换；先写清角度定义。奇函数抵消必须同时有对称区域与积分存在条件。
7. **三重积分与应用**：先选最方便的投影与积分顺序。柱坐标dV=r dr dθ dz；本课球坐标ρ为半径、φ从正z轴量起，dV=ρ² sinφ dρ dφ dθ。不同教材角符号可能互换，使用前写清约定。密度用δ，质量是密度积分；重心是一次矩除以质量，分母不可省略。
8. **曲线积分**：先辨ds还是dx、dy、dz。第一类用弧长元，代入参数后乘速度的模，反向不变；第二类带方向，反向变号。格林先检查闭合边界和正向，区域在行进左侧，有洞时内边界通常顺时针；再算Qx-Py。判断路径无关要有适当区域条件，不能只看Py=Qx便忽略孔洞或场的奇点。
9. **曲面积分与空间公式**：第一类用正面积元，图形z=g(x,y)时有√(1+gx²+gy²)。第二类先选法向，向上面积向量是(-gx,-gy,1)dxdy，反向整体变号。高斯须是闭合向外边界且场在内部也无奇点；开曲面可补面后减补面通量。斯托克斯先右手定则，再配旋度与有向面，换面不能穿过场的奇点。
10. **级数**：先检查通项趋零；不趋零直接发散，趋零仍需判别。正项级数选几何、p级数、比较、比值或根值；比值或根值等于1时换方法。交错级数先确认正项最终单调下降到零；绝对、条件收敛分开判断。幂级数先算中心和半径，再单独代两个端点，求导积分后端点也重新查。傅里叶先认周期、奇偶性与a0/2约定，间断点满足相应收敛条件时取左右极限平均，不自动取原函数点值。

看完后先重做10道练习，再选本校往年试卷的基础计算题。不同学校的章节范围、记号和书写评分要求，以本校考纲及教材为准；本课没有覆盖每一种综合难题。
'''
    (ROOT/'docs/考前解题步骤清单.md').write_text(checklist,encoding='utf8')
    readme=f'''# 一小时学完高等数学（下）

面向零基础大学生，侧重常见期末基础题型、公式条件、解题步骤和易错点，不展开定理证明。成片 **{stamp(t['duration'])}**，10章、82页、143段讲解、10道随堂练习。题目、解答、公式板与数学图示均在本工程中编写。

按常见理工类高数下组织：向量与空间解析几何，多元函数与偏导数，全微分与复合函数求导，多元极值与约束极值，二重积分，三重积分及应用，曲线积分与格林公式，曲面积分与高斯/斯托克斯公式，数项级数，幂级数与傅里叶级数。学校的具体考纲可能有差别，使用前按本校往年试卷核对范围。

## 成片与学习材料

- 深色公式板、逐步显示、持续高亮、右侧条件检查，64段原创连续图示，共320秒动态变化。
- 无底部字幕、无背景音乐。1920×1080，H.264/AAC，10个内嵌章节；30fps时间格，动画每格渲染，静态页面用VFR保持，非全程恒定30fps。
- 已授权百炼系统男声，**原始1.0倍语速**。句号间额外停顿0.1秒，逗号不变。没有为凑时长做语速或后期tempo调整。
- [完整讲稿](content/完整讲稿.md)、[考点定位](docs/考点定位.md)、[公式速查](docs/公式与题型速查.md)、[十章练习与答案](docs/十章练习与答案.md)、[考前步骤清单](docs/考前解题步骤清单.md)、[核对参考](references/参考资料.md)。

## 复用现有配音重新渲染

需要Python、FFmpeg/FFprobe。直接依赖见requirements.txt，本次版本见requirements.lock.txt。中文字体为Windows Microsoft YaHei，数学用Matplotlib STIX；字体未打包。其他平台修改draw.py、diagrams.py等脚本中的中文字体路径后，重新做排版检查。

工程保留82份最终逐页WAV和时间信息、143份原始1.0x语音片段及精简复用元数据、143份本地已知文本对齐缓存。复用这些文件不需要账号或网络。

```powershell
python -m pip install -r requirements.lock.txt
python scripts/build_course.py
python scripts/verify_math.py
python scripts/timeline.py
python scripts/layout_review.py
python scripts/check_original_speed.py
python scripts/check.py
python scripts/preview.py
python scripts/check_preview.py
python scripts/render.py --workers 4
python scripts/check.py --final
python scripts/check_audio_placement.py
python scripts/document.py
```

输出位于工程同级`交付/高等数学下一小时`。`timeline.py --layout`仅用于合成时长的排版审查，正式渲染拒绝此时间轴。重新制作最终成片前，始终不加`--layout`重建时间轴。

## 改讲稿、公式或动画

`content/chapters_a.py`至`chapters_e.py`是内容源，author.py定义R/T公式行和P旁白段。focus是人工指定的相关行，show控制当前显示到哪一步；新步骤开始后保持高亮直到下个实际讲解起点，不在句末清空。图示kind/phase选定具体图形及变化含义，moves用人工编写的唯一短语作为启动锚点，不随机分配时间。

`prepare_audio.py`从原始语音直接解码，在句号附近的静音处增加0.1秒；`timeline.py`将短语映射到加入停顿后的实际时间，并在320秒的动态区间逐30fps格渲染。图示实现位于scripts/diagrams.py。改旁白后必须更新受影响语音、对齐、时间轴和验收，不能只改文字沿用旧时间。

## 生成新配音

先在自己的百炼北京地域账号确认模型可用状态、额度及价格。只通过环境变量DASHSCOPE_API_KEY、SFM_WORKSPACE_ID配置，示例文件不含真实值；脚本不读取私有账号加载器。模型qwen-audio-3.0-tts-plus，系统声音longanlufeng。先`python scripts/voice.py --test`，再`python scripts/voice.py`；成功段落按指纹复用。

之后运行`python scripts/prepare_audio.py`，首次需本地Whisper base模型（约145MB，可由Whisper下载），再重建正式时间轴。默认保持原始1.0倍速度；若内容变化导致时长超出约一小时的合理范围，应先改内容。任何语速变化均须事先向用户说明并获得同意。

## 验收与缓存

verify_math.py独立完成117项符号/数值核验；公式排版检查215条表达式。layout_review.py检查所有143个讲解状态和64段动态图示的中间状态。check.py检查最终音频哈希、实际起点、短语锚点、所有动画格、高亮持续及题答分离；--final进一步比对实际编码画面、检查章节与整片音视频解码。check_audio_placement.py对每段开头和末尾取波形样本与最终AAC核对。独立语速校验将原始MP3解码后的全部语音样本与最终逐页PCM逐样本比较，仅允许约定的静音插入。

人工查看关键帧与自动核验的范围在交付验收说明中记录，不声称整片已经逐分钟人工听看。缓存按源码、导入图示、课程、时间轴、音频和字体指纹绑定，失败可继续。可用`--chapter 01`只渲染一章；改图示共用源码会使相关缓存失效。

打包用显式白名单、精简语音元数据、API Key/业务空间标识模式扫描、离线缓存验证和ZIP完整性检查。真实账号、私有加载器、服务原始响应、依赖/渲染缓存和临时日志不进包。新课程制作不会自动上传GitHub。
'''
    (ROOT/'README.md').write_text(readme,encoding='utf8')
    versions=[n+'=='+importlib.metadata.version(n) for n in ['requests','numpy','scipy','Pillow','matplotlib','sympy','openai-whisper','torch']]
    (ROOT/'requirements.lock.txt').write_text('\n'.join(versions)+'\n',encoding='utf8')
    for name in ['考点定位.md','公式与题型速查.md','十章练习与答案.md','考前解题步骤清单.md']:shutil.copy2(ROOT/'docs'/name,DEL/name)
    shutil.copy2(ROOT/'README.md',DEL/'制作与使用说明.md');shutil.copy2(ROOT/'content/完整讲稿.md',DEL/'完整讲稿.md')
    for name in ['章节目录.txt','逐页知识点目录.txt']:shutil.copy2(DEL/name,ROOT/'docs'/name)
    draw.init(t);draw.render(t['scenes'][0],0).save(DEL/'高等数学下_封面.png');print('DOCUMENTATION_READY',flush=True)
if __name__=='__main__':main()
