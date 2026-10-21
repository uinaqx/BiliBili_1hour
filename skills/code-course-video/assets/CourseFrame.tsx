import React from 'react';
import {activeCodeLines,codePageAt} from './persistent-sync';
import type {CodeScene} from './persistent-sync';

type Props={scene:CodeScene; localFrame:number; chapterTitle:string; pageTitle:string;
  courseTitle:string; notes:string[]; includeCaptions:boolean; caption?:string;
  mode?:'code'|'diagram'; diagram?:React.ReactNode; output?:string;
  outputLabel?:string; revealOutputFrame?:number; renderCodeLine?:(line:string,index:number)=>React.ReactNode};
const color={bg:'#0b1422',panel:'#122033',border:'#2a3b52',text:'#f0f3f7',muted:'#96a9c0',orange:'#ffba78',green:'#a5dfb4'};
const box:React.CSSProperties={position:'absolute',boxSizing:'border-box',background:color.panel,border:`1px solid ${color.border}`,borderRadius:14};

// Integrate into a Remotion Composition at 1920x1080. Subtitle space stays fixed.
export const CourseFrame:React.FC<Props>=(p)=>{
  const mode=p.mode??'code';
  const page=codePageAt(p.scene,p.localFrame);
  const lines=page.code.split('\n');
  if(mode==='code' && lines.length>16)throw new Error('Split code into a new page/panel instead of shrinking the font');
  if(p.output && p.output.trimEnd().split('\n').length>3)throw new Error('Split a long output into an additional page');
  const active=mode==='code'?activeCodeLines(p.scene,p.localFrame):[];
  const resultVisible=p.output!==undefined && p.localFrame>=(p.revealOutputFrame??0);
  return <div style={{width:1920,height:1080,position:'relative',background:color.bg,color:color.text,
    fontFamily:'"Microsoft YaHei", "Noto Sans CJK SC", sans-serif'}}>
    <div style={{position:'absolute',left:56,top:36,fontSize:24,color:color.orange}}>{p.courseTitle}</div>
    <div style={{position:'absolute',left:56,top:78,fontSize:48,fontWeight:700}}>{p.chapterTitle}</div>
    <div style={{position:'absolute',left:58,top:143,fontSize:25,color:color.muted}}>{p.pageTitle}</div>
    <div data-code-panel style={{...box,left:56,top:190,width:1320,height:594,padding:8}}>
      {mode==='diagram'?p.diagram:<div data-code-rows style={{fontFamily:'"Cascadia Code", Consolas, "Noto Sans Mono", monospace',fontSize:34,lineHeight:'36px'}}>
        {lines.map((line,i)=><div key={i} style={{display:'flex',minHeight:36,
          borderLeft:`3px solid ${active.includes(i+1)?color.orange:'transparent'}`,
          background:active.includes(i+1)?'rgba(255,186,120,0.085)':'transparent'}}>
          <span style={{width:62,flexShrink:0,textAlign:'right',paddingRight:16,fontSize:22,color:active.includes(i+1)?color.orange:color.muted}}>{String(i+1).padStart(2,'0')}</span>
          <span style={{whiteSpace:'pre-wrap',overflowWrap:'anywhere',flex:1}}>{p.renderCodeLine?p.renderCodeLine(line,i):line}</span>
        </div>)}
      </div>}
    </div>
    <div style={{...box,left:56,top:800,width:1320,height:146,padding:'6px 16px'}}>
      <div style={{fontSize:18,color:color.muted}}>{p.outputLabel??(mode==='code'?'运行结果':'推演结论')}</div>
      {resultVisible&&<pre data-program-output style={{margin:'3px 0 0',whiteSpace:'pre-wrap',fontFamily:'Consolas, "Microsoft YaHei", monospace',fontSize:32,lineHeight:'36px',color:color.green}}>{p.output}</pre>}
    </div>
    <aside style={{...box,left:1410,top:190,width:454,height:756,padding:24,fontSize:30,lineHeight:1.55}}>
      {p.notes.map((note,i)=><p key={i} style={{margin:'0 0 24px'}}>{note}</p>)}
    </aside>
    {p.includeCaptions&&p.caption&&<div data-caption style={{position:'absolute',left:90,right:90,top:970,height:86,
      fontSize:38,lineHeight:'44px',textAlign:'center',whiteSpace:'pre-wrap'}}>{p.caption}</div>}
  </div>;
};
