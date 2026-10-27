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
    pages=len(t['scenes']);units=sum(len(s['parts']) for s in t['scenes']);motions=sum(len(p['moves']) for s in t['scenes'] for p in s['parts'])
    index=['# 逐页考点定位','','以下使用正式时间轴的原始起点。','','| 章节 | 考点 | 视频起点 |','| --- | --- | --- |']
    notes=['# 考点与协议速查','','按实际教学顺序整理；概念、条件和例题数值一起使用。','']
    questions=['# 十章练习与答案','','每章一道原创随堂练习，题目之后保留4秒思考，答案另页。','','## 题目',''];answers=['## 参考答案','']
    for c in t['chapters']:
        notes+=['## '+c['title'],'']
        for i,s in enumerate(c['scenes']):
            when=stamp(s['startFrame']/30);index.append(f"| {c['title']} | {s['title']} | {when} |")
            if s['kind']=='lesson':notes+=['### '+s['title'],'','视频起点：'+when,'']+rows(s)+['检查：'+'；'.join(dict.fromkeys(n for p in s['parts'] for n in p['notes'])),'']
            if s['kind']=='question':
                questions+=['### '+c['key']+' '+c['title'],'','题目：'+when,'']+rows(s)+[p['text'] for p in s['parts']]+['']
                a=c['scenes'][i+1];assert a['kind']=='answer';answers+=['### '+c['key']+' '+c['title'],'','答案：'+stamp(a['startFrame']/30),'']+rows(a)+[p['text'] for p in a['parts']]+['']
    for name,lines in [('考点定位.md',index),('考点与协议速查.md',notes),('十章练习与答案.md',questions+answers)]:
        (ROOT/'docs'/name).write_text('\n'.join(lines)+'\n',encoding='utf8')
    checklist='''# 计算机网络基础题解题步骤

1. **分层与封装**：先数层数再加首部。TCP/IP四层是应用、传输、网际、网络接口；每下一层多一个首部。MAC地址逐段链路有效，IP地址端到端不变，端口号区分应用进程。看到“时延”先分清发送、传播、处理、排队，带宽只影响发送时延，传播时延只看距离和介质。
2. **物理层**：比特率=波特率×每码元比特数，16种码元对应4比特。奈氏准则用理想低通信道，香农定理含噪声，二者不要混用。信道复用分清频分、时分、波分、码分；电路交换先建立连接，分组交换才逐跳存储转发。
3. **数据链路层**：以太网帧=目的MAC6+源MAC6+类型2+数据46～1500+FCS4，最小帧64B、最大1518B。交换机每端口一个冲突域、不分割广播域；集线器既不分冲突域也不分广播域。自学习看源MAC登记、按目的MAC转发、未知目的则泛洪。
4. **IPv4与子网**：写清网络位和主机位。子网掩码连续1的个数就是前缀长度。/26的块大小是64。每个子网：网络地址、广播地址、可用范围=网络+1到广播-1。CIDR聚合先把各网络写成二进制，找共同前缀，聚合后地址必须是偶数块起点并保留原起点。
5. **IP数据报与分片**：片偏移以8字节为单位，除最后一片外每片数据长度必须是8的倍数。4000字节数据报（20字节首部、3980字节数据）走MTU1500时分成1480+1480+1020，片偏移0、185、370，MF依次1、1、0。TTL每经过一个路由器减1。
6. **路由与转发**：按目的IP查路由表，全部匹配项中取前缀最长者；没有匹配才用默认路由。转发时IP地址不变，MAC地址逐跳重写，TTL递减。RIP是距离向量（最大15跳）、OSPF是链路状态（Dijkstra）、BGP是AS间路径向量。
7. **TCP连接**：三次握手确认双方收发能力：SYN、SYN+ACK、ACK，序号和确认号要互相对应。四次挥手因为TCP半关闭，两个方向分别关闭；主动关闭方进入TIME_WAIT等2MSL。端口0～1023是知名端口：HTTP80、HTTPS443、DNS53、DHCP67/68、FTP21/20、SMTP25、POP3110、SSH22。
8. **TCP可靠传输**：确认号表示期望收到的下一个字节。超时重传的RTO由RTT估计；窗口计算先定位当前发送窗口区间，再把已发未确认和可新发分开。接收窗口rwnd限制发送窗口上限，窗口为0时发送方要用窗口探测。
9. **拥塞控制**：慢启动每轮RTT翻倍，到ssthresh转拥塞避免每轮加1；超时则ssthresh减半、cwnd回1并重新慢启动；收到三个重复ACK走快重传+快恢复，ssthresh和cwnd都设为原cwnd的一半。发送窗口=min(cwnd,rwnd)。
10. **应用层与综合**：DNS先把域名解析成IP（递归与迭代分清），再TCP握手，再发HTTP请求。首字节时间≈DNS+握手+请求，题设RTT=20ms时约3×20=60ms。HTTPS在HTTP基础上增加TLS握手与加密。DHCP是Discover-Offer-Request-ACK四步；FTP控制连接21、数据连接20。

建议先重做10道随堂题，再按课程与往年试题补齐范围。本文用于基础框架与常见题型，不替代完整教材。
'''
    (ROOT/'docs/解题步骤清单.md').write_text(checklist,encoding='utf8')
    readme=f'''# 一小时学完计算机网络

面向零基础大学生，侧重概念辨析、协议过程、计算例题和易错点。正式成片 **{stamp(t['duration'])}**，10章、{pages}页、{units}段讲解、10道原创随堂练习。按分层模型、物理层、数据链路层、网络层、路由、传输层、可靠传输、拥塞控制、应用层形成完整学习顺序。范围与使用条件见[参考资料](references/参考资料.md)。

## 声音与画面

- 旁白使用 **阿里云百炼 qwen-audio-3.1-tts-plus＋许南川（xunanchuan_v3.1）**，用户指定原生合成 rate=1.05，后期 tempo=1.0，不再二次变速。原讲稿、题例、布局及持续高亮机制沿用原版，新音频处理后重新生成全部时间轴。
- 每个句号处额外增加0.1秒静音，逗号保持原样。先处理停顿，再生成画面时间轴。原始语音样本保留。
- 1920×1080，H.264/AAC，无底部字幕、无背景音乐。30fps时间网格；动作逐格渲染，静态画面VFR保持，非全片恒定30fps。
- 开头直接呈现十章知识地图。持续高亮保持到下段实际讲解开始；动画按教师编写的唯一短语触发，终态保留。{motions}段连续动画，共{t['continuousMotionSeconds']:.2f}秒实际变化。
- 13种原创网络图示：分层封装、时延构成、编码与码元、以太网帧、交换机自学习、子网划分、IP首部与分片、NAT转换、最长前缀匹配、三次握手/四次挥手、滑动窗口、拥塞窗口、DNS与HTTP访问链。

## 学习材料

[完整讲稿](content/完整讲稿.md)、[考点定位](docs/考点定位.md)、[考点与协议速查](docs/考点与协议速查.md)、[十章练习答案](docs/十章练习与答案.md)、[解题步骤](docs/解题步骤清单.md)。数值例题与图示数据源在scripts/examples.py，固定期望核对在scripts/verify_examples.py。

## 复用已有音频离线重渲染

需要Python、FFmpeg/FFprobe。直接依赖见requirements.txt，本次环境版本见requirements.lock.txt。中文字体使用Windows Microsoft YaHei；字体不打包。重新配音使用百炼，需要网络与用户自己的授权账号；复用现有音频不需要账号或网络。

工程包已包含最终逐页WAV和时间轴，只重新导出画面时可直接运行scripts/render.py。下列完整重建流程中的prepare_audio.py还需要本机已有Whisper base模型，默认位置为用户目录的.cache/whisper/base.pt；模型权重不随工程打包。仅重新导出已有WAV与时间轴时不需要加载这个模型。

```powershell
python -m pip install -r requirements.lock.txt
python scripts/build_course.py
python scripts/verify_examples.py
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
python scripts/document.py
python scripts/delivery_report.py
python scripts/package.py
```

成片输出到工程同级的交付/计算机网络一小时_百炼3.1Plus许南川。timeline.py --layout只用于内部排版，正式渲染拒绝合成时长。正式导出前要不带--layout重建实测时间轴。render.py --chapter 01可只渲染一章；按输入指纹缓存，可失败后继续。

## 修改内容或拓展

content/chapters_a.py至chapters_d.py是内容源；author.py定义讲解行与旁白。focus人工指定相关行，show控制逐步显示。高亮不会在句末清空；图示kind/phase指定含义。moves中的anchor必须在本段唯一，seconds是最长动画时间，遇下个动作则衔接。

prepare_audio.py直接解码原始MP3，在句号附近低能量处插入0.1秒；原语音样本不删不改。timeline.py用本地Whisper已知文本对齐把动作映射到加入停顿后的实际PCM时间。修改旁白后必须更新相应配音、对齐、时间轴和验收，不能沿用旧时间。动态图示实现在scripts/diagrams.py。

## 生成新配音

使用百炼3.1 Plus＋许南川，音色固定在scripts/audio.py，原生合成速率1.05固定在scripts/voice.py。先运行 python scripts/voice.py --test 试听，再运行 python scripts/voice.py；成功片段按指纹复用，可在中断后续跑。

重新调用前先确认模型权限、额度和价格，在进程环境变量DASHSCOPE_API_KEY、SFM_WORKSPACE_ID中设置自己的配置；缺少配置时仅允许复用已有缓存，不会自动改用其他声音。申请步骤与免费额度注意事项见[百炼语音配置说明](docs/百炼语音配置说明.md)。不要提交真实密钥。全部配音完成后依次运行 prepare_audio.py、timeline.py 及后续验收。改语速前先告知并取得同意；时长变化优先改内容。

## 验收与安全

verify_examples.py对子网、分片、时延、窗口、拥塞窗口、序号与端口等固定数值做独立复算。layout_review.py渲染全部{units}个讲解状态和全部{motions}段动作的四分位。check.py核对音频、实际起点、短语锚点、逐格事件、持续高亮和题答分离；--final再检查编码画面、章节、动态变化和全片解码。check_audio_placement.py逐段与最终AAC位置核对。check_original_speed.py独立解码原始MP3并精确重建最终WAV，仅允许约定静音插入。

自动检查与人工抽看的实际范围见docs/验收记录.md；不声称每分钟均已人工听看，也不把波形合成位置校验当作每个词的对齐证明。

package.py采用文件白名单、精简语音元数据、密钥与业务空间模式扫描、ZIP完整性检查、离线缓存及语音重建验证。真实API Key、Workspace ID、私有账号加载器、原始服务响应、依赖及渲染缓存不会进入工程包。本次不自动上传GitHub。
'''
    (ROOT/'README.md').write_text(readme,encoding='utf8')
    deps=['requests','numpy','scipy','Pillow','matplotlib','openai-whisper','torch']
    lines=[]
    for name in deps:
        try:lines.append(name+'=='+importlib.metadata.version(name))
        except importlib.metadata.PackageNotFoundError:continue
    (ROOT/'requirements.lock.txt').write_text('\n'.join(lines)+'\n',encoding='utf8')
    for name in ['考点定位.md','考点与协议速查.md','十章练习与答案.md','解题步骤清单.md']:shutil.copy2(ROOT/'docs'/name,DEL/name)
    shutil.copy2(ROOT/'README.md',DEL/'制作与使用说明.md');shutil.copy2(ROOT/'content/完整讲稿.md',DEL/'完整讲稿.md');shutil.copy2(ROOT/'references/参考资料.md',DEL/'参考资料.md')
    for name in ['章节目录.txt','逐页知识点目录.txt']:shutil.copy2(DEL/name,ROOT/'docs'/name)
    draw.init(t);draw.render(t['scenes'][0],0).save(DEL/'计算机网络_知识地图.png');print('DOCUMENTATION_READY',flush=True)

if __name__=='__main__':main()
