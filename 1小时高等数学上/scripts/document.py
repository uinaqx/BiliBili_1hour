"""Write a measured topic index, exam checklist, formulas and practice answers."""
import importlib.metadata,json,pathlib,shutil
import draw
ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def stamp(t):
    h,s=divmod(int(t),3600);m,s=divmod(s,60);return f'{h:02}:{m:02}:{s:02}'
def math_rows(s):
    result=[]
    for r in s['rows']:result += ['**'+r['label']+'**','',f"$${r['math']}$$" if r['math'] else r['text'],'']
    return result
def main():
    t=load(ROOT/'public/timeline.json');assert t['scope']=='complete-course';course=load(ROOT/'public/course.json');by={s['key']:s for s in t['scenes']}
    keys=['ca-01-03','ca-01-05','ca-01-06','ca-01-07','ca-02-01','ca-02-02','ca-02-03','ca-03-01','ca-03-05','ca-04-01','ca-04-02','ca-03-03','ca-03-04','ca-04-03','ca-04-04','ca-04-06','ca-05-01','ca-05-03','ca-06-01','ca-06-02','ca-06-04','ca-06-05','ca-06-06','ca-07-01','ca-07-01','ca-07-02','ca-08-02','ca-08-01','ca-08-04','ca-08-05','ca-07-04','ca-07-07','ca-08-07','ca-09-01','ca-09-03','ca-10-01','ca-10-02','ca-10-03','ca-10-05']
    assert len(keys)==len(course['topics'])==39
    rows=['# 39 组考点定位','','原始成片时间，按用户知识点清单排列。相关展开页仍按课程顺序紧接讲解。','','| 知识点 | 视频起点 | 主讲页 |','| --- | --- | --- |']
    for topic,key in zip(course['topics'],keys):assert topic in by[key]['tags'];rows.append(f"| {topic} | {stamp(by[key]['startFrame']/30)} | {by[key]['title']} |")
    (ROOT/'docs/考点定位.md').write_text('\n'.join(rows)+'\n',encoding='utf8')
    formulas=['# 公式与题型速查','','条件和易错点与视频一致。按章节查找，公式使用 LaTeX 记法。完整逐步讲解见完整讲稿。','']
    practice=['# 十章练习与答案','','先做题，再往下看答案；每题对应视频中的独立练习页。','','## 练习题',''];answers=['## 参考答案','']
    for c in t['chapters']:
        formulas+=['## '+c['title'],'']
        for i,s in enumerate(c['scenes']):
            if s['kind']=='lesson':
                formulas+=['### '+s['title'],'',f"视频起点：{stamp(s['startFrame']/30)}",'']+math_rows(s)
                notes=list(dict.fromkeys(n for p in s['parts'] for n in p['notes']));formulas+=['检查：'+'；'.join(notes),'']
            if s['kind']=='question':
                practice+=['### '+c['key']+' '+c['title'],'',s['parts'][0]['text'],'']+math_rows(s)
                answer=c['scenes'][i+1];assert answer['kind']=='answer';answers+=['### '+c['key']+' '+c['title'],'']+math_rows(answer)+[p['text'] for p in answer['parts']]+['']
    (ROOT/'docs/公式与题型速查.md').write_text('\n'.join(formulas),encoding='utf8');(ROOT/'docs/十章练习与答案.md').write_text('\n'.join(practice+answers),encoding='utf8')
    checklist='''# 考前解题步骤清单

1. **极限**：先代入判型；能约分先约分。等价替换保留内部系数和整体结构，遇加减抵消谨慎处理。洛必达先检查零比零或无穷比无穷，分子分母分别求导，每次重新判型。
2. **连续与间断**：先分别算左右极限，再与点值比。可去与跳跃的两侧极限都有限；无穷、振荡归第二类。零点存在先写连续和端点异号，不自动推出唯一。
3. **求导**：外层求导、内部照抄、乘内层导数。乘积两项、商的减号、余弦负号都要检查。抽象函数保留撇号和内部参数；幂指函数先取对数。
4. **特殊求导**：参数一阶为y对参数的导数除以x对参数的导数；二阶再求导后还要再除一次。隐函数含y的复合项补y撇。切线先点后斜率，法线用负倒数，水平切线的法线竖直。微分最后有dx。
5. **中值定理**：先列闭区间连续、开区间可导等条件，再选对应结论。罗尔还需端点值相等；拉格朗日算端点差商；柯西比例式要保证分母条件。
6. **导数应用**：先定义域，再找关键点、分段验号。极值比较一阶左右变号，二阶判别法先有一阶为零；二阶为零不能直接下结论。拐点要求连续且凹凸改变。闭区间最值不要漏端点和不可导候选点，最值代回原函数。
7. **渐近线**：有限位置检查至少一侧是否无穷；无穷远检查水平或斜线。斜线先求k再求b，最后写直线方程。正负无穷两端分别检查。
8. **积分**：分清定与不定。不定加C，定积分上限减下限。换元时表达式、微分和上下限配套；新变量配新端点。分部积分先列u、dv、du、v，再用uv减积分。
9. **定积分与应用**：对称区间且积分存在，才能用偶倍奇零。反常积分先找所有奇点，分别取极限；无穷端的幂分母要求p>1，零端要求p<1。面积上减下或右减左，交换位置时分段。体积先轴与半径，再写平方之差，不能把半径差整体平方。
10. **微分方程**：先识别可分离、一阶线性或二阶常系数齐次。分离时除去的h(y)=0常数解要检查补回。一阶线性先标准化，再用积分因子。二阶先解特征根，不同实根、重根、复根分别套模板。先通解后初值，最后代回原方程核对。

凹凸方向与二阶导符号在视频中并列显示，单独凹/凸名称按本校教材。练习先独立重做，再用本校往年基础题确认题型范围和书写要求。
'''
    (ROOT/'docs/考前解题步骤清单.md').write_text(checklist,encoding='utf8')
    refs='''# 核对参考

讲稿、题型组合、解题页与配音为本工程编写，未复制教材证明。定理使用条件和常见边界情况核对下列大学教材：

- [OpenStax 微分中值定理](https://openstax.org/books/calculus-volume-1/pages/4-4-the-mean-value-theorem)
- [OpenStax 洛必达法则](https://openstax.org/books/calculus-volume-1/pages/4-8-lhopitals-rule)
- [OpenStax 微积分基本定理](https://openstax.org/books/calculus-volume-1/pages/5-3-the-fundamental-theorem-of-calculus)
- [OpenStax 反常积分](https://openstax.org/books/calculus-volume-2/pages/3-7-improper-integrals)
- [OpenStax 二阶线性微分方程](https://openstax.org/books/calculus-volume-3/pages/7-1-second-order-linear-equations)

中文教材对单独“凹/凸”的名称可能不同，本工程以凹向上/凹向下并列二阶导符号，具体名称以学生本校教材及考试要求为准。
'''
    (ROOT/'references/参考资料.md').write_text(refs,encoding='utf8')
    readme=f'''# 一小时学完高等数学（上）

面向零基础大学生的期末基础题型课。成片 **{stamp(t['duration'])}**，共 10 章、39 组考点、78 页、136 段讲解。重点是题型识别、必要使用条件、公式、计算步骤和易错点，不展开证明与概念内涵。

画面是深色公式板，逐步显示计算过程，当前相关步骤持续高亮。无底部字幕、无背景音乐。1920×1080，以 30fps 时间格、静态语义事件 VFR 输出 H.264/AAC，并内嵌 10 个章节。配音为已授权百炼系统男声，句号停顿额外增加0.1秒，逗号不改。

## 学习材料

- [39组考点定位](docs/考点定位.md)
- [公式与题型速查](docs/公式与题型速查.md)
- [十章练习与答案](docs/十章练习与答案.md)
- [考前步骤清单](docs/考前解题步骤清单.md)
- [完整讲稿与分镜](content/完整讲稿.md)
- [核对参考](references/参考资料.md)

本课以常见理工类高数上基础题组织内容。学校的凹凸命名、考查深度与评分要求以本校教材、试卷为准。看完后独立重做练习，并用本校往年基础题继续练习。

## 可编辑工程与重新制作

需要 Python、FFmpeg/FFprobe；依赖见 requirements.txt，本次版本见 requirements.lock.txt。中文用 Microsoft YaHei，数学用 Matplotlib 自带 STIX。系统中文字体未打包；非 Windows 平台修改 scripts/draw.py 的字体路径并重新做排版检查。

工程含最终逐页音频、时间信息和已精简元数据的配音缓存，复用现有配音重新渲染不需要语音账号。

```powershell
python -m pip install -r requirements.lock.txt
python scripts/build_course.py
python scripts/verify_math.py
python scripts/timeline.py
python scripts/layout_review.py
python scripts/check.py
python scripts/preview.py
python scripts/check_preview.py
python scripts/render.py
python scripts/check.py --final
python scripts/check_audio_placement.py
```

输出位于工程同级的 `交付/高等数学上一小时`。不要用 `timeline.py --layout` 的合成时长冒充正式视频，该模式仅用于排版检查。

`content/chapters_a.py` 到 `chapters_e.py` 保存讲稿和分镜。每页有固定公式行；P的focus是教师指定的相关行，show是当前显示到哪一行。没有讲到的后续步骤保持隐藏。改公式、标签或旁白后先构建清单；改旁白还需重新生成相应语音，再对齐，不能按字数平均估计时间。

新配音通过自己的环境变量 `DASHSCOPE_API_KEY` 与 `SFM_WORKSPACE_ID` 配置，脚本不自动读取.env。先执行 `python scripts/voice.py --test`，再 `python scripts/voice.py`。已成功片段按指纹缓存。模型是北京地域 `qwen-audio-3.0-tts-plus`，声音 `longanlufeng`；模型权限、额度和价格应在自己的百炼控制台确认。工程不包含真实API Key、业务空间ID或私有账号加载器。

之后执行 `python scripts/prepare_audio.py` 完成最终速度、句号停顿和本地已知文本对齐；首次需要本地 Whisper base 模型。再重新生成时间轴、排版、试片、成片与检查记录。默认根据实测语音保持在58～63分钟，内容大幅变化时应调整讲稿，不用长静音补时长。

## 检查与缓存

`verify_math.py` 独立核验例题计算和边界例子，报告绑定课程清单。`draw.py` 检查所有公式、字体和侧栏尺寸。高亮实际使用的state函数在 `check.py` 中做保持、静音和换页测试。最终模式逐个检查计划显示状态的真实编码像素、公式逐步显示、章节与完整解码；音轨脚本对每段开头与末段做波形位置核对。人工抽查、自动检查与整片人工听看是不同范围，验收记录会明确区分。

按章缓存可失败后续跑；缓存目录和临时编译/渲染结果不进入交付包。打包用显式文件清单、精简语音缓存元数据、密钥/业务空间ID模式扫描及ZIP路径和CRC校验。制作本地视频不自动授权上传GitHub。
'''
    (ROOT/'README.md').write_text(readme,encoding='utf8')
    versions=[]
    for name in ['requests','numpy','scipy','Pillow','matplotlib','sympy','openai-whisper','torch']:versions.append(name+'=='+importlib.metadata.version(name))
    (ROOT/'requirements.lock.txt').write_text('\n'.join(versions)+'\n',encoding='utf8')
    for name in ['考点定位.md','公式与题型速查.md','十章练习与答案.md','考前解题步骤清单.md']:shutil.copy2(ROOT/'docs'/name,DEL/name)
    shutil.copy2(ROOT/'README.md',DEL/'制作与使用说明.md');shutil.copy2(DEL/'章节目录.txt',ROOT/'docs/章节目录.txt');shutil.copy2(DEL/'逐页知识点目录.txt',ROOT/'docs/逐页知识点目录.txt')
    draw.init(t);draw.render(t['scenes'][0],0).save(DEL/'高等数学上_封面.png');print('DOCUMENTATION_READY',flush=True)
if __name__=='__main__':main()
