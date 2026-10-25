import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import data from '../public/timeline.json';
import {codeLinesAt,CodeCue} from './sync';
import {DataDiagram,VisualSpec} from './diagrams';
type VisualCue={beginFrame:number;spec:VisualSpec|null};
type Scene={key:string;number:number;exercise:string;chapter:string;chapterIndex:number;sceneIndex:number;sceneCount:number;startFrame:number;durationFrames:number;speechFrames:number;leadFrames:number;sentenceTailFrames:number;code:string;title:string;notes:string[];kind:string;filename:string;section:string;excerpt:boolean;output:string|null;resultFrame:number;audio:string;steps:number[];initialCodeLines:number[];codeCues:CodeCue[];initialVisual:VisualSpec|null;diagramCues:VisualCue[]};
export const Timeline=data as unknown as {scope?:string;totalFrames:number;scenes:Scene[];chapters:{title:string}[]};
const C={bg:'#0b1422',panel:'#122033',border:'#2a3b52',text:'#f0f3f7',muted:'#96a9c0',orange:'#ffba78',blue:'#80d4e7',green:'#a5dfb4'};
const mono='"Cascadia Code", Consolas, "Microsoft YaHei", monospace';
function Tokens({text}:{text:string}){
 const names='as|async|await|break|const|continue|crate|dyn|else|enum|extern|false|fn|for|if|impl|in|let|loop|match|mod|move|mut|pub|ref|return|self|Self|static|struct|super|trait|true|type|unsafe|use|where|while';
 const types='bool|char|f32|f64|i8|i16|i32|i64|u8|u16|u32|u64|usize|isize|str|String|Vec|Option|Some|None|HashMap|Display|Debug';
 const keyword=new RegExp('^(?:'+names+')$'),type=new RegExp('^(?:'+types+')$');
 const p=new RegExp('(//.*|"(?:\\\\.|[^"\\\\])*"|\'(?:\\\\.|[^\'\\\\])\'|\'[A-Za-z_]\\w*|\\b(?:'+names+'|'+types+')\\b|\\b\\d+(?:\\.\\d+)?\\b)','g');
 return <>{text.split(p).filter(Boolean).map((v,i)=>{let color=C.text;if(v.startsWith('//'))color=C.muted;else if(v.startsWith('"')||/^'.*'$/.test(v))color=C.green;else if(keyword.test(v))color=C.orange;else if(type.test(v))color=C.blue;else if(/^\d|^'/.test(v))color='#d6b8f1';return <span key={i} style={{color}}>{v}</span>;})}</>;
}
function Overview(){return <AbsoluteFill style={{background:'radial-gradient(ellipse at 28% 38%, #102c49 0%, #0a1d35 52%, #07172c 100%)',color:'#f4f7fc',fontFamily:'Microsoft YaHei, sans-serif'}}>
 <div style={{position:'absolute',left:88,top:70,fontSize:30,color:'#ffb740'}}>完整覆盖 · 按原题编号跟练</div>
 <div style={{position:'absolute',left:76,top:135,fontSize:176,lineHeight:1.1,fontWeight:700}}>Rust 基础</div>
 <div style={{position:'absolute',left:86,top:335,fontSize:122,lineHeight:1.1,fontWeight:600,color:'#ffb740'}}>58题跟练</div>
 <div style={{position:'absolute',left:88,right:80,top:560,display:'grid',gridTemplateColumns:'1fr 1fr',columnGap:62}}>
 {[Timeline.chapters.slice(0,5),Timeline.chapters.slice(5)].map((col,j)=><div key={j}>{col.map(c=><div data-overview-topic key={c.title} style={{height:76,display:'flex',alignItems:'center',gap:20}}><span style={{width:18,height:18,borderRadius:20,background:'#ffb740',flexShrink:0}}/><span style={{fontSize:36,fontWeight:500}}>{c.title}</span></div>)}</div>)}
 </div>
 </AbsoluteFill>;}
export const Course:React.FC<{includeAudio:boolean;includeCaptions:boolean}>=({includeAudio})=>{
 const rootRef=React.useRef<HTMLDivElement>(null);
 const frame=useCurrentFrame();const s=Timeline.scenes.find(x=>frame>=x.startFrame&&frame<x.startFrame+x.durationFrames)??Timeline.scenes[Timeline.scenes.length-1];const local=frame-s.startFrame;
 const active=codeLinesAt(s.codeCues,local,s.initialCodeLines);const visual=s.diagramCues.filter(c=>c.beginFrame<=local).slice(-1)[0]?.spec??s.initialVisual;
 const stage=s.steps.reduce((a,x,i)=>local>=x?i:a,0),question=s.kind==='question',pause=question&&local>=s.leadFrames+s.speechFrames+s.sentenceTailFrames;
 const showResult=!question&&s.output!==null&&local>=s.resultFrame;
 React.useLayoutEffect(()=>{
  const audit=()=>{
  const document=rootRef.current;if(!document)return;
  const readySide=document.querySelector('[data-side]');if(!readySide||readySide.clientWidth<350)return;
  const code=document.querySelector('[data-code-inner]'),panel=document.querySelector('[data-code-panel]');
  if(code&&panel){const a=code.getBoundingClientRect(),b=panel.getBoundingClientRect();if(a.bottom>b.bottom-8)throw Error('Code overflow '+s.key+' '+a.bottom+'/'+b.bottom);}
  const result=document.querySelector('[data-result-text]');if(result&&result.scrollHeight>116)throw Error('Result overflow '+s.key);
  const side=document.querySelector('[data-side]');if(side&&side.scrollHeight>side.clientHeight+3)throw Error('Side overflow '+s.key);
  for(const n of Array.from(document.querySelectorAll('[data-overview-topic]'))){if(n.getBoundingClientRect().right>1890)throw Error('Overview overflow');}
  const svg=document.querySelector('svg');if(svg){const b=svg.getBoundingClientRect();for(const n of Array.from(svg.querySelectorAll('text'))){const a=n.getBoundingClientRect();if(a.left<b.left-2||a.right>b.right+2)throw Error('Diagram overflow '+s.key);}}
  console.log('PRACTICE_META:'+JSON.stringify({key:s.key,frame,local,activeLines:active,rows:Array.from(document.querySelectorAll('[data-line]')).map(n=>{const r=n.getBoundingClientRect();return {line:Number(n.getAttribute('data-line')),selected:n.getAttribute('data-selected')==='true',left:r.left,top:r.top,right:r.right,bottom:r.bottom};}),resultVisible:showResult,resultText:result?.textContent??null}));
  };
  audit();const raf=requestAnimationFrame(audit);const observer=new ResizeObserver(audit);if(rootRef.current)observer.observe(rootRef.current);
  return ()=>{cancelAnimationFrame(raf);observer.disconnect();};
 },[frame,s.key]);
 const audio=includeAudio&&<Sequence from={s.startFrame+s.leadFrames} durationInFrames={s.speechFrames}><Audio src={staticFile(s.audio)}/></Sequence>;
 if(s.key==='rp-overview')return <><Overview/>{audio}</>;
 return <AbsoluteFill ref={rootRef} style={{background:C.bg,color:C.text,fontFamily:'Microsoft YaHei, sans-serif'}}>
  <div style={{position:'absolute',top:0,left:0,right:0,height:6,background:C.border}}><div style={{height:6,width:`${s.startFrame/Timeline.totalFrames*100}%`,background:C.orange}}/></div>
  <div style={{position:'absolute',left:64,top:35,fontSize:25,color:C.orange}}>Rust 习题跟练 · {String(s.chapterIndex).padStart(2,'0')}</div>
  <div style={{position:'absolute',right:64,top:39,fontSize:22,color:C.muted}}>全部58题 · 读题、修改与验证</div>
  <div style={{position:'absolute',left:64,top:87,fontSize:46,fontWeight:600}}>{s.chapter}</div>
  <div style={{position:'absolute',left:64,top:157,fontSize:23,color:question?C.blue:C.green}}>{s.title}</div>
  <div data-code-panel style={{position:'absolute',left:64,top:208,width:1336,height:560,boxSizing:'border-box',borderRadius:18,overflow:'hidden',border:`1px solid ${C.border}`,background:C.panel}}>
   <div style={{height:40,background:'#192a40',display:'flex',alignItems:'center',padding:'0 22px',gap:9}}>{['#ed908a','#efd081','#91d4b0'].map(color=><span key={color} style={{width:10,height:10,borderRadius:10,background:color}}/>)}<span style={{marginLeft:15,fontSize:19,color:C.muted}}>{s.filename}　关键代码节选 · 完整文件见配套源码</span></div>
   <div style={{padding:'15px 18px 12px 8px',fontFamily:mono,fontVariantLigatures:'none',fontSize:34,lineHeight:'36px'}}><div data-code-inner>{s.code.split('\n').map((r,i)=>{const selected=active.includes(i+1);return <div key={i} data-line={i+1} data-selected={selected} style={{display:'flex',minHeight:36,borderLeft:`3px solid ${selected?C.orange:'transparent'}`,background:selected?'rgba(255,186,120,.085)':'transparent'}}><div style={{width:59,flexShrink:0,textAlign:'right',paddingRight:17,fontSize:21,color:selected?C.orange:'#6e829e'}}>{String(i+1).padStart(2,'0')}</div><div style={{whiteSpace:'pre-wrap',overflowWrap:'anywhere',flex:1}}><Tokens text={r}/></div></div>;})}</div></div>
  </div>
  <div style={{position:'absolute',left:64,top:778,width:1336,height:164,boxSizing:'border-box',border:`1px solid ${C.border}`,borderRadius:14,padding:'10px 18px',background:'#15283b'}}>
   <div style={{fontSize:20,lineHeight:'23px',color:question?C.blue:C.muted,marginBottom:6}}>{question?'动手练习':s.output?.startsWith('test result:')?'完整文件测试结果':'完整程序运行结果'}</div>
   <pre data-result-text style={{fontSize:32,fontFamily:mono,lineHeight:'34px',whiteSpace:'pre-wrap',overflowWrap:'anywhere',margin:0,color:question?C.muted:C.green}}>{question?'暂停视频先完成，再继续核对答案。':showResult?s.output:'跟随当前步骤，随后核对实际结果。'}</pre>
  </div>
  <div data-side style={{position:'absolute',left:1432,right:64,top:215,height:720,display:'flex',flexDirection:'column'}}>
   <div style={{fontSize:23,color:C.blue,marginBottom:22,flexShrink:0}}>{question?'读题与限制':'本步要点'}</div>
   {s.notes.map((n,i)=><div key={i} style={{fontSize:27,lineHeight:1.5,marginBottom:16,opacity:i<=stage?1:.4,flexShrink:0}}><span style={{color:C.orange}}>• </span>{n}</div>)}
   {visual&&!question&&<div style={{marginTop:20,flexShrink:0}}><DataDiagram spec={visual}/></div>}
   {pause&&<div style={{marginTop:'auto',border:`1px solid ${C.blue}`,borderRadius:14,padding:18,background:'#133342',textAlign:'center'}}><div style={{fontSize:24,color:C.blue}}>思考与动手</div><div style={{fontSize:68,fontFamily:mono,lineHeight:1.2,marginTop:6}}>{Math.max(1,Math.ceil((s.durationFrames-local)/30))}</div><div style={{fontSize:20,color:C.muted,marginTop:6}}>需要更久请暂停视频</div></div>}
  </div>
  <div style={{position:'absolute',top:950,left:66,fontSize:17,color:'#7186a1'}}>本章第 {s.sceneIndex+1} / {s.sceneCount} 个片段</div>
  <div style={{position:'absolute',top:980,bottom:0,left:0,right:0,background:'#09111e',borderTop:`1px solid ${C.border}`}}/>
  {audio}
 </AbsoluteFill>;
};
