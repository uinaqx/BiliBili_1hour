// Reference renderer state: phrase endings never clear the current selection.
export type CodeCue = {beginFrame:number; endFrame?:number; lines:number[]; cue?:string; panelId?:string};
export type Panel = {id?:string; beginFrame:number; code:string; initialCodeLines:number[]};
export type CodeScene = {code:string; initialCodeLines:number[]; durationFrames:number; codeCues:CodeCue[]; panels?:Panel[]};
export type DiagramCue = {beginFrame:number; patch:Record<string,unknown>; groupId?:string};

export function codePageAt(scene:CodeScene, frame:number) {
  if (frame < 0 || frame >= scene.durationFrames) throw new Error('Frame outside scene');
  const panels = [...(scene.panels ?? [])].sort((a,b)=>a.beginFrame-b.beginFrame);
  const startedPanels = panels.filter(p=>p.beginFrame<=frame);
  const current = startedPanels[startedPanels.length-1];
  const begin = current?.beginFrame ?? 0;
  const end = panels.find(p=>p.beginFrame>frame)?.beginFrame ?? scene.durationFrames;
  return {id:current?.id ?? (current ? String(begin) : 'root'), begin, end,
    code:current?.code ?? scene.code, initial:current?.initialCodeLines ?? scene.initialCodeLines};
}

export function activeCodeLines(scene:CodeScene, frame:number):number[] {
  const page = codePageAt(scene, frame);
  const started = scene.codeCues.filter(c=>c.beginFrame>=page.begin && c.beginFrame<page.end &&
    c.beginFrame<=frame && (c.panelId===undefined || c.panelId===page.id));
  const latest = Math.max(-1,...started.map(c=>c.beginFrame));
  const chosen = started.length ? started.filter(c=>c.beginFrame===latest).flatMap(c=>c.lines) : page.initial;
  const result = [...new Set(chosen)].sort((a,b)=>a-b);
  const rows = page.code.split('\n');
  if (page.code && (!result.length || result.some(n=>!Number.isInteger(n)||n<1||n>rows.length) ||
      !result.some(n=>rows[n-1].trim()))) throw new Error('Invalid highlight for current code panel');
  return result;
}

export function diagramStateAt(events:DiagramCue[], frame:number, initial:Record<string,unknown>={}, groupId?:string) {
  const state = {...initial};
  for (const event of [...events].sort((a,b)=>a.beginFrame-b.beginFrame)) {
    if (event.beginFrame>frame) break;
    if (event.groupId!==undefined && event.groupId!==groupId) continue;
    Object.assign(state,event.patch);
  }
  return state;
}
