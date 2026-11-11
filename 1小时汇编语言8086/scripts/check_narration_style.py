"""Assist human review of the affirmative teaching style requested by the user."""
import ast,collections,hashlib,json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
PATTERNS=['不是','不能','不代表','不等于','并不能','不说明','不自动','不是说','不要','不保证','需要注意的是','必须强调的是','这并不意味着']
def inspect(texts):
 hits=[dict(part=i,phrase=p,count=t.count(p)) for i,t in enumerate(texts) for p in PATTERNS if p in t]
 sentences=collections.Counter(x.strip() for t in texts for x in re.split('[。！？]',t) if len(x.strip())>=12)
 repeated=[dict(sentence=s,count=n) for s,n in sentences.items() if n>1]
 return dict(parts=len(texts),cjk=sum(len(re.findall('[\u4e00-\u9fff]',t)) for t in texts),defensivePatterns=hits,defensivePatternOccurrences=sum(h['count'] for h in hits),repeatedLongSentences=repeated)
def main():
 course=json.loads((ROOT/'public/course.json').read_text(encoding='utf8'));texts=[p['text'] for c in course['chapters'] for s in c['scenes'] for p in s['parts']];after=inspect(texts);before=[]
 for p in sorted((ROOT/'build/revisions/before-style-rewrite').glob('chapters_*.py')):
  for node in ast.walk(ast.parse(p.read_text(encoding='utf8'))):
   if isinstance(node,ast.Call) and isinstance(node.func,ast.Name):
    if node.func.id in ['L','Q']:before.extend(a.value for a in node.args[4:6] if isinstance(a,ast.Constant))
    elif node.func.id=='P' and isinstance(node.args[0],ast.Constant):before.append(node.args[0].value)
 assert len(texts)==121 and not after['defensivePatterns'],after['defensivePatterns']
 assert not after['repeatedLongSentences'],after['repeatedLongSentences']
 if before:before=inspect(before)
 else:
  saved=ROOT/'build/narration-style-review.json';assert saved.exists(),'Original style baseline is absent; keep the packaged review report for historical comparison'
  before=json.loads(saved.read_text(encoding='utf8'))['before']
 report=dict(allPassed=True,courseSha256=hashlib.sha256((ROOT/'public/course.json').read_bytes()).hexdigest(),before=before,after=after,scope='All 121 narration units were manually rewritten; pattern and exact-sentence checks assist style review. Program execution and audio/video checks are separate.')
 (ROOT/'build/narration-style-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
 out=f'''# 讲稿语言自检

本次按用户指定风格，人工重写全部121段旁白，并调整页面注解：直接讲数据、操作、状态与结果；技术条件放在所需的例子中说明。

改写前共有{before['defensivePatternOccurrences']}处被筛选的否定式澄清与提醒，改写后为{after['defensivePatternOccurrences']}处。长句按完整句子检查，重复数为{len(after['repeatedLongSentences'])}。四秒思考等功能提示按教学流程保留。

最终旁白约{after['cjk']}个中文字。每章保留原有知识目标、代码、例题和答案，新增说明围绕当前例子的操作过程与核对方法。计算、分支条件、位宽、栈布局和接口约定按实际含义保留。

这份记录是文字检查结果；语音定位、代码执行和最终视频使用各自的验收记录。
'''
 (ROOT/'docs/讲稿语言自检.md').write_text(out,encoding='utf8');print(json.dumps(dict(allPassed=True,parts=len(texts),before=before['defensivePatternOccurrences'],after=after['defensivePatternOccurrences'],cjk=after['cjk'],repeatedLongSentences=after['repeatedLongSentences']),ensure_ascii=False),flush=True)
if __name__=='__main__':main()
