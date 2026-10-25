"""Write reusable references, timestamped diagram guide and runtime dependencies."""
import importlib.metadata,json,pathlib,shutil
from PIL import Image
import draw
from timeline import stamp
ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out'
def main():
    t=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf8'));assert t['scope']=='complete-course';DEL.mkdir(parents=True,exist_ok=True);draw.init(t)
    rows=['# 逐页来源与图示','','时间戳为最终时间轴的原始页面起点。动画锚点按最终页面 PCM 定位，持续变化后保留状态。','', '| 起点 | 页面 | 图示种类 | 来源 |','| --- | --- | --- | --- |']
    registry={'S1':'https://openai.com/index/unrolling-the-codex-agent-loop/','S2':'https://www.anthropic.com/research/writing-tools-for-agents','S3':'https://www.anthropic.com/research/effective-context-engineering-for-ai-agents','S4':'https://www.anthropic.com/research/effective-harnesses-for-long-running-agents','S5':'https://docs.langchain.com/oss/python/langgraph/persistence','S6':'https://modelcontextprotocol.io/specification/2025-06-18/server/tools','S7':'https://openai.github.io/openai-agents-python/running_agents/','S8':'https://github.com/temporalio/documentation/blob/main/docs/develop/python/best-practices/error-handling.mdx'}
    for s in t['scenes']:
        assert set(s['sources'])<=set(registry);kinds=', '.join(dict.fromkeys(p['visual']['kind'] for p in s['parts']));sources='、'.join(f'[{x}]({registry[x]})' for x in s['sources']);rows.append(f"| {stamp(s['startFrame']/30)} | {s['key']} {s['title']} | {kinds} | {sources} |")
    text='\n'.join(rows)+'\n';(ROOT/'references/逐页来源与图示.md').write_text(text,encoding='utf8');(DEL/'图示与参考来源.md').write_text(text+'\n'+(ROOT/'references/来源.md').read_text(encoding='utf8'),encoding='utf8')
    for source,name in [(ROOT/'docs/机制速查.md','机制速查.md'),(ROOT/'docs/本地案例说明.md','本地案例说明.md')]:shutil.copy2(source,DEL/name)
    shutil.copy2(ROOT/'build/demo-execution.json',DEL/'本地案例实际执行记录.json')
    draw.render(t['scenes'][0],0).save(DEL/'课程知识地图.png')
    packages=['requests','numpy','scipy','Pillow','openai-whisper','torch'];locked=['# Python 3.11 / Windows; FFmpeg and system fonts are separate prerequisites.']
    for name in packages:locked.append(name+'=='+importlib.metadata.version(name))
    (ROOT/'requirements.lock.txt').write_text('\n'.join(locked)+'\n',encoding='utf8')
    print('DOCUMENTS_READY',len(t['scenes']),'page references; locked',len(packages),'dependencies',flush=True)
if __name__=='__main__':main()
