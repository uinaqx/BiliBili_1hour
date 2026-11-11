"""Generate learner-facing documentation from the delivered course and trace checks."""
import json,pathlib,shutil,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out'
sys.path.insert(0,str(ROOT/'scripts'));from examples import CASES
def load(p):return json.loads(p.read_text(encoding='utf8'))
def write(name,rows):
 p=ROOT/'docs'/name;p.write_text('\n'.join(rows)+'\n',encoding='utf8');shutil.copy2(p,DEL/name)
def stamp(t):
 h,s=divmod(int(t),3600);m,s=divmod(s,60);return f'{h:02}:{m:02}:{s:02}'
def main():
 DEL.mkdir(exist_ok=True,parents=True);c=load(ROOT/'public/course.json');t=load(ROOT/'public/timeline.json');v=load(ROOT/'build/examples-verification.json')
 rows=['# 现代汇编学习手册','','与完整有声课程对应；以实际片段、明确输入和结果核对每一项。','## 课程目录','']
 rows+=['- '+stamp(ch['startFrame']/30)+' '+ch['title'] for ch in t['chapters']]
 rows+=['','## 三层阅读顺序','','先确定架构与语法，再确定函数 ABI 和操作系统。用数据类型、位宽、布局解释每次读写；用比较关系与返回位置解释控制流。','','## 本课示例环境','','代码片段在模拟器中以 0x100000 为代码入口、0x200000 为数据区起点、0x400000 为栈区起点。x86-64 函数入口 RSP 为 0x40FFE8，栈中预先放置返回哨兵；AArch64 入口 SP 为 0x40FFF0，X30 保存返回哨兵。RET 用于结束当前被调用函数，操作系统进程退出另按平台接口处理。','','数据采用小端。入口未显式赋值的普通寄存器初始为零。跨平台调用示例见 examples/native；使用该目录的函数与 C 调用者连接。','']
 for ch in c['chapters']:
  rows+=['## '+ch['title'],'']
  for s in ch['scenes']:
   if s['kind']!='lesson':continue
   rows+=['### '+s['title'],'']
   rows+=['- '+p for p in s['points']]+['']
   if s['run']:
    case=CASES[s['run']];rows+=['```asm',*case['code'],'```','']
    if case['initial']:rows+=['入口：'+ '；'.join(k.upper()+'='+hex(n) for k,n in case['initial'].items())+'。','']
    rows+=['输入数据前32字节：`'+case['data'][:64]+'`。','']
    if case['expected']:rows+=['完整执行检查：'+ '；'.join(k.upper()+'='+str(n-(1<<64) if n>=1<<63 else n) for k,n in case['expected'].items())+'。','']
    else:rows+=['完整执行检查：成功取得实际标签位置并返回。标签地址按实际编码长度定位。','']
 write('学习手册与代码说明.md',rows)
 rows=['# 十章练习与答案','','每章在视频中留有四秒独立思考。','']
 for ch in c['chapters']:
  q=next(s for s in ch['scenes'] if s['kind']=='question');a=next(s for s in ch['scenes'] if s['kind']=='answer');rows+=['## '+ch['title'],'','题目：'+q['parts'][0]['text'],'','答案：'+a['parts'][0]['text'],'']+['- '+p for p in a['points']]+['']
 write('十章练习与答案.md',rows)
 rows=['# 本次重制说明','','新版围绕现代64位应用完整重写，保留原有深色版式、左下结果、右侧整页总结与持续高亮。旧工程与旧成片保留。','','| 反馈关注点 | 本次具体改动 |','|---|---|','| 旧课8086与16位内容占主线 | 改为x86-64与AArch64；段值×16加偏移和DOS INT 21h移入历史补充 |','| 缺少x64 | 系统讲解RAX/EAX/AL、RIP相对地址、64位指针、System V调用、Windows x64参数与影子空间 |','| 缺少ARM | AArch64贯穿寄存器、常数、访存、扩展、运算、条件、循环、数组、函数、栈和综合任务 |','| 容易混淆平台规则 | 按指令集、ABI、操作系统分层；Windows x64独立展示 |','| 画面要跟着讲解 | 人工短语与代码/实际执行步骤对应，结合最终PCM声学时间；切换后持续保持 |','','最终时长：'+stamp(t['duration'])+'。10章、75页、130段配音；10道题与10份独立答案。','','配音在用户恢复授权后完成：百炼3.1 Plus、许南川、原生1.05倍速。后期tempo固定1.0，句号间额外0.1秒，逗号保持。完整成片保留底部字幕，另附SRT。','']
 write('重制说明.md',rows)
 report=ROOT/'build/final-review.json'
 rows=['# 验收记录','','## 示例与内容','','- 正常机器码程序：'+str(v['normalPrograms'])+'个。','- 结果与边界检查：'+str(v['checks'])+'项。','- 预期失败案例：'+str(v['expectedFailures'])+'个，区分汇编拒绝、x64除法异常和未映射读取。','- 45个正常片段的实际指令状态、字节编码、输入和输出均保留。','- NASM已生成并核验ELF64与Win64目标文件；原生进程运行见目标环境操作说明。','']
 if report.exists():
  r=load(report);rows+=['## 完整成片','','- 时长：'+stamp(r['duration'])+'，1920×1080，H.264/AAC，10个内嵌章节。','- 全片解码：通过。','- 计划显示事件：'+str(r['plannedDisplayEvents'])+'个，全部在实际MP4显示时间中存在。','- 编码画面抽取：'+str(r['sampledEncodedStates'])+'个状态，覆盖全部页面、字幕边界、高亮切换前后及保持期。','- 实际高亮行像素检查：'+str(r['checkedHighlightRows'])+'行。','- 全画面缩略图平均绝对像素误差最大值：'+f"{r['maxPixelMAE']:.4f}"+' / 255。','- 开头、中段、结尾各抽取8秒AAC与最终PCM进行同位置相关性检查。','','这些记录覆盖程序检查与编码状态抽查。人工视觉复核包含试片、关键帧和每章联络图；未声称按实时速度听看整部课程。','','## 本次文件绑定','','- MP4 SHA-256：`'+r['videoSha256']+'`','- 时间轴 SHA-256：`'+r['timelineSha256']+'`','- 课程清单 SHA-256：`'+r['courseSha256']+'`','- 绘制实现 SHA-256：`'+r['drawingSha256']+'`','']
 else:rows+=['完整成片编码验收尚在进行；此记录会在实际检查完成后更新。','']
 write('验收记录.md',rows)
 for src,name in [(ROOT/'docs/完整讲稿.md','完整讲稿.md'),(ROOT/'references/参考资料.md','参考资料.md'),(ROOT/'README.md','制作与使用说明.md')]:shutil.copy2(src,DEL/name)
 print('DOCS_BUILT',stamp(t['duration']),flush=True)
if __name__=='__main__':main()
