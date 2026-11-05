"""Publish source-free student materials; measured chapter times are added when ready."""
import json,pathlib,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def main():
 c=load(ROOT/'public/course.json');coverage=load(ROOT/'build/coverage.json');DEL.mkdir(parents=True,exist_ok=True);scenes=[s for ch in c['chapters'] for s in ch['scenes']];beats=sum(len(s['beats']) for s in scenes)
 timeline=load(ROOT/'public/timeline.json') if (ROOT/'public/timeline.json').exists() else {};measured=timeline.get('scope')=='complete' and len(timeline.get('scenes',[]))==len(scenes)
 times={s['id']:s['startFrame']/30 for s in timeline.get('scenes',[])} if measured else {}
 def stamp(seconds):
  h,seconds=divmod(int(seconds),3600);m,seconds=divmod(seconds,60);return f'{h:02}:{m:02}:{seconds:02}'
 outlines=['# 章节大纲与知识点定位','',('完整成片时长：'+stamp(timeline['duration'])+'；以下时间依据最终声音实测。') if measured else '时间戳将在全部配音完成后按实测时间生成。',''];practice=['# 课件例题与考题详解',''];summary=['# 逐页复习总结',''];worked=0
 for ch in c['chapters']:
  outlines+=['## '+ch['title'],''];summary+=['## '+ch['title'],'']
  for s in ch['scenes']:
   outlines+=['- '+(stamp(times[s['id']])+' ' if measured else '')+s['title']+('（例题解析）' if s['kind']=='worked' else '')]
   summary+=['### '+s['title'],'']+['- '+x for x in s['points']]+['']
   if s['kind']=='worked':
    worked+=1;practice+=['## '+ch['title']+' · '+s['title'],'']
    if s.get('prompt'):practice+=['题设：','']+['- '+str(p) for p in s['prompt']]+['']
    practice+=['讲解与推导：','']+[line for b in s['beats'] for line in [b['text'],'']]
    if s.get('answer'):practice+=['结论：','']+['- '+str(x) for x in s['answer']]+['']
    practice+=['复习检查：','']+['- '+x for x in s['points']]+['']
  outlines+=['']
 missing=['# 课件中缺少完整题干的条目','','下列项目仅列教材题号，或原图中题干不完整。讲解以课件实际给出的条件与解答为依据。','']
 for item in coverage['missingQuestionStems']:
  missing+=['```json',json.dumps(item,ensure_ascii=False,indent=2),'```','']
 corrections=['# 课件技术更正与说明','','以下记录只使用中性页号，便于核对更正位置。视频中相应页面采用准确步骤卡或明确的模型条件。','']
 for item in coverage['corrections']:corrections+=['```json',json.dumps(item,ensure_ascii=False,indent=2),'```','']
 ledger=['# 课件覆盖对照','','原始资料共920页，每页均已关联实际讲解场景、合并讲解或明确排除理由。源文件采用中性编号；行政与身份内容不进入成片。','','|中性页号|处理|场景|说明|','|---|---|---|---|']
 for page,items in sorted(coverage['items'].items()):
  for item in items:ledger+=['|'+page+'|'+item['status']+'|'+', '.join(item.get('sceneIds',[]))+'|'+item.get('reason','').replace('|','／')+'|']
 for name,lines in [('章节大纲.md',outlines),('课件例题与考题详解.md',practice),('逐页复习总结.md',summary),('缺失题干清单.md',missing),('课件技术更正.md',corrections),('课件覆盖对照.md',ledger)]:
  text='\n'.join(lines)+'\n';(ROOT/'docs'/name).write_text(text,encoding='utf8');(DEL/name).write_text(text,encoding='utf8')
 shutil.copy2(ROOT/'docs/完整讲稿.md',DEL/'完整讲稿.md')
 readme=f'''# 计算机组成原理课件精讲

以用户提供的13份课件、920个原始页面为材料，整理为10章、{len(scenes)}个讲解场景、{beats}段旁白。课程时长以完整讲解为准，最终按实测声音生成。无底部字幕、无背景音乐。

逐页覆盖表保留重复内容的合并关系、知识点和题目所在场景。行政安排、学校和个人身份信息、无技术必要的署名页排除。原始文件名和原始PPT/PDF留在本地私有缓存，交付只收集中性编号的技术页面与重新编写的讲解。

## 课程顺序

1. 计算机系统、性能与发展
2. 数据表示与校验
3. 浮点数表示
4. 计算机运算方法
5. 系统总线
6. 存储系统
7. 输入输出系统
8. 指令系统
9. CPU与流水线
10. 控制单元与时序

## 讲解与画面

每个场景以图、表、公式或原题为中心，按条件、过程和结论展开。右侧保留4条具体总结。含身份信息、题干照片不完整或公式有误的原图，使用中性步骤卡替代。课件中的旧硬件表格与排行榜按其历史年份和版本解释。

1920×1080深色画框，保留原课件技术图与表格细节。需要时按已编写的矩形强调或放大；讲解页面随对应语音单元切换，静音期间继续保持。静态片段使用事件驱动VFR，时间点在30fps网格。

语音设置为百炼qwen-audio-3.1-tts-plus、许南川xunanchuan_v3.1、原生rate 1.05。后期tempo 1.0，句号额外增加0.1秒，逗号维持原停顿。所有成功片段按文本、模型、声音和设置保存缓存。

## 学习资料

- docs/完整讲稿.md：全部讲解正文。
- docs/课件例题与考题详解.md：{worked}个例题解析场景，包含计算条件、推导与结论。
- docs/逐页复习总结.md：全部场景的4条复习要点。
- docs/课件覆盖对照.md：920页材料的场景关联与处理说明。
- docs/课件技术更正.md：原课件笔误、模型条件和程序语义更正。
- docs/缺失题干清单.md：只有题号或题干照片缺失的条目。

## 工程结构

content/module_*.json包含可编辑讲稿、题解、总结、画面关联和覆盖记录；public/slides为实际用到的去身份技术图；public/audio_original为原配音缓存，public/audio为处理后的逐段及逐场景WAV；scripts包含声音、画面、时间轴和分章渲染工具。

工程包包含已完成的最终逐场景声音。安装requirements.txt中的依赖并准备FFmpeg/FFprobe后，可依次运行python scripts/timeline.py、python scripts/render.py、python scripts/verify_final.py，离线重建无字幕视频。Windows绘制使用已安装的微软雅黑字体，字体文件不随工程分发；其他系统先调整draw.py中的字体路径。

修改讲稿后，可运行python scripts/build_course.py --public-only，用包内匿名课件图和中性页数清单重建课程。再运行voice.py补配音、prepare_audio.py处理声音、timeline.py生成时间轴，最后运行render.py。各章按内容、声音、图像和字体指纹缓存，重复运行复用成功结果。生成新声音需要自己的账号环境变量DASHSCOPE_API_KEY、SFM_WORKSPACE_ID，现有声音离线复用；配置方法见docs/百炼语音配置说明.md。

content/pause_overrides.json记录一处服务返回词跨越句号的边界修订。它绑定原始声音哈希，并在实测静音区间中点增加约定停顿；保留原语速和全部正文。验收记录绑定本次成片、课程与时间轴哈希。

build/voice-resume-state.json记录本地配音续跑状态。用户要求暂停时，在线配音与自动重试保持停止，等明确恢复后继续。原账户加载器及账户值不属于公开工程。

## 数值与隐私检查

verify_data_examples.py验证编码、浮点、海明与CRC给定模型；verify_arithmetic.py独立核算补码、乘除和舍入；verify_hardware_content.py核算地址、缓存、中断和流水等例题。具体检查范围以各报告为准。

屏幕文字与公式检查使用真实字体渲染，原图图片另做视觉身份审查。最终视频的媒体、音轨和章节检查在完整编码后记录；配音尚未完成时不生成整片通过结论。

工程中的制作代码与重新编写的讲解可按附带许可使用；原课件技术图来自用户提供的材料，其原有权利归属保持。
'''
 (ROOT/'README.md').write_text(readme,encoding='utf8');shutil.copy2(ROOT/'README.md',DEL/'制作说明.md');print('STUDY_MATERIALS_READY',worked,'worked scenes',flush=True)
if __name__=='__main__':main()
