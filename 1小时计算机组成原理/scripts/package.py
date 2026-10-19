"""Package the original lesson, models and editable video without credentials."""
import json,pathlib,re,shutil,sys,zipfile
sys.stdout.reconfigure(encoding='utf-8');ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out'
def scan(path):
 if path.suffix.lower() not in {'.py','.mjs','.tsx','.ts','.json','.md','.txt','.example','.gitignore'}:return
 text=path.read_text(encoding='utf-8-sig',errors='replace')
 for pattern in (r'\bsk-[A-Za-z0-9_.-]{20,}',r'\bllm-[a-z0-9]{10,}'):
  if re.search(pattern,text):raise RuntimeError('Possible credential in '+str(path.relative_to(ROOT)))
def main():
 report=json.loads((ROOT/'build/final-validation.json').read_text(encoding='utf-8'));assert report['allPassed']
 course=json.loads((ROOT/'public/course.json').read_text(encoding='utf-8'));minutes,seconds=divmod(report['durationSeconds'],60);duration=f'{int(minutes)} 分 {seconds:.1f} 秒'
 rows=['# 课堂练习与答案','','每题在成片中提供四秒独立思考。先写出状态或算式，再核对结果。','']
 for c in course['chapters']:
  q=next((s for s in c['scenes'] if s['kind']=='question'),None);a=next((s for s in c['scenes'] if s['kind']=='answer'),None)
  if not q:continue
  rows.extend(['## '+c['title']+' · '+c['english'],'','题目：'+q['sourceNarration'],'','答案与解释：'+a['sourceNarration'],'','要点：'+'；'.join(a['notes']),''])
 (DEL/'课堂练习与答案.md').write_text('\n'.join(rows),encoding='utf-8')
 shutil.copy2(ROOT/'content/完整讲稿.md',DEL/'完整讲稿.md');shutil.copy2(ROOT/'content/计算示例与模型约定.md',DEL/'计算示例与模型约定.md')
 validation=['# 成片验收说明','',f'总时长：{duration}。','',
  '- 12 章、73 个分镜、11 道课堂题，处于 50～70 分钟范围内。',
  '- 旁白服务速率固定 1.0，没有按目标时长加速、减速或拉伸；逐段 PCM 与原始配音直接解码结果一致。',
  f"- 补码加法与溢出、全加器、容量、字节序、缓存、四指令模拟、性能与分页模型通过 {report['modelAssertions']} 项断言。",
  '- 1920×1080、H.264/AAC、12 个 MP4 章节标记；全片严格解码通过。',
  f"- 检查全部 {report['encodedStates']} 个编码显示状态及 {report['captions']} 条字幕的实际显示，未发现应显示却空白的状态。",
  '- 每章合成声音与来源 PCM 的波形相关性、偏移校验通过。',
  '- 检查各分镜完成状态、所有课堂题倒计时和答案，并抽查成片章节首、中、尾与拼接处。','',
  '字幕已按现有音频的语义识别逐字时间重新校准，独立声学时间用于交叉检查。字幕持续到下一句，末句覆盖到朗读结束。修订成片直接复制旧版 AAC，载荷与包时间戳校验一致。自动识别及显示检查不等于逐字人工听辨。','']
 (DEL/'验收说明.md').write_text('\n'.join(validation),encoding='utf-8')
 readme=['# 一小时学习计算机组成原理','',f'成片时长：{duration}。自然语速，符合约定的 50～70 分钟。','',
  '- `一小时学习计算机组成原理_字幕校准版.mp4`：已校准字幕的完整视频，语音、画面步骤及章节时间保持不变；主文件 `一小时学习计算机组成原理.mp4` 已同步更新。',
  '- `中文字幕.srt`、`章节目录.md`：独立字幕与实测章节时间。',
  '- `完整讲稿.md`、`课堂练习与答案.md`、`计算示例与模型约定.md`：教学配套材料。',
  '- `计算机组成原理视频工程.zip`：讲稿、图示、声音缓存、制作脚本与 README。',
  '- `验收说明.md`、`验收报告.json`：实际检查记录。','',
  '视觉沿用数据结构课程，左侧原代码区改为结构图、位格、数据流与计算过程，字幕底部居中。工程不包含 API Key 或 Workspace ID。','']
 (DEL/'交付说明.md').write_text('\n'.join(readme),encoding='utf-8')
 paths=[]
 for folder in ['src','content','scripts']:
  paths.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
 paths.extend(ROOT/p for p in ['README.md','requirements.txt','requirements-subtitles.txt','package.json','package-lock.json','tsconfig.json','.gitignore','.env.example','public/course.json','public/timeline.json'])
 paths.extend(p for p in (ROOT/'public/audio').glob('*') if p.suffix in {'.json','.wav'} and not p.name.endswith('.scaled.wav'))
 paths.extend(p for p in (ROOT/'public/audio_original').glob('*') if p.suffix in {'.json','.mp3'} and not p.name.startswith('voice-test'))
 paths.extend((ROOT/'build/alignment').glob('*.json'))
 for folder in ['subtitle-fa','subtitle-asr']:
  paths.extend((ROOT/'build'/folder).glob('*.json'))
 paths.extend(p for p in [ROOT/'build/subtitle-calibration.json',ROOT/'build/subtitle-audio-proof.json',ROOT/'build/subtitle-review.json'] if p.exists())
 paths.extend(ROOT/'build'/p for p in ['audio-settings.json','audio-alignment.json','model-validation.json','final-validation.json'])
 for p in paths:scan(p)
 archive=DEL/'计算机组成原理视频工程.zip'
 with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=5) as z:
  for p in sorted(set(paths)):z.write(p,'计组一小时制作工程/'+p.relative_to(ROOT).as_posix())
 with zipfile.ZipFile(archive) as z:assert z.testzip() is None
 print('PACKAGED',len(set(paths)),round(archive.stat().st_size/1024**2,1),'MiB; credential pattern scan passed',flush=True)
if __name__=='__main__':main()
