"""Explicit, privacy-scanned editable release; credentials are never written."""
import hashlib,json,pathlib,shutil
from safe_delivery import pack,secrets_from_env
ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out'
def release(known=()):
 report=json.loads((ROOT/'build/final-verification.json').read_text(encoding='utf8'));video=DEL/'一小时学完TypeScript_零基础_无字幕.mp4'
 assert report['allPassed'] and report['videoSha256']==hashlib.sha256(video.read_bytes()).hexdigest()
 for n in ['example-verification','project-verification','layout-verification']:
  assert json.loads((ROOT/'build'/f'{n}.json').read_text(encoding='utf8'))['allPassed']
 narration=json.loads((ROOT/'public/course.json').read_text(encoding='utf8'))
 text='''# 成片交付说明

本次成片：一小时学完 TypeScript，时长 58 分 02.97 秒，1920×1080，H.264/AAC，无字幕，10 章。

高亮按老版 Rust 第二讲的视觉样式制作：浅暖色整行底色、3px 橙色左侧竖条、橙色活动行号。行间距保持 40px；无四周描边和蓝色选框。每句旁白的行号关系在讲稿源文件中人工指定，再定位到最终配音中的短语起点，高亮持续到下一处切换。

60 个原始示例全部实际编译验证，预期错误单独核验，并运行修正版；网页完整项目通过真实浏览器的新增、删除、刷新恢复、错误输入和异常存储处理检查。

实际 MP4 已逐编码状态检查高亮底色，对照页面源帧，核验章节位置、音轨样本对应及无字幕。内部试片、老版高亮参考、代表性代码和答案画面已抽查；完整一小时的人工逐句听看不在本次检查范围内。

配套资料包括完整讲稿、60 组代码及答案、全部十章时间戳和开销记录网页项目。可编辑工程保留原始配音、最终音频、声学对齐缓存、语义标记、渲染程序和依赖锁文件。账户密钥和业务空间标识未放入交付包。
'''
 (ROOT/'docs/交付说明.md').write_text(text,encoding='utf8')
 for n in ['完整讲稿.md','示例与习题答案.md','参考资料.md','交付说明.md']:shutil.copy2(ROOT/'docs'/n,DEL/n)
 shutil.copy2(ROOT/'build/final-verification.json',DEL/'成片验证报告.json')
 includes=['README.md','.gitignore','.env.example','package.json','package-lock.json','requirements.txt','content','docs','examples','public/course.json','public/timeline.json','public/audio_original','build/alignment']
 includes += [str(p.relative_to(ROOT)) for p in sorted((ROOT/'scripts').glob('*.py')) if p.name!='setup_pipeline.py']
 for c in narration['chapters']:
  for s in c['scenes']:includes += ['public/audio/'+s['key']+'.wav','public/audio/'+s['key']+'.json']
 includes += ['build/'+n+'.json' for n in ['audio-preparation','example-verification','project-verification','layout-verification','highlight-resolution','final-verification']]
 result=pack(ROOT,includes,DEL/'TypeScript可编辑工程.zip',known);assert result['allPassed'],result
 examples=pack(ROOT,['examples','package.json','package-lock.json'],DEL/'TypeScript配套示例与项目.zip',known);assert examples['allPassed'],examples
 (DEL/'工程隐私扫描报告.json').write_text(json.dumps(dict(project=result,examples=examples),ensure_ascii=False,indent=2),encoding='utf8')
 print('SAFE_RELEASE_READY',result['filesScanned'],examples['filesScanned'],flush=True)
if __name__=='__main__':release(secrets_from_env(['DASHSCOPE_API_KEY','SFM_WORKSPACE_ID']))
