"""Create review contact sheets and a source/teaching package (videos separate)."""
import hashlib
import json
import zipfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]

def main():
    output=ROOT/'output'
    validation=json.loads((output/'validation.json').read_text())
    if validation.get('overall')!='pass':raise RuntimeError('validation must pass before packaging')
    full=next(m for m in validation['media'] if m['file']=='course_120min_silent.mp4')
    preview=next(m for m in validation['media'] if m['file']=='silent_preview.mp4')
    status=f'''# 本轮交付状态

定位：大学计算机组成原理主干学习；代码生成图解与实验。配音按用户要求暂不处理。

## 已交付

- 11章、60镜、总计7200秒的课程时间轴；完整讲稿{validation['course']['narration_chars']}字符、60道即时自测及答案、18道课后练习及开放实验。
- 60镜离线HTML/SVG互动预览，支持播放、暂停、章节跳转、任意定位与逐状态审阅；完整阅读讲义和300条分镜阶段记录。
- 确定性教学模型：数据表示、固定位宽算术、浮点示例、Cache、CPU语义子集、流水调度、性能与I/O事件；可直接修改参数运行。
- 全长静音MP4：{full['duration']:.3f}秒，1920×1080，H.264/yuv420p，VFR关键状态保持，实际编码{full['frames']}帧，包含11章导航；显示时长不靠重复帧堆积。
- 静音样片：{preview['duration']:.3f}秒、1920×1080、恒定30fps、{preview['frames']}帧，演示LRU命中、替换与脏块写回。
- 文稿估时SRT。它是静音阅读提示，未做真实语音对齐。

## 实际验证

- 单元测试{validation['unit_tests']['run']}项通过，包括全部65536组八位加法、Cache随机读写与写回、CPU错误输入及状态轨迹、流水依赖。
- 全部60镜在4个阶段共240个状态渲染，浏览器无脚本错误；文字未超出画布和主图/侧栏边界。
- 导航、上一镜/下一镜、播放与seek确定性检查通过。
- 样片实际媒体元数据、头中尾解码通过；全长实际媒体元数据、11章、时间戳覆盖、头中尾及全片严格解码通过。
- 人工查看了代表性关键帧与样片写回画面。未声称已实时人工观看完整两小时。

## 使用与范围

直接打开output/index.html可审片。制作命令与实验示例见README。全长版采用关键状态切换与保持；逐帧过渡样片与连续时间网页单独提供，不将VFR静音版描述成逐帧插值的精剪母版。

配音、声音合成与基于语音的精确字幕对齐不属于本轮范围。所有模型的教学假设已写在总案、分镜和代码说明中；不把模型输出当真实硬件计时。
'''
    (ROOT/'docs/07_交付状态.md').write_text(status,encoding='utf-8')
    scenes=sorted((output/'review').glob('S*.png'))
    for group in range(2):
        subset=scenes[group*30:(group+1)*30]
        sheet=Image.new('RGB',(1440,3000),'#0b111c');d=ImageDraw.Draw(sheet)
        for i,p in enumerate(subset):
            im=Image.open(p);im.thumbnail((480,270));x=i%3*480;y=i//3*300
            sheet.paste(im,(x,y+25));d.text((x+8,y+5),p.stem,fill='white')
        sheet.save(output/f'contact_sheet_{group+1:02d}.jpg',quality=85)
    archive=output/'computer_organization_source.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for f in sorted(ROOT.rglob('*')):
            if not f.is_file():continue
            rel=f.relative_to(ROOT)
            if '__pycache__' in rel.parts or any(p.startswith('course-render-') for p in rel.parts):continue
            if f.suffix in ('.pyc','.mp4','.zip') or f.name in ('sum_demo','contact_sheet.jpg'):continue
            z.write(f,'computer-organization-120/'+str(rel))
    deliverables=[]
    for f in (archive,output/'course_120min_silent.mp4',output/'silent_preview.mp4'):
        if f.exists():
            digest=hashlib.file_digest(f.open('rb'),'sha256').hexdigest()
            deliverables.append(dict(name=f.name,bytes=f.stat().st_size,sha256=digest))
    (output/'deliverables.json').write_text(json.dumps(deliverables,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(deliverables,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
