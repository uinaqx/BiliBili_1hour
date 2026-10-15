import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import data from '../public/timeline.json';
type Caption={start:number;end:number;text:string};
type Scene={key:string;section:string;title:string;chapter:string;english:string;chapterIndex:number;sceneIndex:number;sceneCount:number;startFrame:number;durationFrames:number;speechFrames:number;leadFrames:number;sentenceTailFrames:number;steps:number[];code:string;notes:string[];kind:string;error:string|null;panic:boolean;testFailed:boolean;output:string|null;diagram:string|null;focus:number[];audio:string;captions:Caption[];filename:string;excerpt:boolean;panels:{beginFrame:number;code:string;notes:string[];output:string;filename?:string}[]};
export const Timeline=data as unknown as {totalFrames:number;scenes:Scene[];audioAvailable?:boolean};
const C={bg:'#0b1422',panel:'#122033',border:'#2a3b52',text:'#f0f3f7',muted:'#96a9c0',orange:'#ffba78',blue:'#80d4e7',green:'#a5dfb4',red:'#ff9ca0'};
const mono='"Cascadia Code", Consolas, "Microsoft YaHei", monospace';
const smooth=(x:number)=>{const t=Math.max(0,Math.min(1,x));return t*t*(3-2*t);};
function Tokens({text}:{text:string}){
 const p=/(\/\/.*|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])'|'\w+|\b(?:fn|let|mut|const|if|else|return|for|in|struct|enum|impl|trait|where|use|mod|pub|crate|super|as|Self|self|match|true|false|macro_rules|move|loop)\b|\b(?:String|Vec|HashMap|Option|Some|None|Result|Ok|Err|Box|Rc|Arc|Mutex|RefCell|Copy|Clone|Debug|PartialEq|PartialOrd|bool|char|u\d+|i\d+|usize|f64|T)\b|\b\d+(?:\.\d+)?\b)/g;
 return <>{text.split(p).filter(Boolean).map((v,i)=>{let color=C.text;if(v.startsWith('//'))color=C.muted;else if(v.startsWith('"')||v.startsWith("'"))color=C.green;else if(/^(fn|let|mut|const|if|else|return|for|in|struct|enum|impl|trait|where|use|mod|pub|crate|super|as|Self|self|match|true|false|macro_rules|move|loop)$/.test(v))color=C.orange;else if(/^(String|Vec|HashMap|Option|Some|None|Result|Ok|Err|Box|Rc|Arc|Mutex|RefCell|Copy|Clone|Debug|PartialEq|PartialOrd|bool|char|u\d+|i\d+|usize|f64|T)$/.test(v))color=C.blue;else if(/^\d/.test(v))color='#d6b8f1';return <span key={i} style={{color}}>{v}</span>;})}</>;
}
function Diagram({type,stage}:{type:string;stage:number}){
 const text=(x:number,y:number,label:string,color=C.text,size=23)=><text x={x} y={y} fill={color} fontSize={size} fontFamily='Microsoft YaHei'>{label}</text>;
 const box=(x:number,y:number,w:number,label:string,color=C.blue)=><g><rect x={x} y={y} width={w} height={52} rx={9} stroke={color} fill={C.bg} strokeWidth={2}/>{text(x+12,y+34,label,color)}</g>;
 const arrow=(x:number,y:number,x2:number,y2:number,color=C.muted)=><path d={`M${x} ${y} L${x2} ${y2}`} stroke={color} strokeWidth={3} markerEnd='url(#arr)'/>;
 let body:React.ReactNode;
 if(type==='convert')body=<>{text(0,27,'显式转换，目标类型明确',C.muted)}{box(0,65,142,'u8 · 80')}{arrow(154,90,220,90)}{box(235,65,150,'u32 · 80',C.green)}</>;
 else if(type==='result')body=<>{text(0,27,'同一次操作，成功或失败',C.muted)}{box(45,62,300,'Ok(有效值)',C.green)}{box(45,143,300,'Err(错误说明)',C.red)}</>;
 else if(type==='module'||type==='files')body=<>{text(0,27,type==='files'?'模块声明 → 模块源文件':'模块路径与公开接口',C.muted)}{box(40,60,310,type==='files'?'main.rs':'crate')}{arrow(193,118,193,141)}{box(40,155,310,type==='files'?'grades.rs':'grades::passed',C.green)}</>;
 else if(type==='propagate')body=<>{box(110,10,170,'parse')}{arrow(184,72,87,123,C.green)}{arrow(202,72,307,123,C.red)}{box(0,138,171,'Ok → 继续',C.green)}{box(213,138,174,'Err → 返回',C.red)}</>;
 else if(type==='test')body=<>{text(0,27,'测试的三个步骤',C.muted)}{box(34,57,320,'1  准备测试数据')}{box(34,126,320,'2  执行被测代码')}{box(34,195,320,'3  核对实际与预期',C.green)}</>;
 else if(type==='iterator')body=<>{text(0,27,'按顺序逐项访问',C.muted)}{box(0,64,160,'60     80')}{arrow(174,89,220,89)}{box(234,64,150,'next()')}{text(8,167,'Some(60) → Some(80)',C.green,24)}{text(8,213,'最后返回 None',C.blue,24)}</>;
 else if(type==='pipeline')body=<>{text(0,25,'50、60、80',C.muted,25)}{box(10,54,365,'filter ≥ 60  →  60、80')}{arrow(190,116,190,139)}{box(10,153,365,'map + 1  →  61、81',C.green)}</>;
 else if(type==='box')body=<>{text(0,27,'拥有者 → 堆上的数据',C.muted)}{box(0,76,150,'Box',C.orange)}{arrow(163,102,225,102)}{box(240,76,140,'80',C.green)}{text(0,192,'离开作用域，负责释放',C.muted,23)}</>;
 else if(type==='rc')body=<>{text(0,27,'共享拥有同一份数据',C.muted)}{box(112,57,173,'“小林”',C.green)}{box(0,160,160,'first',C.orange)}<g opacity={stage===3?.25:1}>{box(222,160,163,'second')}{arrow(296,151,238,119)}</g>{arrow(75,151,153,119)}{text(0,253,'共享句柄 ≠ 深拷贝文字',C.muted,23)}</>;
 else if(type==='thread')body=<>{text(0,27,'建立明确的等待关系',C.muted)}{box(30,54,330,'子线程任务完成',C.orange)}{arrow(195,116,195,141)}{box(30,155,330,'join 返回后继续',C.green)}</>;
 else if(type==='channel')body=<>{text(0,27,'通过消息传递结果',C.muted)}{box(0,69,142,'tx · 发送',C.orange)}{arrow(154,95,222,95)}{box(235,69,150,'rx · 接收',C.green)}{text(80,184,'消息：85',C.blue,27)}</>;
 else if(type==='mutex'||type==='shared')body=<>{text(0,27,type==='shared'?'共享拥有 + 互斥修改':'一次只有一方进入修改',C.muted)}{box(4,60,175,type==='shared'?'线程 1':'获得守卫',C.orange)}{box(211,60,174,type==='shared'?'线程 2':'作用域结束')}{arrow(90,122,171,158)}{arrow(296,122,219,158)}{box(75,175,240,type==='shared'?'同一个 Mutex':'自动释放锁',C.green)}</>;
 else if(type==='macro'||type==='expand')body=<>{text(0,27,'调用 → 按规则展开',C.muted)}{box(8,56,370,type==='expand'?'total!(4, 5, 6)':'宏调用')}{arrow(192,118,192,142)}{box(8,158,370,type==='expand'?'0 + 4 + 5 + 6':'展开后的 Rust 代码',C.green)}</>;
 else if(type==='checklist')body=<>{text(0,27,'按各自职责检查',C.muted)}{['fmt  ·  外观','check  ·  编译','test  ·  行为','clippy  ·  补充分析'].map((x,i)=><g key={x}>{box(15,53+i*65,355,x,i<stage?C.green:C.blue)}</g>)}</>;
 else body=<>{text(0,27,'从具体问题出发',C.muted)}{['类型与错误','模块与测试','数据处理与共享','生成代码与检查'].map((x,i)=><g key={x}>{box(15,53+i*65,355,x,i<stage?C.green:C.blue)}</g>)}</>;
 return <svg width='100%' viewBox='0 0 390 335'><defs><marker id='arr' markerWidth='8' markerHeight='8' refX='7' refY='4' orient='auto'><path d='M0 0 L8 4 L0 8Z' fill={C.muted}/></marker></defs>{body}</svg>;
}
export const Course:React.FC<{includeAudio:boolean;includeCaptions:boolean}>=({includeAudio,includeCaptions})=>{
 const frame=useCurrentFrame();const original=Timeline.scenes.find(x=>frame>=x.startFrame&&frame<x.startFrame+x.durationFrames)??Timeline.scenes[Timeline.scenes.length-1];
 const local=frame-original.startFrame;const panel=original.panels?.filter(p=>local>=p.beginFrame).slice(-1)[0];const s=panel?{...original,code:panel.code,notes:panel.notes,output:panel.output,filename:panel.filename??original.filename}:original;let stage=0;s.steps.forEach((v,i)=>{if(local>=v)stage=i;});
 const transition=smooth((local-s.steps[stage])/12);const question=s.kind==='question',pause=question&&local>=s.leadFrames+s.speechFrames+s.sentenceTailFrames;
 const lines=s.code.split('\n');const candidates=s.focus.length?s.focus:lines.map((r,i)=>/let |println!|if |fn |for |return |\.map|\.filter|\.join|match |Some|None|Ok|Err|pub |assert/.test(r)?i+1:0).filter(Boolean);
 const selected=candidates[Math.round(stage*Math.max(0,candidates.length-1)/3)]??1;const previous=candidates[Math.round(Math.max(0,stage-1)*Math.max(0,candidates.length-1)/3)]??selected;
 const caption=s.captions.find(c=>(local-s.leadFrames)/30>=c.start&&(local-s.leadFrames)/30<c.end);
 const statusColor=question?C.blue:s.error||s.panic||s.testFailed?C.red:s.kind==='answer'?C.green:C.muted;
 const showResult=!question&&s.output!==null&&(s.kind==='answer'||stage>=1);
 const resultLabel=s.filename==='终端命令'?'命令用途':s.error?'编译检查结果':s.panic?'运行结果（预期 panic）':s.testFailed?'测试结果（预期失败）':s.chapterIndex===4?'测试结果（摘要）':s.chapterIndex===9?'代码检查结果':s.excerpt?'完整程序运行结果':'运行结果';
 React.useLayoutEffect(()=>{
  const readySide=document.querySelector('[data-side]');if(!readySide||readySide.clientWidth<350)return;
  const code=document.querySelector('[data-code-inner]');const panel=document.querySelector('[data-code-panel]');
  if(code&&panel){const a=code.getBoundingClientRect(),b=panel.getBoundingClientRect();if(a.bottom>b.bottom-9)throw Error('Code overflows left panel: '+s.key);}
  const result=document.querySelector('[data-result-text]');if(result&&result.getBoundingClientRect().bottom>902)throw Error('Result overflows dedicated area: '+s.key);
  const side=document.querySelector('[data-side]');if(side&&side.scrollHeight>side.clientHeight+3)throw Error('Side panel overflow: '+s.key+' '+side.scrollHeight+'/'+side.clientHeight);
 },[frame,s.key]);
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:'"Microsoft YaHei", sans-serif'}}>
  <div style={{position:'absolute',top:0,left:0,right:0,height:6,background:C.border}}><div style={{height:6,width:`${(s.startFrame+s.steps[stage])/Timeline.totalFrames*100}%`,background:C.orange}}/></div>
  <div style={{position:'absolute',left:64,top:35,fontSize:25,color:C.orange}}>Rust 进阶基础 · {String(s.chapterIndex).padStart(2,'0')}　{s.english}</div>
  <div style={{position:'absolute',right:64,top:39,fontSize:22,color:C.muted}}>初学者课堂 · Rust 2024</div>
  <div style={{position:'absolute',left:64,top:87,fontSize:46,fontWeight:600}}>{s.chapter}</div>
  <div style={{position:'absolute',left:64,top:157,fontSize:23,color:statusColor}}>{s.title}{s.kind==='question'?' · 先独立思考':s.kind==='answer'?' · 一起核对':''}</div>
  {s.code?<>
   <div data-code-panel style={{position:'absolute',left:64,top:208,width:1336,height:518,boxSizing:'border-box',borderRadius:18,overflow:'hidden',border:`1px solid ${C.border}`,background:C.panel}}>
    <div style={{height:40,background:'#192a40',display:'flex',alignItems:'center',padding:'0 22px',gap:9}}>{['#ed908a','#efd081','#91d4b0'].map(color=><span key={color} style={{width:10,height:10,borderRadius:10,background:color}}/>)}<span style={{marginLeft:15,fontSize:19,color:C.muted}}>{s.filename}　{s.excerpt?'节选 · 完整程序见配套示例':`示例 ${s.section}`}</span></div>
    <div style={{padding:'15px 18px 12px 8px',fontFamily:mono,fontSize:34,lineHeight:'36px'}}><div data-code-inner>{lines.map((r,i)=>{const strength=i+1===selected?transition:i+1===previous?1-transition:0;return <div key={i} style={{display:'flex',minHeight:36,borderLeft:`3px solid ${strength>.02?C.orange:'transparent'}`,background:`rgba(255,186,120,${strength*.085})`}}><div style={{width:59,flexShrink:0,textAlign:'right',paddingRight:17,fontSize:21,color:strength>.1?C.orange:'#6e829e'}}>{String(i+1).padStart(2,'0')}</div><div style={{whiteSpace:'pre-wrap',overflowWrap:'anywhere',flex:1}}><Tokens text={r}/></div></div>;})}</div></div>
   </div>
   <div style={{position:'absolute',left:64,top:744,width:1336,height:164,boxSizing:'border-box',border:`1px solid ${showResult&&(s.error||s.panic||s.testFailed)?'#89535c':C.border}`,borderRadius:14,padding:'10px 18px',background:'#15283b'}}>
    <div style={{fontSize:20,lineHeight:'23px',color:statusColor,marginBottom:6}}>{question?'课堂练习':resultLabel}</div>
    <pre data-result-text style={{fontSize:32,fontFamily:mono,lineHeight:'36px',whiteSpace:'pre-wrap',overflowWrap:'anywhere',margin:0,color:question?C.muted:s.error||s.panic||s.testFailed?C.red:C.green}}>{question?'先预测结果，四秒后一起核对。':showResult?s.output?.trimEnd():'跟随讲解，随后显示结果。'}</pre>
   </div>
  </>:<div style={{position:'absolute',left:64,top:208,width:1336,height:700,boxSizing:'border-box',borderRadius:18,border:`1px solid ${C.border}`,background:C.panel,padding:'46px 48px'}}>
   <div style={{fontSize:26,color:C.orange,marginBottom:25}}>{s.chapterIndex===0?'从例子出发，逐步理解':'把知识点连成一个工作流程'}</div>
   <div style={{fontSize:72,fontWeight:600,lineHeight:1.3,marginBottom:26}}>Rust 进阶基础</div>
   <div style={{fontSize:39,color:C.orange,marginBottom:40}}>{s.chapterIndex===0?'九个主题，继续学习':'理解规则，再选择工具'}</div>
   {s.notes.map((n,i)=><div key={i} style={{fontSize:34,lineHeight:1.7,marginBottom:14,opacity:i<=stage?1:.22}}><span style={{color:C.orange,marginRight:20}}>{i+1}.</span>{n}</div>)}
  </div>}
  <div data-side style={{position:'absolute',left:1432,right:64,top:215,height:691,display:'flex',flexDirection:'column'}}>
   <div style={{fontSize:23,color:C.blue,marginBottom:22,flexShrink:0}}>{question?'思考提示':s.kind==='answer'?'答案与原因':'本页要点'}</div>
   {s.notes.map((n,i)=><div key={i} style={{fontSize:27,lineHeight:1.5,marginBottom:16,opacity:i<=stage?1:.25,flexShrink:0}}><span style={{color:C.orange}}>• </span>{n}</div>)}
   {!question&&s.diagram&&<div style={{marginTop:18,flexShrink:0}}><Diagram type={s.diagram} stage={stage}/></div>}
   {pause&&<div style={{marginTop:'auto',border:`1px solid ${C.blue}`,borderRadius:14,padding:20,background:'#133342',textAlign:'center'}}><div style={{fontSize:25,color:C.blue}}>思考时间</div><div style={{fontSize:76,fontFamily:mono,lineHeight:1.2,marginTop:8}}>{Math.max(1,Math.ceil((s.durationFrames-local)/30))}</div><div style={{fontSize:21,color:C.muted,marginTop:8}}>随后核对答案</div></div>}
  </div>
  <div style={{position:'absolute',top:915,left:66,fontSize:17,color:'#7186a1'}}>本章第 {s.sceneIndex+1} / {s.sceneCount} 个片段 · 理解一步，再前进一步</div>
  <div style={{position:'absolute',top:942,bottom:0,left:0,right:0,background:'#09111e',borderTop:`1px solid ${C.border}`}}/>
  {includeCaptions&&caption&&<div style={{position:'absolute',left:90,right:90,bottom:53,textAlign:'center',fontSize:40,lineHeight:1.4}}>{caption.text}</div>}
  {includeAudio&&<Sequence from={s.startFrame+s.leadFrames} durationInFrames={s.speechFrames}><Audio src={staticFile(s.audio)}/></Sequence>}
 </AbsoluteFill>;
};
