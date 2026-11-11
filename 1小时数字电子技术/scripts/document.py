"""Deliver measured chapters, study notes, original exercises and editable-project guide."""
import json,pathlib,shutil
import draw
ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def stamp(t):
    h,s=divmod(int(t),3600);m,s=divmod(s,60);return f'{h:02}:{m:02}:{s:02}'
def rows(s):
    out=[]
    for r in s['rows']:out += [r['label']+'：',('$'+r['math']+'$') if r['math'] else r['text'],'']
    return out
def main():
    t=load(ROOT/'public/timeline.json');assert t['scope']=='complete-course';DEL.mkdir(parents=True,exist_ok=True)
    maths=load(ROOT/'build/examples-verification.json');rtl=load(ROOT/'build/rtl-verification.json');formula=load(ROOT/'build/formula-review.json');motion=sum(len(u['motions']) for s in t['scenes'] for u in s['units']);parts=sum(len(s['parts']) for s in t['scenes'])
    directory='\n'.join(stamp(c['startFrame']/30)+' '+c['title'] for c in t['chapters'])+'\n';(ROOT/'docs/章节目录.txt').write_text(directory,encoding='utf8')
    index=['# 知识点定位',''];guide=['# 数字电子技术基础速查','','公式要连同有效电平、位宽、初态、有效边沿与模型条件一起使用。完整解释见讲稿。',''];practice=['# 十章练习与答案','']
    for c in t['chapters']:
        guide+=['## '+c['title'],'']
        for i,s in enumerate(c['scenes']):
            time=stamp(s['startFrame']/30);index+=['- '+time+' '+s['title']]
            if s['kind']=='lesson':guide+=['### '+s['title'],'','视频起点：'+time,'']+rows(s)+['；'.join(dict.fromkeys(n for p in s['parts'] for n in p['notes'])),'']
            if s['kind']=='question':
                a=c['scenes'][i+1];assert a['kind']=='answer';practice+=['## '+c['title'],'','题目 '+time,'']+rows(s)+[s['narration'],'','答案 '+stamp(a['startFrame']/30),'']+rows(a)+[a['narration'],'']
    for name,lines in [('知识点定位.md',index),('数字电子技术基础速查.md',guide),('十章练习与答案.md',practice)]: (ROOT/'docs'/name).write_text('\n'.join(lines)+'\n',encoding='utf8')
    readme=f'''# 一小时讲完数字电子技术：基础与电路

面向零基础大学生，成片时长{stamp(t['duration'])}（{t['duration']:.3f}秒）。10章、{len(t['scenes'])}页、{parts}段讲解，每章一道原创题，题目说完留4秒，再显示独立答案页。

课程依次学习数制与编码、逻辑门与电平特性、逻辑代数与卡诺图、组合逻辑分析与设计、常用组合逻辑器件、锁存器与触发器、时序电路分析与设计、计数器与寄存器、存储器与可编程逻辑、脉冲波形与数模转换。先看具体输入和输出，再归纳规则与名称。

## 画面与声音

1920×1080，深色公式、真值表、电路与波形，右侧讲解要点。第一页直接展示十章知识地图。当前公式或说明持续选中，在下一段实际旁白开始时移动，静音与思考期继续保持。{motion}段人工选定短语触发的动画，共{t['continuousMotionSeconds']:.2f}秒；动态段按30fps网格逐格生成，静态段VFR保持，非全片恒定30fps。无底部字幕、无音乐。

百炼qwen-audio-3.1-tts-plus、许南川xunanchuan_v3.1、原生rate=1.05；后期tempo=1.0。句号额外增加0.1秒，逗号不变。未为凑时长额外加速或减速。保留原始配音、句号声学边界、最终WAV与时间缓存，工程可离线复用现有声音。

## 模型与验证

本课包含{maths['checks']}项有限输入枚举与计算检查，{formula['formulas']}条公式排版；另有{rtl['normalSimulations']}组正常RTL仿真与{rtl['expectedFailures']}组预期失败，共{rtl['checks']}项自检。RTL采用Icarus Verilog 13.0，测试记录与波形均保留。

D锁存器和D触发器使用实际RTL仿真波形。其他图示按本课约定生成，明确标出理想功能或教学示意。门限、毛刺、脉动计数、建立保持和施密特波形不是器件实测。模三状态机明确规定11下一拍恢复00。ADC使用向下分箱的教学模型，不能直接套用四舍五入量化误差。细节见references/参考资料.md。

## 工程目录

- content/：原创讲稿、每段对应的选中行、题答、人工选择的动画触发短语。
- public/course.json与timeline.json：完整课程与实测时间轴。
- scripts/diagrams.py：可编辑门电路、卡诺图、状态表、寄存器、存储与转换动画。
- scripts/rtl_diagrams.py与build/simulation-data.json：实际VCD波形的慢放展示。
- scripts/examples.py与verify_math.py：独立数字逻辑与数值例子检查。
- examples/：23组RTL测试及预期失败；用于扩展验证，学习本课不要求先懂Verilog。
- public/audio/与audio_original/：{len(t['scenes'])}份最终逐页WAV与{parts}份原始MP3，配音元数据只留复用字段。
- docs/与references/：章节、基础速查、练习答案、资料、验收记录及自己的百炼账号配置说明。

## 离线重渲染

需要Python、FFmpeg/ffprobe。依赖版本见requirements.lock.txt。公式使用Matplotlib MathText与STIX，无需完整TeX。中文字体为Windows Microsoft YaHei；字体不随包分发，跨系统需修改字体路径并复查排版。

```powershell
python -m pip install -r requirements.lock.txt
python scripts/document.py
python scripts/verify_math.py
python scripts/layout_review.py
python scripts/check_original_speed.py
python scripts/check.py
python scripts/preview.py
python scripts/check_preview.py
python scripts/render.py --workers 4
python scripts/check.py --final
python scripts/check_audio_placement.py
```

已有时间轴、公式、声音和仿真数据可直接复用。若要重新运行RTL自检，安装Icarus Verilog，或将IVERILOG_BIN指向其bin目录，再运行python scripts/verify_rtl.py。有限计算检查与正常渲染不需要重新调用在线语音服务。

## 修改内容与生成新声音

修改content后运行build_course.py。若只改图示，复用原声音与时间轴，再运行布局检查、内部试片及渲染。若旁白文字改变，使用自己的DASHSCOPE_API_KEY与SFM_WORKSPACE_ID运行voice.py生成对应新段，然后运行prepare_audio.py、timeline.py、原速检查及后续检查。prepare_audio.py需要本地Whisper base权重，默认路径为用户目录.cache/whisper/base.pt，权重不随包提供。

.env.example为空配置样例，脚本从进程环境读取真实账号。先阅读docs/百炼语音配置说明.md，确认模型权限、额度和费用。已有声音无需账号即可离线复用。不要把真实账号值放进代码、文档、日志或公开仓库。

timeline.py --layout只用于估算排版，render.py会拒绝该时间轴。修改课程、声音或绘图后旧验收记录失效；完成本次检查后运行document.py、delivery_report.py和package.py。

## 验收与交付边界

全部页面、旁白段落、思考与答案页做布局和持续选中检查；试片检查编码后的图示中间状态；最终视频另做画面像素、章节、音轨放置位置及完整解码检查。具体次数、覆盖范围和文件SHA-256见验收记录。有限测试不等于真实器件电气验证，也不声称逐分钟人工听完整片。

工程白名单ZIP包含源文件、已有声音和可复用时间资料，排除真实API Key、Workspace ID、私有账号加载器、请求标识、系统字体、Whisper权重、依赖缓存和大量渲染中间图。本次未自动上传GitHub。
'''
    (ROOT/'README.md').write_text(readme,encoding='utf8')
    for src,name in [(ROOT/'README.md','制作与使用说明.md'),(ROOT/'content/完整讲稿.md','完整讲稿.md'),(ROOT/'references/参考资料.md','参考资料.md'),*[(ROOT/'docs'/n,n) for n in ['章节目录.txt','知识点定位.md','数字电子技术基础速查.md','十章练习与答案.md']]]:shutil.copy2(src,DEL/name)
    draw.init(t);draw.render(t['scenes'][0],0).save(DEL/'数字电子技术_知识地图.png');print('DOCUMENTATION_READY',flush=True)
if __name__=='__main__':main()
