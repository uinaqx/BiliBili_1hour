CHAPTERS=[]
def chapter(key,title,english):
 c=dict(key=key,title=title,english=english,scenes=[]);CHAPTERS.append(c);return c
def scene(c,key,title,text,notes,visual,kind='lesson'):
 beats=[x.strip() for x in text.strip().split('|')];assert len(beats)==4,(key,len(beats))
 if key.endswith('-q'):kind='question'
 if key.endswith('-a'):kind='answer'
 c['scenes'].append(dict(key=key,section=key,title=title,narration=''.join(beats),sourceNarration='\n\n'.join(beats),beats=beats,notes=notes,visual=visual,kind=kind,hold=4 if kind=='question' else 1.2))
