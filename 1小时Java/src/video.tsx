import React from 'react';
import {DataDiagram} from './diagrams';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import data from '../public/timeline.json';
type Caption={start:number;end:number;text:string};
type Scene={key:string;section:string;title:string;chapter:string;english:string;chapterIndex:number;sceneIndex:number;sceneCount:number;startFrame:number;durationFrames:number;speechFrames:number;leadFrames:number;sentenceTailFrames:number;steps:number[];code:string;notes:string[];kind:string;error:string|null;panic:boolean;testFailed:boolean;output:string|null;diagram:string|null;focus:number[];audio:string;captions:Caption[];filename:string;excerpt:boolean;panels:{beginFrame:number;code:string;notes:string[];output:string;filename?:string}[]};
export const Timeline=data as unknown as {totalFrames:number;scenes:Scene[];audioAvailable?:boolean};
const C={bg:'#0b1422',panel:'#122033',border:'#2a3b52',text:'#f0f3f7',muted:'#96a9c0',orange:'#ffba78',blue:'#80d4e7',green:'#a5dfb4',red:'#ff9ca0'};
const mono='"Cascadia Code", Consolas, "Microsoft YaHei", monospace';
const smooth=(x:number)=>{const t=Math.max(0,Math.min(1,x));return t*t*(3-2*t);};
function Tokens({text}:{text:string}){
 const names='int|double|float|long|short|byte|boolean|char|void|final|if|else|return|for|while|do|switch|case|default|break|continue|class|public|private|protected|static|this|try|catch|throw|new|import|true|false';
 const keywords=new RegExp('^(?:'+names+')$');
 const types=/^(String|Scanner|ArrayList|HashMap|Student|Main|Integer|NumberFormatException|IllegalArgumentException)$/;
 const p=new RegExp("(//.*|\"(?:\\\\.|[^\"\\\\])*\"|'(?:\\\\.|[^'\\\\])'|\\b(?:"+names+"|String|Scanner|ArrayList|HashMap|Student|Main|Integer|NumberFormatException|IllegalArgumentException)\\b|\\b\\d+(?:\\.\\d+)?\\b)",'g');
 return <>{text.split(p).filter(Boolean).map((v,i)=>{let color=C.text;if(v.startsWith('//'))color=C.muted;else if(v.startsWith('"')||v.startsWith("'"))color=C.green;else if(keywords.test(v))color=C.orange;else if(types.test(v))color=C.blue;else if(/^\d/.test(v))color='#d6b8f1';return <span key={i} style={{color}}>{v}</span>;})}</>;
}
export const Course:React.FC<{includeAudio:boolean;includeCaptions:boolean}>=({includeAudio,includeCaptions})=>{
 const frame=useCurrentFrame();const original=Timeline.scenes.find(x=>frame>=x.startFrame&&frame<x.startFrame+x.durationFrames)??Timeline.scenes[Timeline.scenes.length-1];
 const local=frame-original.startFrame;const panel=original.panels?.filter(p=>local>=p.beginFrame).slice(-1)[0];const s=panel?{...original,code:panel.code,notes:panel.notes,output:panel.output,filename:panel.filename??original.filename}:original;let stage=0;s.steps.forEach((v,i)=>{if(local>=v)stage=i;});
 const transition=smooth((local-s.steps[stage])/12);const question=s.kind==='question',pause=question&&local>=s.leadFrames+s.speechFrames+s.sentenceTailFrames;
 const lines=s.code.split('\n');const candidates=s.focus.length?s.focus:lines.map((r,i)=>/System.out|nextInt|nextLine|class |return |if |for |while |score|value|throw|catch|public|private/.test(r)?i+1:0).filter(Boolean);
 const selected=candidates[Math.round(stage*Math.max(0,candidates.length-1)/3)]??1;const previous=candidates[Math.round(Math.max(0,stage-1)*Math.max(0,candidates.length-1)/3)]??selected;
 const caption=s.captions.find(c=>(local-s.leadFrames)/30>=c.start&&(local-s.leadFrames)/30<c.end);
 const statusColor=question?C.blue:s.error||s.panic||s.testFailed?C.red:s.kind==='answer'?C.green:C.muted;
 const showResult=!question&&s.output!==null&&(s.kind==='answer'||stage>=1);
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
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:'"Microsoft YaHei", sans-serif'}}>
  <div style={{position:'absolute',top:0,left:0,right:0,height:6,background:C.border}}><div style={{height:6,width:`${(s.startFrame+s.steps[stage])/Timeline.totalFrames*100}%`,background:C.orange}}/></div>
  <div style={{position:'absolute',left:64,top:35,fontSize:25,color:C.orange}}>Java 基础 · {String(s.chapterIndex).padStart(2,'0')}　{s.english}</div>
  <div style={{position:'absolute',right:64,top:39,fontSize:22,color:C.muted}}>零基础课堂 · Java 21</div>
  <div style={{position:'absolute',left:64,top:87,fontSize:46,fontWeight:600}}>{s.chapter}</div>
  <div style={{position:'absolute',left:64,top:157,fontSize:23,color:statusColor}}>{s.title}{s.kind==='question'?' · 先独立思考':s.kind==='answer'?' · 一起核对':''}</div>
  {s.code?<>
   <div data-code-panel style={{position:'absolute',left:64,top:208,width:1336,height:518,boxSizing:'border-box',borderRadius:18,overflow:'hidden',border:`1px solid ${C.border}`,background:C.panel}}>
    <div style={{height:40,background:'#192a40',display:'flex',alignItems:'center',padding:'0 22px',gap:9}}>{['#ed908a','#efd081','#91d4b0'].map(color=><span key={color} style={{width:10,height:10,borderRadius:10,background:color}}/>)}<span style={{marginLeft:15,fontSize:19,color:C.muted}}>{s.filename}　{s.excerpt?'节选 · 完整 Main.java 见配套示例':`示例 ${s.section}`}</span></div>
    <div style={{padding:'15px 18px 12px 8px',fontFamily:mono,fontSize:34,lineHeight:'36px'}}><div data-code-inner>{lines.map((r,i)=>{const strength=i+1===selected?transition:i+1===previous?1-transition:0;return <div key={i} style={{display:'flex',minHeight:36,borderLeft:`3px solid ${strength>.02?C.orange:'transparent'}`,background:`rgba(255,186,120,${strength*.085})`}}><div style={{width:59,flexShrink:0,textAlign:'right',paddingRight:17,fontSize:21,color:strength>.1?C.orange:'#6e829e'}}>{String(i+1).padStart(2,'0')}</div><div style={{whiteSpace:'pre-wrap',overflowWrap:'anywhere',flex:1}}><Tokens text={r}/></div></div>;})}</div></div>
   </div>
   <div style={{position:'absolute',left:64,top:744,width:1336,height:164,boxSizing:'border-box',border:`1px solid ${showResult&&(s.error||s.panic||s.testFailed)?'#89535c':C.border}`,borderRadius:14,padding:'10px 18px',background:'#15283b'}}>
    <div style={{fontSize:20,lineHeight:'23px',color:statusColor,marginBottom:6}}>{question?'课堂练习':resultLabel}</div>
    <pre data-result-text style={{fontSize:compactResult?30:32,fontFamily:mono,lineHeight:compactResult?'28px':'36px',whiteSpace:'pre-wrap',overflowWrap:'anywhere',margin:0,color:question?C.muted:s.error||s.panic||s.testFailed?C.red:C.green}}>{question?'先预测结果，四秒后一起核对。':showResult?s.output?.trimEnd():'跟随讲解，随后显示结果。'}</pre>
   </div>
  </>:<div style={{position:'absolute',left:64,top:208,width:1336,height:700,boxSizing:'border-box',borderRadius:18,border:`1px solid ${C.border}`,background:C.panel,padding:'46px 48px'}}>
   <div style={{fontSize:26,color:C.orange,marginBottom:25}}>{question?'课堂练习：先预测，再验证':'从具体问题出发，逐步理解'}</div>
   <div style={{fontSize:72,fontWeight:600,lineHeight:1.3,marginBottom:26}}>一小时学习 Java</div>
   <div style={{fontSize:39,color:C.orange,marginBottom:40}}>{s.chapterIndex===0?'从第一行程序开始':'把熟悉的小步骤连起来'}</div>
   {s.notes.map((n,i)=><div key={i} style={{fontSize:34,lineHeight:1.7,marginBottom:14,opacity:i<=stage?1:.22}}><span style={{color:C.orange,marginRight:20}}>{i+1}.</span>{n}</div>)}
  </div>}
  <div data-side style={{position:'absolute',left:1432,right:64,top:215,height:691,display:'flex',flexDirection:'column'}}>
   <div style={{fontSize:23,color:C.blue,marginBottom:22,flexShrink:0}}>{question?'思考提示':s.kind==='answer'?'答案与原因':'本页要点'}</div>
   {s.notes.map((n,i)=><div key={i} style={{fontSize:27,lineHeight:1.5,marginBottom:16,opacity:i<=stage?1:.25,flexShrink:0}}><span style={{color:C.orange}}>• </span>{n}</div>)}
   {!question&&s.diagram&&<div style={{marginTop:18,flexShrink:0}}><DataDiagram type={s.diagram} stage={stage} sceneKey={s.key} progress={transition}/></div>}
   {pause&&<div style={{marginTop:'auto',border:`1px solid ${C.blue}`,borderRadius:14,padding:20,background:'#133342',textAlign:'center'}}><div style={{fontSize:25,color:C.blue}}>思考时间</div><div style={{fontSize:76,fontFamily:mono,lineHeight:1.2,marginTop:8}}>{Math.max(1,Math.ceil((s.durationFrames-local)/30))}</div><div style={{fontSize:21,color:C.muted,marginTop:8}}>随后核对答案</div></div>}
  </div>
  <div style={{position:'absolute',top:915,left:66,fontSize:17,color:'#7186a1'}}>本章第 {s.sceneIndex+1} / {s.sceneCount} 个片段</div>
  <div style={{position:'absolute',top:942,bottom:0,left:0,right:0,background:'#09111e',borderTop:`1px solid ${C.border}`}}/>
  {includeCaptions&&caption&&<div style={{position:'absolute',left:90,right:90,bottom:53,textAlign:'center',fontSize:40,lineHeight:1.4}}>{caption.text}</div>}
  {includeAudio&&<Sequence from={s.startFrame+s.leadFrames} durationInFrames={s.speechFrames}><Audio src={staticFile(s.audio)}/></Sequence>}
 </AbsoluteFill>;
};
