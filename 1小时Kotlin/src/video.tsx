import {CodeCue,DiagramCue,codeLinesAt,diagramAt} from './sync';
import React from 'react';
import {DataDiagram} from './diagrams';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import data from '../public/timeline.json';
type Caption={start:number;end:number;text:string};
type Scene={resultFrame:number;initialCodeLines:number[];codeCues:CodeCue[];diagramCues:DiagramCue[];cueFocus:boolean;key:string;section:string;title:string;chapter:string;english:string;chapterIndex:number;sceneIndex:number;sceneCount:number;startFrame:number;durationFrames:number;speechFrames:number;leadFrames:number;sentenceTailFrames:number;steps:number[];code:string;notes:string[];kind:string;error:string|null;panic:boolean;testFailed:boolean;output:string|null;diagram:string|null;focus:number[];audio:string;captions:Caption[];filename:string;excerpt:boolean;panels:{beginFrame:number;initialCodeLines:number[];code:string;notes:string[];output:string;filename?:string}[]};
export const Timeline=data as unknown as {totalFrames:number;audioAvailable?:boolean;scenes:Scene[]};
const C={bg:'#0b1422',panel:'#122033',border:'#2a3b52',text:'#f0f3f7',muted:'#96a9c0',orange:'#ffba78',blue:'#80d4e7',green:'#a5dfb4',red:'#ff9ca0'};
const mono='"Cascadia Code", Consolas, "Microsoft YaHei", monospace';
const smooth=(x:number)=>{const t=Math.max(0,Math.min(1,x));return t*t*(3-2*t);};
const introTopics=[
 ['变量与数据类型','Variables & Types'],['运算符与输入输出','Operators & I/O'],['分支与循环','Control Flow'],['函数与作用范围','Functions & Scope'],['字符串与集合','Strings & Collections'],
 ['空值与空安全','Null Safety'],['类与对象','Classes & Objects'],['集合处理','Collection Operations'],['扩展函数','Extension Functions'],['错误处理与文件','Errors & Files'],
];
function CourseOverview(){
 React.useLayoutEffect(()=>{for(const node of Array.from(document.querySelectorAll('[data-overview-topic]'))){const box=node.getBoundingClientRect();if(box.right>1895||box.bottom>958||node.scrollWidth>node.clientWidth+1)throw Error('Course overview topic overflow');}},[]);
 return <AbsoluteFill style={{background:'radial-gradient(ellipse at 28% 38%, #102c49 0%, #0a1d35 52%, #07172c 100%)',color:'#f4f7fc',fontFamily:'"Microsoft YaHei", sans-serif'}}>
  <div style={{position:'absolute',left:88,top:76,fontSize:30,letterSpacing:4,color:'#ffb740'}}>KOTLIN · 语言基础</div>
  <div style={{position:'absolute',left:76,top:140,fontSize:184,lineHeight:1.1,fontWeight:750,letterSpacing:-5}}>Kotlin</div>
  <div style={{position:'absolute',left:84,top:342,fontSize:142,lineHeight:1.1,fontWeight:700,color:'#ffb740'}}>一小时</div>
  <div style={{position:'absolute',left:88,right:74,top:565,display:'grid',gridTemplateColumns:'1fr 1fr',columnGap:62}}>
   {[introTopics.slice(0,5),introTopics.slice(5)].map((column,j)=><div key={j}>{column.map(([cn,en])=><div data-overview-topic key={cn} style={{height:77,display:'flex',alignItems:'center',gap:18,whiteSpace:'nowrap'}}>
    <span style={{width:19,height:19,borderRadius:20,background:'#ffb740',flexShrink:0}}/>
    <span style={{fontSize:34,fontWeight:600}}>{cn}</span><span style={{fontSize:24,color:'#a8b7d0'}}>· {en}</span>
   </div>)}</div>)}
  </div>
 </AbsoluteFill>;
}
function Tokens({text}:{text:string}){
 const names='fun|val|var|const|if|else|when|return|for|while|do|in|is|as|break|continue|class|data|object|interface|open|override|public|private|protected|internal|this|try|catch|finally|throw|import|true|false|null';
 const keywords=new RegExp('^(?:'+names+')$');
 const types=/^(String|Int|Double|Float|Long|Boolean|Char|Unit|List|MutableList|Map|Set|Student|File|NumberFormatException|IllegalArgumentException)$/;
 const p=new RegExp("(//.*|\"(?:\\\\.|[^\"\\\\])*\"|'(?:\\\\.|[^'\\\\])'|\\b(?:"+names+"|String|Int|Double|Float|Long|Boolean|Char|Unit|List|MutableList|Map|Set|Student|File|NumberFormatException|IllegalArgumentException)\\b|\\b\\d+(?:\\.\\d+)?\\b)",'g');
 return <>{text.split(p).filter(Boolean).map((v,i)=>{let color=C.text;if(v.startsWith('//'))color=C.muted;else if(v.startsWith('"')||v.startsWith("'"))color=C.green;else if(keywords.test(v))color=C.orange;else if(types.test(v))color=C.blue;else if(/^\d/.test(v))color='#d6b8f1';return <span key={i} style={{color}}>{v}</span>;})}</>;
}
export const Course:React.FC<{includeAudio:boolean;includeCaptions:boolean}>=({includeAudio,includeCaptions})=>{
 const frame=useCurrentFrame();const original=Timeline.scenes.find(x=>frame>=x.startFrame&&frame<x.startFrame+x.durationFrames)??Timeline.scenes[Timeline.scenes.length-1];
 const local=frame-original.startFrame;const panel=original.panels?.filter(p=>local>=p.beginFrame).slice(-1)[0];const s=panel?{...original,code:panel.code,notes:panel.notes,output:panel.output,filename:panel.filename??original.filename}:original;let stage=0;s.steps.forEach((v,i)=>{if(local>=v)stage=i;});
 const transition=smooth((local-s.steps[stage])/12);const question=s.kind==='question',pause=question&&local>=s.leadFrames+s.speechFrames+s.sentenceTailFrames;
 const lines=s.code.split('\n');
 const pageBegin=panel?.beginFrame??0;const activeLines=codeLinesAt((s.codeCues??[]).filter(e=>e.beginFrame>=pageBegin),local,panel?.initialCodeLines??s.initialCodeLines);const diagramState=diagramAt(s.diagramCues??[],local);const diagramStage=diagramState.stage??(s.diagramCues?.length?0:stage);
 const caption=s.captions.find(c=>(local-s.leadFrames)/30>=c.start&&(local-s.leadFrames)/30<c.end);
 const statusColor=question?C.blue:s.error||s.panic||s.testFailed?C.red:s.kind==='answer'?C.green:C.muted;
 const showResult=!question&&s.output!==null&&local>=s.resultFrame;
 const resultLabel=s.error?'编译检查结果':s.panic?'运行时异常':s.filename==='终端命令'?'命令执行结果':s.excerpt?'完整程序运行结果':'运行结果';
 const compactResult=(s.output?.trimEnd().split('\n').length??0)>3;
 React.useLayoutEffect(()=>{
  const readySide=document.querySelector('[data-side]');if(!readySide||readySide.clientWidth<350)return;
  const code=document.querySelector('[data-code-inner]');const panel=document.querySelector('[data-code-panel]');
  if(code&&panel){const a=code.getBoundingClientRect(),b=panel.getBoundingClientRect();if(a.bottom>b.bottom-9)throw Error('Code overflows left panel: '+s.key);}
  const result=document.querySelector('[data-result-text]');if(result&&result.scrollHeight>117)throw Error('Result overflows dedicated area: '+s.key);
  const side=document.querySelector('[data-side]');if(side&&side.scrollHeight>side.clientHeight+3)throw Error('Side panel overflow: '+s.key+' '+side.scrollHeight+'/'+side.clientHeight);
  const svg=document.querySelector('svg');if(svg){const b=svg.getBoundingClientRect();for(const t of Array.from(svg.querySelectorAll('text'))){const a=t.getBoundingClientRect();if(a.left<b.left-2||a.right>b.right+2)throw Error('Diagram text overflow: '+s.key+' '+t.textContent);}}
 },[frame,s.key]);
 if(original.key==='kt-01-01')return <><CourseOverview/>{includeAudio&&<Sequence from={s.startFrame+s.leadFrames} durationInFrames={s.speechFrames}><Audio src={staticFile(s.audio)}/></Sequence>}</>;
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:'"Microsoft YaHei", sans-serif'}}>
  <div style={{position:'absolute',top:0,left:0,right:0,height:6,background:C.border}}><div style={{height:6,width:`${(s.startFrame+s.steps[stage])/Timeline.totalFrames*100}%`,background:C.orange}}/></div>
  <div style={{position:'absolute',left:64,top:35,fontSize:25,color:C.orange}}>Kotlin 基础 · {String(s.chapterIndex).padStart(2,'0')}　{s.english}</div>
  <div style={{position:'absolute',right:64,top:39,fontSize:22,color:C.muted}}>零基础课堂 · Kotlin 2.0.21</div>
  <div style={{position:'absolute',left:64,top:87,fontSize:46,fontWeight:600}}>{s.chapter}</div>
  <div style={{position:'absolute',left:64,top:157,fontSize:23,color:statusColor}}>{s.title}{s.kind==='question'?' · 先独立思考':s.kind==='answer'?' · 一起核对':''}</div>
  {s.code?<>
   <div data-code-panel style={{position:'absolute',left:64,top:208,width:1336,height:518,boxSizing:'border-box',borderRadius:18,overflow:'hidden',border:`1px solid ${C.border}`,background:C.panel}}>
    <div style={{height:40,background:'#192a40',display:'flex',alignItems:'center',padding:'0 22px',gap:9}}>{['#ed908a','#efd081','#91d4b0'].map(color=><span key={color} style={{width:10,height:10,borderRadius:10,background:color}}/>)}<span style={{marginLeft:15,fontSize:19,color:C.muted}}>{s.filename}　{s.excerpt?'节选 · 完整 Main.kt 见配套示例':`示例 ${s.section}`}</span></div>
    <div style={{padding:'15px 18px 12px 8px',fontFamily:mono,fontSize:34,lineHeight:'36px'}}><div data-code-inner>{lines.map((r,i)=>{const strength=activeLines.includes(i+1)?1:0;return <div key={i} style={{display:'flex',minHeight:36,borderLeft:`3px solid ${strength>.02?C.orange:'transparent'}`,background:`rgba(255,186,120,${strength*.085})`}}><div style={{width:59,flexShrink:0,textAlign:'right',paddingRight:17,fontSize:21,color:strength>.1?C.orange:'#6e829e'}}>{String(i+1).padStart(2,'0')}</div><div style={{whiteSpace:'pre-wrap',overflowWrap:'anywhere',flex:1}}><Tokens text={r}/></div></div>;})}</div></div>
   </div>
   <div style={{position:'absolute',left:64,top:744,width:1336,height:164,boxSizing:'border-box',border:`1px solid ${showResult&&(s.error||s.panic||s.testFailed)?'#89535c':C.border}`,borderRadius:14,padding:'10px 18px',background:'#15283b'}}>
    <div style={{fontSize:20,lineHeight:'23px',color:statusColor,marginBottom:6}}>{question?'课堂练习':resultLabel}</div>
    <pre data-result-text style={{fontSize:compactResult?30:32,fontFamily:mono,lineHeight:compactResult?'28px':'36px',whiteSpace:'pre-wrap',overflowWrap:'anywhere',margin:0,color:question?C.muted:s.error||s.panic||s.testFailed?C.red:C.green}}>{question?'先预测结果，四秒后一起核对。':showResult?s.output?.trimEnd():'跟随讲解，随后显示结果。'}</pre>
   </div>
  </>:<div style={{position:'absolute',left:64,top:208,width:1336,height:700,boxSizing:'border-box',borderRadius:18,border:`1px solid ${C.border}`,background:C.panel,padding:'46px 48px'}}>
   <div style={{fontSize:26,color:C.orange,marginBottom:25}}>{question?'课堂练习：先预测，再验证':'从具体问题出发，逐步理解'}</div>
   <div style={{fontSize:72,fontWeight:600,lineHeight:1.3,marginBottom:26}}>一小时学习 Kotlin</div>
   <div style={{fontSize:39,color:C.orange,marginBottom:40}}>{s.chapterIndex===1?'从第一行程序开始':'把熟悉的小步骤连起来'}</div>
   {s.notes.map((n,i)=><div key={i} style={{fontSize:34,lineHeight:1.7,marginBottom:14,opacity:i<=stage?1:.22}}><span style={{color:C.orange,marginRight:20}}>{i+1}.</span>{n}</div>)}
  </div>}
  <div data-side style={{position:'absolute',left:1432,right:64,top:215,height:691,display:'flex',flexDirection:'column'}}>
   <div style={{fontSize:23,color:C.blue,marginBottom:22,flexShrink:0}}>{question?'思考提示':s.kind==='answer'?'答案与原因':'本页要点'}</div>
   {s.notes.map((n,i)=><div key={i} style={{fontSize:27,lineHeight:1.5,marginBottom:16,opacity:i<=stage?1:.25,flexShrink:0}}><span style={{color:C.orange}}>• </span>{n}</div>)}
   {!question&&s.diagram&&<div style={{marginTop:18,flexShrink:0}}><DataDiagram type={s.diagram} state={diagramState} stage={diagramStage} sceneKey={s.key} progress={transition}/></div>}
   {pause&&<div style={{marginTop:'auto',border:`1px solid ${C.blue}`,borderRadius:14,padding:20,background:'#133342',textAlign:'center'}}><div style={{fontSize:25,color:C.blue}}>思考时间</div><div style={{fontSize:76,fontFamily:mono,lineHeight:1.2,marginTop:8}}>{Math.max(1,Math.ceil((s.durationFrames-local)/30))}</div><div style={{fontSize:21,color:C.muted,marginTop:8}}>随后核对答案</div></div>}
  </div>
  <div style={{position:'absolute',top:915,left:66,fontSize:17,color:'#7186a1'}}>本章第 {s.sceneIndex+1} / {s.sceneCount} 个片段</div>
  <div style={{position:'absolute',top:942,bottom:0,left:0,right:0,background:'#09111e',borderTop:`1px solid ${C.border}`}}/>
  {includeCaptions&&caption&&<div style={{position:'absolute',left:90,right:90,bottom:53,textAlign:'center',fontSize:40,lineHeight:1.4}}>{caption.text}</div>}
  {includeAudio&&<Sequence from={s.startFrame+s.leadFrames} durationInFrames={s.speechFrames}><Audio src={staticFile(s.audio)}/></Sequence>}
 </AbsoluteFill>;
};
