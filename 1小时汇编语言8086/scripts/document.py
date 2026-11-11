"""Generate student materials and an editable-project guide from the final course."""
import json,pathlib,shutil
import draw
ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def stamp(t):
 h,s=divmod(int(t),3600);m,s=divmod(s,60);return f'{h:02}:{m:02}:{s:02}'
def shown(s):
 if s.get('code'):return ['```asm',*s['code'],'```','']
 return [line for row in s['rows'] for line in [row['label']+'：'+row['text'],'']]
def main():
 t=load(ROOT/'public/timeline.json');assert t['scope']=='complete-course';DEL.mkdir(parents=True,exist_ok=True)
 m=load(ROOT/'build/examples-verification.json');parts=sum(len(s['parts']) for s in t['scenes']);highlights=sum(len(u['highlights']) for s in t['scenes'] for u in s['units'])
 directory='\n'.join(stamp(c['startFrame']/30)+' '+c['title'] for c in t['chapters'])+'\n';(ROOT/'docs/章节目录.txt').write_text(directory,encoding='utf8')
 index=['# 知识点定位',''];guide=['# 汇编语言基础速查','','本课使用8086实模式与NASM Intel语法。按位宽、数据解释、段地址和执行路径阅读。',''];practice=['# 十章练习与答案',''];narration=['# 一小时讲完汇编语言：旁白讲稿',''];summaries=['# 逐页总结','','每页总结覆盖本页全部讲解；练习页为提示，答案页给出结果与原因。','']
 for c in t['chapters']:
  guide+=['## '+c['title'],''];narration+=['## '+c['title'],''];summaries+=['## '+c['title'],'']
  for i,s in enumerate(c['scenes']):
   time=stamp(s['startFrame']/30);index+=['- '+time+' '+s['title']]
   narration+=['### '+time+' '+s['title'],'']+[line for p in s['parts'] for line in [p['text'],'']]
   summaries+=['### '+time+' '+s['title'],'']+['- '+note for note in s['summary']]+['']
   if s['kind']=='question':narration+=['（思考4秒，随后展示答案。）','']
   if s['kind']=='lesson':guide+=['### '+s['title'],'','视频起点：'+time,'']+shown(s)+['- '+note for note in s['summary']]+['']
   if s['kind']=='question':
    a=c['scenes'][i+1];assert a['kind']=='answer';practice+=['## '+c['title'],'','题目 '+time,'']+shown(s)+[s['narration'],'','答案 '+stamp(a['startFrame']/30),'']+shown(a)+[a['narration'],'']
 for name,lines in [('知识点定位.md',index),('汇编语言基础速查.md',guide),('十章练习与答案.md',practice),('旁白讲稿.md',narration),('逐页总结.md',summaries)]:
  (ROOT/'docs'/name).write_text('\n'.join(lines)+'\n',encoding='utf8')
 readme=f'''# 一小时讲完汇编语言：8086基础

面向零基础大学生，成片实测{stamp(t['duration'])}（{t['duration']:.3f}秒）。10章、{len(t['scenes'])}页、{parts}段讲解；每章一道原创练习，说完留4秒思考，再展示独立答案。

从MOV、ADD的具体变化开始，依次学习体系结构与数据表示、数据传送与寻址、算术与标志、逻辑与移位、分支、循环与数组、栈与调用、字符输入输出、程序组织与调试，最后完成总和与最大值的小程序。先看数据和步骤，再给规则与名称。

## 画面与讲解

1920×1080，深色布局。左侧代码34px，左下完整运行结果30px；右侧每页4条具体总结，涵盖操作、示例数值与结论。总结覆盖同页全部讲解，整页持续显示。练习页给解题步骤，答案页给结果与原因。第一页直接展示十章知识地图。无底部字幕、无背景音乐。

{highlights}处人工选定的旁白短语决定代码行与实际执行状态。当前高亮持续保留，下一处讲解开始时才移动。{t['continuousMotionSeconds']:.0f}秒数据流与概念动画按30fps网格生成，静态画面使用VFR保持。寄存器、标志、内存、栈与输出从实际机器码执行记录读取。

讲稿以自然肯定式表达说明“是什么、怎么做、得到什么”，减少预设误解、模板澄清和重复限定。完整文字在content/完整讲稿.md，纯旁白、逐页总结和速查在docs/。

## 语音

百炼qwen-audio-3.1-tts-plus、许南川xunanchuan_v3.1、原生rate=1.05，后期tempo=1.0。中文句号额外增加0.1秒，逗号不变。原始声音与最终逐页WAV全部保留，离线重渲染直接复用。旁白改动后仅生成变动段落。

## 指令执行与示例

使用8086实模式、NASM Intel语法，源文件声明CPU 8086、BITS 16、ORG 100h。NASM将{m['normalPrograms']}组正常示例汇编为机器码，Unicorn实际执行，另有{m['expectedFailures']}组预期失败，共{m['checks']}项检查。测试初态与DOS服务适配范围见references/参考资料.md。

- content/：十章讲稿、题答、整页总结、人工短语及代码行映射。
- scripts/：声音生成、声学对齐、执行验证、绘图、时间轴、渲染和检查。
- examples/：完整可汇编源码、错误示例与版本观察。
- build/assembled/：当前机器码与NASM源行列表。
- build/execution-data.json：实际执行快照；build/alignment/：声音时间资料。
- public/course.json与timeline.json：课程清单与实测时间轴。
- public/audio/与audio_original/：{len(t['scenes'])}份最终WAV与{parts}份可离线复用MP3。
- docs/与references/：目录、速查、题答、总结、资料、语音配置和验收记录。

## 安装与离线重渲染

需要Python、FFmpeg/ffprobe；依赖见requirements.lock.txt。字体使用Windows Microsoft YaHei与Consolas，跨系统时修改scripts/draw.py和diagrams.py中的字体路径。已有执行数据和声音可直接用于重渲染。

```powershell
python -m pip install -r requirements.lock.txt
python scripts/layout_review.py
python scripts/check_original_speed.py
python scripts/check.py
python scripts/preview.py
python scripts/check_preview.py
python scripts/render.py --workers 4
python scripts/check.py --final
python scripts/check_audio_placement.py
python scripts/document.py
python scripts/delivery_report.py
python scripts/package.py
```

渲染按章缓存，中断后重复相同命令继续。修改绘图后会使用新的缓存标识。timeline.py --layout仅用于排版估算，正式渲染要求实测时间轴。

## 修改内容

编辑content/chapters_a.py至chapters_d.py，运行build_course.py。右侧整页总结在content/page_summaries.py编辑。代码讲解对象和对应执行状态在content/sync_plan.py维护；选择的是实际讲解短语，而后由最终声音定位时间。

修改代码后安装NASM 3.02，把nasm.exe加入PATH，再运行verify_math.py，检查机器码与预期输出。修改旁白后使用自己的环境变量DASHSCOPE_API_KEY和SFM_WORKSPACE_ID运行voice.py；随后运行prepare_audio.py、timeline.py、原速检查、布局检查与试片。prepare_audio.py需要本地Whisper base权重，默认路径为用户目录.cache/whisper/base.pt。

`.env.example`仅列出变量名。生成新声音前阅读docs/百炼语音配置说明.md并检查服务权限与额度。已有声音离线复用。真实API Key与Workspace ID保留在自己的本地环境中。

## 检查与交付

验收覆盖全部页面、代码高亮、执行状态、每个练习与答案，另有90秒试片、最终编码帧抽样、音轨位置匹配、章节检查及全片解码。次数与文件摘要见docs/验收记录.md。声音位置匹配与抽样ASR各有明确覆盖范围。

工程使用白名单打包，声音元数据只留缓存复用字段。文件包含已有声音、源文件、机器码、执行与对齐资料；字体、权重、依赖、账号加载器、请求标识、临时日志及大批渲染帧存于本地制作环境。本项目附MIT许可。
'''
 (ROOT/'README.md').write_text(readme,encoding='utf8')
 for src,name in [(ROOT/'README.md','制作与使用说明.md'),(ROOT/'content/完整讲稿.md','完整讲稿.md'),(ROOT/'references/参考资料.md','参考资料.md'),*[(ROOT/'docs'/n,n) for n in ['章节目录.txt','知识点定位.md','汇编语言基础速查.md','十章练习与答案.md','旁白讲稿.md','逐页总结.md','讲稿语言自检.md']]]:shutil.copy2(src,DEL/name)
 draw.init(t);draw.render(t['scenes'][0],0).save(DEL/'汇编语言_知识地图.png');print('DOCUMENTATION_READY',flush=True)
if __name__=='__main__':main()
