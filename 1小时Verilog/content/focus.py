"""Teacher-reviewed code-line targets; persistent selection changes only at actual narration starts."""
TARGETS={
 'vl-01-03':([1,3],[2]),
 'vl-01-04':([3,4],[3,4]),
 'vl-02-01':([1,2],[3]),
 'vl-02-02':([1,2],[3,4,5]),
 'vl-02-04':([1,2,3,4,5],[6]),
 'vl-03-01':([1,4],[5,6]),
 'vl-03-02':([1,2,4],[3,5]),
 'vl-03-03':([3],[3]),
 'vl-04-01':([3],[4,5]),
 'vl-04-02':([4,5],[5]),
 'vl-04-03':([3,4,5,6,7],[8]),
 'vl-04-04':([3,4],[3,4]),
 'vl-04-05':([4,5],[4,5]),
 'vl-05-01':([3],[3,5]),
 'vl-05-02':([3,4],[3,4]),
 'vl-05-03':([3,4],[3,4]),
 'vl-05-04':([3,4,5],[3,5]),
 'vl-05-05':([2,5],[3,5]),
 'vl-06-01':([6,7],[6,7]),
 'vl-06-02':([6,7],[6,7]),
 'vl-06-03':([6,7],[6,7]),
 'vl-07-01':([4,5],[3,4,5,6]),
 'vl-07-02':([1,3,4],[1,3,4,6]),
 'vl-07-03':([4,5,6,7],[6,7]),
 'vl-07-04':([3,4,5,6],[7]),
 'vl-08-02':([3,4,5,6,7],[3,4,5,6,7]),
 'vl-08-03':([2,3,4,5,6],[4,5,6,7]),
 'vl-08-04':([8],[8]),
 'vl-09-01':([2,3],[5]),
 'vl-09-02':([1,3,4,5,6],[7,8,9]),
 'vl-09-03':([1,2,4,5,6],[5,6]),
 'vl-10-02':([4,5,6,7,8,9,10],[1,3,5,6,7,8,9,10]),
 'vl-10-03':([5,6],[5,6,7,8,9,10])
}
def refine(chapters):
 scenes={s['key']:s for c in chapters for s in c['scenes']}
 assert set(TARGETS)=={s['key'] for s in scenes.values() if s['code']},'Every code scene needs an explicit teacher-reviewed map'
 for key,pairs in TARGETS.items():
  scene=scenes[key];assert len(pairs)==len(scene['parts'])
  for part,lines in zip(scene['parts'],pairs):
   assert lines and len(lines)==len(set(lines)) and all(1<=n<=len(scene['code']) for n in lines)
   part['codeLines']=list(lines);part['lines']=list(lines)
