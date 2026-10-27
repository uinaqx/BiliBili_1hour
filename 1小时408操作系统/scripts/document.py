"""Measured chapter index, source-derived study notes and editable-project instructions."""
import importlib.metadata,json,pathlib,shutil
import draw
ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out'

def stamp(t):
    h,s=divmod(int(t),3600);m,s=divmod(s,60);return f'{h:02}:{m:02}:{s:02}'

def rows(s):
    out=[]
    for r in s['rows']:out+=['**'+r['label']+'**','',f"$${r['math']}$$" if r['math'] else r['text'],'']
    return out

def main():
    t=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf8'));assert t['scope']=='complete-course';DEL.mkdir(exist_ok=True)
    index=['# 逐页考点定位','','以下使用正式时间轴的原始起点。','','| 章节 | 考点 | 视频起点 |','| --- | --- | --- |']
    notes=['# 考点与算法速查','','按实际教学顺序整理；公式和算法必须与题设一起使用。','']
    questions=['# 十章练习与答案','','每章一道原创随堂题，题目之后保留4秒思考，答案另页。','','## 题目',''];answers=['## 参考答案','']
    for c in t['chapters']:
        notes+=['## '+c['title'],'']
        for i,s in enumerate(c['scenes']):
            when=stamp(s['startFrame']/30);index.append(f"| {c['title']} | {s['title']} | {when} |")
            if s['kind']=='lesson':notes+=['### '+s['title'],'','视频起点：'+when,'']+rows(s)+['检查：'+'；'.join(dict.fromkeys(n for p in s['parts'] for n in p['notes'])),'']
            if s['kind']=='question':
                questions+=['### '+c['key']+' '+c['title'],'','题目：'+when,'']+rows(s)+[p['text'] for p in s['parts']]+['']
                a=c['scenes'][i+1];assert a['kind']=='answer';answers+=['### '+c['key']+' '+c['title'],'','答案：'+stamp(a['startFrame']/30),'']+rows(a)+[p['text'] for p in a['parts']]+['']
    for name,lines in [('考点定位.md',index),('考点与算法速查.md',notes),('十章练习与答案.md',questions+answers)]:
        (ROOT/'docs'/name).write_text('\n'.join(lines)+'\n',encoding='utf8')
    checklist='''# 408操作系统基础题解题步骤

1. **概述与运行机制**：先区分并发与并行、态转换与进程切换、普通函数与系统调用。事件按来源分外部中断与内部异常。实时看截止时间，不能只看平均运行速度。
2. **进程与线程**：就绪只差处理器，阻塞还差事件。事件完成先回就绪；时间片耗尽通常也回就绪。区分PCB与代码，区分同进程共享堆与线程私有栈。线程阻塞影响要结合映射模型。
3. **调度**：先抄到达、服务、时间片、抢占和切换开销。每次只在已到达且就绪者中选。完成后再算周转=完成−到达，带权周转=周转/服务；等待时间按题设扣除非等待部分。HRRN在同一当前时刻比较响应比。RR新到达与片尾入队的先后顺序读题设。
4. **同步互斥**：先确定资源初值和前驱关系，再写PV。互斥量通常初值1，前驱通知初值0；empty=N、full=0。先等待资源条件，再申请互斥锁，避免持有锁时等别人才能产生的资源。不要只交换两个P却忘写对应V。
5. **死锁**：找互斥、不可剥夺、占有并等待、循环等待。预防是破坏必要条件，避免是分配前查安全。Need=Max−Allocation；先查Request≤Need和Available，再试分配并检查安全序列。每完成一个进程，Work只加回原Allocation。不安全不等于此刻已经死锁。
6. **内存地址**：统一字节/字/页的单位。页号=逻辑地址整除页大小，页内偏移取余；查页表换页框后，物理地址=页框×页大小+原偏移。TLB未命中先查页表，不等于缺页。分段先查段长，合法后基址加偏移。
7. **页面置换**：先写页框数与初始状态。每次访问先判断命中，缺页才计数。FIFO命中不调整调入次序；LRU命中更新使用次序；OPT看将来。Clock访问位与指针一起更新。平均耗时先把毫秒和纳秒统一，确认缺页耗时是否已含普通访存。
8. **文件系统**：文件内偏移先换算逻辑块与块内偏移，再讨论分配。索引项数=块字节数/指针字节数；一级、二级索引分别展开。容量题分清数据块与索引元数据。目录、FCB/inode、系统打开表和进程描述符是不同层。
9. **磁盘与外存**：先画起点、边界、方向、请求。FCFS按到达；SSTF每次重算距离；SCAN到物理端点，LOOK到最远请求。循环算法确认回跳计入与否。用相邻磁道差的绝对值求和，不漏回程。位、字节、盘块最后逐级向上取整。
10. **I/O综合**：区分驱动软件与控制器硬件，区分轮询、中断和DMA。DMA减轻逐字搬运，初始化与完成仍可能需要CPU。缓冲题先区分稳定周期与有限批次总时间。综合题按“请求—等待—完成—就绪—调度”追踪，不把设备完成直接写成正在运行。

建议先重做10道随堂题，再用报考年度大纲与往年试题补齐范围。本文用于基础框架与常见题型，不替代完整教材。
'''
    (ROOT/'docs/解题步骤清单.md').write_text(checklist,encoding='utf8')
    readme=f'''# 一小时学完408操作系统

面向第一次系统学习操作系统的大学生，侧重概念辨析、算法步骤和基础题型。正式成片 **{stamp(t['duration'])}**，10章、83页、145段讲解、10道原创随堂题。按处理机、同步死锁、内存、文件、磁盘、I/O形成完整学习顺序。范围与使用条件见[参考资料](references/参考资料.md)。

## 声音与画面

- 百炼 **qwen-audio-3.1-tts-plus＋许南川（xunanchuan_v3.1）**，用户明确选择原生合成rate=1.05。后期tempo=1.0，没有再变速。
- 每个句号处额外增加0.1秒静音，逗号保持原样。先处理停顿，再生成画面时间轴。呼吸声在文本配音中，保留原始语音样本。
- 1920×1080，H.264/AAC，无底部字幕、无背景音乐。30fps时间网格；动作逐格渲染，静态画面VFR保持，非全片恒定30fps。
- 开头直接呈现十章知识地图。持续高亮保持到下段实际讲解开始；动作按教师编写的唯一短语触发，终态保留。106段连续动画，共{t['continuousMotionSeconds']:.2f}秒实际变化。
- 可视化包含进程状态、甘特图、信号量、银行家安全序列、页表与地址、置换过程、文件索引、磁盘寻道与缓冲时间线。

## 学习材料

[完整讲稿](content/完整讲稿.md)、[考点定位](docs/考点定位.md)、[考点与算法速查](docs/考点与算法速查.md)、[十章练习答案](docs/十章练习与答案.md)、[解题步骤](docs/解题步骤清单.md)。数值例题与图示数据源在scripts/examples.py，固定期望核对在verify_examples.py。

## 复用已有音频离线重渲染

需要Python、FFmpeg/FFprobe。直接依赖见requirements.txt，本次环境版本见requirements.lock.txt。中文字体使用Windows Microsoft YaHei，公式使用Matplotlib STIX；字体不打包。其他平台须先替换draw.py、diagrams.py及QA脚本中的字体路径，再检查全部排版。

工程包保留83份最终逐页WAV与时间信息、145份原生1.05配音及精简元数据、145份本地已知文本对齐缓存。复用这些音频不需要账号或网络。

```powershell
python -m pip install -r requirements.lock.txt
python scripts/build_course.py
python scripts/verify_examples.py
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

成片输出到工程同级的交付/408操作系统一小时。timeline.py --layout只用于内部排版，正式渲染拒绝合成时长。正式导出前要不带--layout重建实测时间轴。render.py --chapter 01可只渲染一章；按输入指纹缓存，可失败后继续。

## 修改内容或拓展

content/chapters_a.py至chapters_e.py是内容源；author.py定义讲解行与旁白，cues.py细化动作锚点。focus人工指定相关行，show控制逐步显示。高亮不会在句末清空；图示kind/phase指定含义。moves中的anchor必须在本段唯一，seconds是最长动画时间，遇下个动作则衔接。

prepare_audio.py直接解码原始MP3，在句号附近低能量处插入0.1秒；原语音样本不删不改。timeline.py用本地Whisper已知文本对齐把动作映射到加入停顿后的实际PCM时间。修改旁白后必须更新相应配音、对齐、时间轴和验收，不能沿用旧时间。动态图示实现在scripts/diagrams.py。

## 生成新配音

使用自己的百炼北京地域账号，先确认模型开通、权限、额度和价格。完整步骤见[百炼语音配置与免费额度检查](docs/百炼语音配置说明.md)。在环境变量DASHSCOPE_API_KEY、SFM_WORKSPACE_ID中设置自己的配置；.env.example只列变量名，脚本不会自动读取.env。

先运行python scripts/voice.py --test，再运行python scripts/voice.py。当前模型、声音、指令及rate=1.05固定在脚本中，成功段落按指纹复用。随后运行python scripts/prepare_audio.py，首次需本地Whisper base模型（约145MB，放在用户.cache/whisper/base.pt），再生成正式时间轴。改语速前先告知并取得同意；时长变化优先改内容。

## 验收与安全

verify_examples.py有240项独立固定期望/约束检查。layout_review.py渲染145个讲解状态和全部106段动作的四分位。check.py核对音频、实际起点、短语锚点、逐格事件、持续高亮和题答分离；--final再检查编码画面、章节、动态变化和全片解码。check_audio_placement.py取145段各前后1.2秒，与最终AAC位置核对。check_original_speed.py独立解码原始MP3并精确重建最终WAV，仅允许约定静音插入。

自动检查与人工抽看的实际范围见docs/验收记录.md；不声称每分钟均已人工听看，也不把波形合成位置校验当作每个词的对齐证明。

package.py采用文件白名单、精简语音元数据、密钥与业务空间模式扫描、ZIP完整性检查、离线缓存及语音重建验证。真实API Key、Workspace ID、私有账号加载器、原始服务响应、依赖及渲染缓存不会进入工程包。本次不自动上传GitHub。
'''
    (ROOT/'README.md').write_text(readme,encoding='utf8')
    deps=['requests','numpy','scipy','Pillow','matplotlib','sympy','openai-whisper','torch']
    (ROOT/'requirements.lock.txt').write_text('\n'.join(n+'=='+importlib.metadata.version(n) for n in deps)+'\n',encoding='utf8')
    for name in ['考点定位.md','考点与算法速查.md','十章练习与答案.md','解题步骤清单.md']:shutil.copy2(ROOT/'docs'/name,DEL/name)
    shutil.copy2(ROOT/'README.md',DEL/'制作与使用说明.md');shutil.copy2(ROOT/'content/完整讲稿.md',DEL/'完整讲稿.md');shutil.copy2(ROOT/'references/参考资料.md',DEL/'参考资料.md')
    for name in ['章节目录.txt','逐页知识点目录.txt']:shutil.copy2(DEL/name,ROOT/'docs'/name)
    draw.init(t);draw.render(t['scenes'][0],0).save(DEL/'408操作系统_知识地图.png');print('DOCUMENTATION_READY',flush=True)

if __name__=='__main__':main()
