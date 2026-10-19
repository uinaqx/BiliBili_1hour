import importlib,json,pathlib,sys
sys.stdout.reconfigure(encoding='utf-8');ROOT=pathlib.Path(__file__).resolve().parents[1];(ROOT/'public').mkdir(exist_ok=True);(ROOT/'build').mkdir(exist_ok=True);(ROOT/'out').mkdir(exist_ok=True);DEL=ROOT/'out';DEL.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'content'));from author import CHAPTERS
from visual_data import VISUALS
for name in ['chapters_a','chapters_b','chapters_c','chapters_d']:
 if (ROOT/'content'/(name+'.py')).exists():importlib.import_module(name)
scenes=[s for c in CHAPTERS for s in c['scenes']];assert len({s['key'] for s in scenes})==len(scenes)
for s in scenes:s['visualPanels']=VISUALS[s['visual']]
course=dict(title='一小时学习计算机组成原理',language='结构图与计算示例',audience='初学者与大学生',chapters=CHAPTERS)
(ROOT/'public/course.json').write_text(json.dumps(course,ensure_ascii=False,indent=2),encoding='utf-8')
rows=['# 一小时学习计算机组成原理：完整讲稿','','自然语速；最终时长以配音实测为准，接受 50～70 分钟。','']
for c in CHAPTERS:
 rows.extend(['## '+c['title']+' · '+c['english'],''])
 for s in c['scenes']:
  rows.extend(['### '+s['key']+' '+s['title'],'',s['sourceNarration'],'','画面要点：'+'；'.join(s['notes']),''])
  if s['kind']=='question':rows.extend(['（四秒独立思考，随后核对答案）',''])
text='\n'.join(rows);(ROOT/'content/完整讲稿.md').write_text(text,encoding='utf-8');(DEL/'完整讲稿.md').write_text(text,encoding='utf-8')
spoken=''.join(s['narration'] for s in scenes);print('COURSE_READY',len(CHAPTERS),len(scenes),sum('\u4e00'<=c<='\u9fff' for c in spoken),flush=True)
