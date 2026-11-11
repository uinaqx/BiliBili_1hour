"""Study materials and reproduction guide, derived from the measured timeline."""
import json,pathlib,shutil
import draw
ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out'
def stamp(t):
 h,s=divmod(int(t),3600);m,s=divmod(s,60);return f'{h:02}:{m:02}:{s:02}'
def rows(s):
 out=[]
 for r in s['rows']:out += [r['label']+'：',('$'+r['math']+'$') if r['math'] else r['text'],'']
 return out
def main():
 t=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf8'));assert t['scope']=='complete-course';DEL.mkdir(exist_ok=True)
 directory='\n'.join(stamp(c['startFrame']/30)+' '+c['title'] for c in t['chapters'])+'\n';(ROOT/'docs/章节目录.txt').write_text(directory,encoding='utf8')
 index=['# 知识点定位',''];guide=['# 离散数学基础速查','','使用条件与例题一起复习。完整解释见讲稿。',''];practice=['# 十章练习与答案','']
 for c in t['chapters']:
  guide+=['## '+c['title'],'']
  for i,s in enumerate(c['scenes']):
   time=stamp(s['startFrame']/30);index+=['- '+time+' '+s['title']]
   if s['kind']=='lesson':guide+=['### '+s['title'],'','视频起点：'+time,'']+rows(s)+['；'.join(dict.fromkeys(n for p in s['parts'] for n in p['notes'])),'']
   if s['kind']=='question':
    a=c['scenes'][i+1];assert a['kind']=='answer';practice+=['## '+c['title'],'','题目 '+time,'']+rows(s)+[s['narration'],'','答案 '+stamp(a['startFrame']/30),'']+rows(a)+[a['narration'],'']
 for name,lines in [('知识点定位.md',index),('离散数学基础速查.md',guide),('十章练习与答案.md',practice)]: (ROOT/'docs'/name).write_text('\n'.join(lines)+'\n',encoding='utf8')
 readme=f'''# 一小时学完离散数学：可视化基础

面向零基础大学生，实际成片{stamp(t['duration'])}。10章、71页、121段讲解、10道原创练习，各题讲完保留4秒思考，随后单独显示答案。

范围：命题逻辑与推理、谓词量词与证明、集合运算、关系及等价偏序、函数与对应、排列组合、递推归纳、图、树和编码、群等基本代数结构。为常见本科基础范围提供入门地图；不同学校大纲与术语应另核对。

## 画面和声音

1920×1080，深色公式与图示，右侧讲解要点。开头直接展示十章知识地图。当前公式或文字持续选中，直到下一段实际旁白起点才切换，静音与思考期不会闪灭。38段人工短语触发的动画，共{t['continuousMotionSeconds']:.2f}秒；动态段按30fps网格逐格生成，静态段VFR保持，非全片恒定30fps。无底部字幕、无音乐。

百炼qwen-audio-3.1-tts-plus、许南川xunanchuan_v3.1、原生rate=1.05，后期tempo=1.0。句号额外0.1秒，逗号不变。原始配音、句号声学边界、最终WAV和对齐缓存保留，工程可离线复用现有配音。模板主题指令曾作文字纠正；有效旧配音按原指纹复用，不伪造新生成记录。

## 文件

- content/：原创讲稿、两段一页的语义计划、题答与动画短语。
- public/course.json和timeline.json：课程与实测时间轴。
- scripts/diagrams.py：真值表、集合区域、关系、函数箭头、分组、选择树、图和树的可编辑画法。
- scripts/examples.py和verify_math.py：有限集合、真值表、关系性质、排列组合、递推、路线、生成树、编码及模4运算的独立核对。
- docs/：基础速查、练习答案、章节、知识点定位、验收记录和百炼开通说明。
- public/audio/及audio_original/：71份最终逐页WAV与121份原始MP3，元数据仅保留复用所需字段。

## 复现

需要Python、FFmpeg/ffprobe，依赖版本见requirements.lock.txt。公式使用Matplotlib MathText与STIX，不需要安装完整TeX。中文字体使用Windows Microsoft YaHei；字体不随包分发，跨系统需改字体路径并重新检查布局。

```powershell
python -m pip install -r requirements.lock.txt
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

改内容后重新运行build_course.py。若旁白文字改变，使用自己的DASHSCOPE_API_KEY与SFM_WORKSPACE_ID运行voice.py生成新语音，再运行prepare_audio.py、timeline.py及后续检查。prepare_audio.py需本地Whisper base权重，默认位于用户目录.cache/whisper/base.pt；权重不随包提供。真实账号配置只在进程环境里读取，.env.example为空。先看docs/百炼语音配置说明.md，确认模型权限、额度和费用。

已有声音可直接离线重渲染。timeline.py --layout只用于估算排版，正式render.py会拒绝该时间轴。修改声音、公式或图示后，旧验收报告失效；完成检查再运行document.py、delivery_report.py及package.py。

## 验收与边界

190项有限枚举、计算和反例检查；84条数学表达式排版；每页持续强调和38段动画中间状态；最终成片像素、旁白首尾位置、内嵌章节和完整解码分别核对。具体范围与文件哈希见验收记录。有限测试不是一般定理的形式化证明，局部音轨抽查也不等于逐分钟人工听完整片。

白名单ZIP包含可编辑工程及现有声音；API Key、Workspace ID、私有账号加载器、请求标识、原始服务响应、系统字体、模型权重和渲染缓存不打包。本轮没有自动上传GitHub。
'''
 (ROOT/'README.md').write_text(readme,encoding='utf8')
 for src,dest in [(ROOT/'README.md','制作与使用说明.md'),(ROOT/'content/完整讲稿.md','完整讲稿.md'),(ROOT/'references/参考资料.md','参考资料.md'),*[(ROOT/'docs'/n,n) for n in ['章节目录.txt','知识点定位.md','离散数学基础速查.md','十章练习与答案.md']]]:shutil.copy2(src,DEL/dest)
 draw.init(t);draw.render(t['scenes'][0],0).save(DEL/'离散数学_知识地图.png');print('DOCUMENTATION_READY',flush=True)
if __name__=='__main__':main()
