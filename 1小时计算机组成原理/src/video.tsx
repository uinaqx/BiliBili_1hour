import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {C,Panel,VisualCanvas} from './visuals';
import data from '../public/timeline.json';
type Caption={start:number;end:number;text:string};
type Scene={key:string;title:string;chapter:string;english:string;chapterIndex:number;sceneIndex:number;sceneCount:number;startFrame:number;durationFrames:number;speechFrames:number;leadFrames:number;sentenceTailFrames:number;steps:number[];kind:string;notes:string[];audio:string;captions:Caption[];visualPanels:Panel[]};
export const Timeline=data as unknown as {totalFrames:number;scenes:Scene[];audioAvailable?:boolean};
const smooth=(x:number)=>{const t=Math.max(0,Math.min(1,x));return t*t*(3-2*t);};
export const Course:React.FC<{includeAudio:boolean;includeCaptions:boolean}>=({includeAudio,includeCaptions})=>{
 const frame=useCurrentFrame();const s=Timeline.scenes.find(s=>frame>=s.startFrame&&frame<s.startFrame+s.durationFrames)??Timeline.scenes[Timeline.scenes.length-1];const local=frame-s.startFrame;let stage=0;s.steps.forEach((f,i)=>{if(local>=f)stage=i;});const p=s.visualPanels[stage];
 const transition=smooth((local-s.steps[stage])/12);const question=s.kind==='question',answer=s.kind==='answer';const pause=question&&local>=s.leadFrames+s.speechFrames+s.sentenceTailFrames;const caption=s.captions.find(c=>(local-s.leadFrames)/30>=c.start&&(local-s.leadFrames)/30<c.end);
 React.useLayoutEffect(()=>{
  const side=document.querySelector('[data-side]');if(!side||side.clientWidth<350)return;
  if(side.scrollHeight>side.clientHeight+3)throw Error('Side panel overflow: '+s.key+' '+side.scrollHeight+'/'+side.clientHeight);
  const footer=document.querySelector('[data-footer]');if(footer&&footer.scrollHeight>112)throw Error('Conclusion overflow: '+s.key);
 },[frame,s.key]);
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:'Microsoft YaHei, sans-serif'}}>
  <div style={{position:'absolute',top:0,left:0,right:0,height:6,background:C.border}}><div style={{height:6,width:`${(s.startFrame+s.steps[stage])/Timeline.totalFrames*100}%`,background:C.orange}}/></div>
  <div style={{position:'absolute',left:64,top:35,fontSize:25,color:C.orange}}>计算机组成原理 · {String(s.chapterIndex).padStart(2,'0')}　{s.english}</div>
  <div style={{position:'absolute',right:64,top:39,fontSize:22,color:C.muted}}>初学者课堂 · 图解与推演</div>
  <div style={{position:'absolute',left:64,top:87,fontSize:46,fontWeight:600}}>{s.chapter}</div>
  <div style={{position:'absolute',left:64,top:157,fontSize:23,color:question?C.blue:answer?C.green:C.muted}}>{s.title}{question?' · 先独立思考':answer?' · 一起核对':''}</div>
  <div style={{position:'absolute',left:64,top:208,width:1336,height:518,borderRadius:18,overflow:'hidden',boxSizing:'border-box',border:`1px solid ${C.border}`,background:C.panel}}>
   <div style={{height:43,background:'#192a40',display:'flex',alignItems:'center',padding:'0 23px',gap:9}}>{['#ed908a','#efd081','#91d4b0'].map(color=><span key={color} style={{width:10,height:10,borderRadius:10,background:color}}/>)}<span style={{marginLeft:15,fontSize:23,color:question?C.blue:C.muted}}>{p.title}</span><span style={{marginLeft:'auto',fontSize:20,color:C.muted}}>图示 {s.key}　{stage+1} / 4</span></div>
   <div style={{position:'absolute',left:24,right:24,top:58,bottom:12}}><VisualCanvas panel={p} stage={stage} progress={transition}/></div>
  </div>
  <div style={{position:'absolute',left:64,top:744,width:1336,height:164,boxSizing:'border-box',border:`1px solid ${C.border}`,borderRadius:14,padding:'10px 18px',background:'#15283b'}}>
   <div style={{fontSize:20,lineHeight:'25px',color:question?C.blue:answer?C.green:C.muted,marginBottom:9}}>{question?'课堂练习':answer?'答案与原因':'推演与结论'}</div>
   <div data-footer style={{fontSize:32,lineHeight:'39px',color:question?C.muted:C.green}}>{pause?'请先独立作答，随后一起核对。':p.footer}</div>
  </div>
  <div data-side style={{position:'absolute',left:1432,right:64,top:215,height:691,display:'flex',flexDirection:'column'}}>
   <div style={{fontSize:23,color:C.blue,marginBottom:20,flexShrink:0}}>{question?'思考提示':'关键概念'}</div>
   {s.notes.map((n,i)=><div key={i} style={{fontSize:27,lineHeight:1.5,marginBottom:17,opacity:i<=stage?1:.28,flexShrink:0}}><span style={{color:C.orange}}>• </span>{n}</div>)}
   {!question&&<div style={{marginTop:22,borderTop:`1px solid ${C.border}`,paddingTop:20}}>{s.visualPanels.map((v,i)=><div key={i} style={{display:'flex',gap:13,marginBottom:15,color:i===stage?C.orange:C.muted,fontSize:23,lineHeight:1.4}}><span style={{flexShrink:0}}>{i+1}.</span><span>{v.title}</span></div>)}</div>}
   {pause&&<div style={{marginTop:'auto',border:`1px solid ${C.blue}`,borderRadius:14,padding:20,background:'#133342',textAlign:'center'}}><div style={{fontSize:25,color:C.blue}}>思考时间</div><div style={{fontSize:76,lineHeight:1.2,marginTop:8}}>{Math.max(1,Math.ceil((s.durationFrames-local)/30))}</div><div style={{fontSize:21,color:C.muted,marginTop:8}}>随后核对答案</div></div>}
  </div>
  <div style={{position:'absolute',top:915,left:66,fontSize:17,color:'#7186a1'}}>本章第 {s.sceneIndex+1} / {s.sceneCount} 个片段 · 理解一步，再前进一步</div>
  <div style={{position:'absolute',top:942,bottom:0,left:0,right:0,background:'#09111e',borderTop:`1px solid ${C.border}`}}/>
  {includeCaptions&&caption&&<div style={{position:'absolute',left:90,right:90,bottom:53,textAlign:'center',fontSize:40,lineHeight:1.4}}>{caption.text}</div>}
  {includeAudio&&<Sequence from={s.startFrame+s.leadFrames} durationInFrames={s.speechFrames}><Audio src={staticFile(s.audio)}/></Sequence>}
 </AbsoluteFill>;
};
