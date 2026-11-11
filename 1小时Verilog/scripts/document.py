"""Generate measured chapter index, full study guide and honest reproduction instructions."""
import hashlib,json,pathlib,shutil
import draw
ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out'
def stamp(t):
 h,s=divmod(int(t),3600);m,s=divmod(s,60);return f'{h:02}:{m:02}:{s:02}'
def main():
 t=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf8'));assert t['scope']=='complete-course';DEL.mkdir(exist_ok=True)
 chapters=['\n'.join(stamp(c['startFrame']/30)+' '+c['title'] for c in t['chapters'])+'\n'];(DEL/'章节目录.txt').write_text(chapters[0],encoding='utf8')
 notes=['# Verilog基础速查','','使用Verilog-2005设计子集；测试平台与设计分开。',''];questions=['# 十章练习与答案',''];index=['# 原片逐页知识点定位','']
 for c in t['chapters']:
  notes+=['## '+c['title'],'']
  for i,s in enumerate(c['scenes']):
   time=stamp(s['startFrame']/30);index+=['- '+time+' '+s['title']]
   if s['kind']=='lesson':
    notes+=['### '+s['title'],'','视频起点：'+time,'']
    if s['code']:notes+=['代码：'+s['codeFile'],'','```verilog','\n'.join(s['code']),'```','']
    for p in s['parts']:notes+=['；'.join(p['notes']),'']
   if s['kind']=='question':
    a=c['scenes'][i+1];assert a['kind']=='answer';questions+=['## '+c['title'],'','题目 '+time,'',s['narration'],'','答案 '+stamp(a['startFrame']/30),'',a['narration'],'']
 for name,lines in [('Verilog基础速查.md',notes),('十章练习与答案.md',questions),('考点定位.md',index)]:
  (ROOT/'docs'/name).write_text('\n'.join(lines)+'\n',encoding='utf8');shutil.copy2(ROOT/'docs'/name,DEL/name)
 shutil.copy2(DEL/'章节目录.txt',ROOT/'docs/章节目录.txt')
 readme=f'''# 一小时学完Verilog：电路、代码与仿真

面向零基础大学生，成片 **{stamp(t['duration'])}**，10章、71页、121段讲解、10道练习。逐步学习硬件描述、端口与信号、位宽与运算、组合过程、时钟与计数、阻塞与非阻塞赋值、层次化与参数、状态机、测试平台，最后完成带使能的闪灯设计。

## 声音与画面

百炼qwen-audio-3.1-tts-plus、许南川xunanchuan_v3.1，原生合成rate=1.05，后期tempo=1.0。每个句号额外0.1秒，逗号保持原样。无底部字幕、无背景音乐。1920×1080，H.264/AAC，10个内嵌章节。30fps动画网格，静止画面VFR保持，非全片恒定30fps。

深色代码区、右侧讲解要点；仿真结果位于左侧代码下方。代码字号34px，结果30px。高亮与相关多行选中持续保留，到下段实际讲解开始才切换。讲解代码最多13行；长状态机和测试平台使用明确标注的节选。右侧小波形与主区大图使用实际VCD记录，时间游标只是将仿真放慢阅读，不表示真实器件不存在传播延迟。

## 内容与学习材料

[完整讲稿](content/完整讲稿.md)、[基础速查](docs/Verilog基础速查.md)、[练习答案](docs/十章练习与答案.md)、[原片章节](docs/章节目录.txt)、[逐页定位](docs/考点定位.md)、[参考资料](references/参考资料.md)。

examples/catalog.py是原创设计和刺激源；examples/rtl/是完整设计，examples/testbenches/是自检查测试平台，examples/expected-failures/是刻意保留的错误设计。设计使用Verilog-2005子集，不混入SystemVerilog的logic、always_comb、always_ff。正常编译、预期编译失败和预期功能检查失败分别记录。

## 安装与验证仿真工具

需要Python、FFmpeg/ffprobe，以及Icarus Verilog。本次使用Icarus Verilog 13.0 stable。安装方法参考Icarus官方文档；Windows可用MSYS2 UCRT64提供的iverilog及运行依赖。用环境变量IVERILOG_BIN指向自己的bin目录，或将iverilog、vvp加入PATH。仿真器及运行库不随本工程打包，不改系统安全设置。

```powershell
python -m pip install -r requirements.lock.txt
python scripts/build_course.py
python scripts/verify_examples.py
```

verify_examples.py会重新生成RTL与测试文件，使用-g2005编译并实际运行23组正常仿真，完成204项检查，另验证语法/展开失败和功能错误。它使用相对路径和独立临时目录，以适配Windows中文路径。组合例子对照真值表，时序例子对照逐拍期望；VCD和精简波形数据保留在build/sim/与build/simulation-data.json。设计文件不使用延迟，时间单位在测试平台指定；工具的无timescale提示保留在原始检查记录中。

## 复用声音与重新导出

本地交付工程保留71份最终逐页WAV、121份原始配音和对齐缓存。已有时间轴及simulation-data.json可直接用于重渲染，不需要重新请求语音服务或重新运行仿真器。系统中文字体使用Microsoft YaHei，代码使用Consolas，字体不随工程提供；其他平台需替换字体路径并重新检查布局。

```powershell
python scripts/render.py --workers 4
python scripts/check.py --final
python scripts/check_audio_placement.py
```

修改设计后先重新验证仿真，再更新涉及的画面。修改旁白后使用自己的账号重新生成声音与对齐：

```powershell
python scripts/voice.py --test
python scripts/voice.py
python scripts/prepare_audio.py
python scripts/timeline.py
python scripts/layout_review.py
python scripts/check_original_speed.py
python scripts/check.py
python scripts/preview.py
python scripts/check_preview.py
python scripts/render.py --workers 4
python scripts/check.py --final
python scripts/check_audio_placement.py
python scripts/speech_spotcheck.py
python scripts/document.py
python scripts/delivery_report.py
python scripts/package.py
```

配音只从进程环境读取DASHSCOPE_API_KEY与SFM_WORKSPACE_ID，.env.example只有空变量名。先阅读[百炼开通与免费额度说明](docs/百炼语音配置说明.md)，确认自己的模型权限、额度和价格。prepare_audio.py需要本机Whisper base模型，默认位于用户目录.cache/whisper/base.pt；权重不打包。先完成声音与句号停顿，再映射实际时间，不按字数均分，不为了凑一小时再变速。

正式输出位于工程同级交付/Verilog一小时。timeline.py --layout仅供无声排版检查，正式导出会拒绝估算时间。先检查90秒内部试片，再继续全片。报告与实际视频、时间轴和源码哈希绑定，原片报告不代表修改后的版本通过。

## 边界与交付

本课验证RTL仿真，不声称已经完成综合、时序收敛或开发板验证。闪灯参数仅为快速仿真；实际板卡还需核对引脚、频率、位宽、输入同步与消抖。语义规则与工具参考列在references/。

工程采用文件白名单打包，语音元数据只保留复用所需字段。API Key、Workspace ID、私有账号加载器、请求标识、原始服务响应、模型权重与依赖/帧缓存不会进入工程ZIP。本轮不自动上传GitHub。源码沿用工程许可证。
'''
 (ROOT/'README.md').write_text(readme,encoding='utf8');shutil.copy2(ROOT/'README.md',DEL/'制作与使用说明.md');shutil.copy2(ROOT/'content/完整讲稿.md',DEL/'完整讲稿.md');shutil.copy2(ROOT/'references/参考资料.md',DEL/'参考资料.md')
 draw.init(t);draw.render(t['scenes'][0],0).save(DEL/'Verilog_知识地图.png');print('VERILOG_DOCUMENTATION_READY',flush=True)
if __name__=='__main__':main()
