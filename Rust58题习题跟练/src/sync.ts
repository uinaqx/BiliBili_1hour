// Speech onsets move the highlight; phrase endings never clear it.
export type CodeCue={beginFrame:number;endFrame:number;lines:number[];cue:string;findingId?:string};
export type DiagramCue={beginFrame:number;endFrame?:number;stage?:number;focus?:number;contents?:string;mode?:string;values?:number[];cue:string};
export function codeLinesAt(events:CodeCue[],frame:number,initialLines:number[]=[]):number[]{
  const started=events.filter(e=>frame>=e.beginFrame);
  if(!started.length)return [...initialLines];
  const latest=Math.max(...started.map(e=>e.beginFrame));
  const current=started.filter(e=>e.beginFrame===latest);
  const reviewed=current.filter(e=>e.findingId);
  return [...new Set((reviewed.length?reviewed:current).flatMap(e=>e.lines))].sort((a,b)=>a-b);
}
export function diagramAt(events:DiagramCue[],frame:number):Partial<DiagramCue>{
  let selected:Partial<DiagramCue>={};
  for(const e of events){if(e.beginFrame>frame)break;if(e.endFrame!==undefined&&frame>=e.endFrame)continue;selected={...selected,...e};}
  return selected;
}
