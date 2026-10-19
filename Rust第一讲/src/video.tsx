import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import data from '../public/timeline.json';
import project from '../project.json';
type Caption={start:number;end:number;text:string};
type Scene={key:string;title:string;chapter:string;english:string;chapterIndex:number;sceneIndex:number;sceneCount:number;startFrame:number;durationFrames:number;speechFrames:number;leadFrames:number;steps:number[];code:string;notes:string[];kind:string;error:string|null;panic:boolean;output:string|null;diagram:string|null;focus:number[];audio:string;captions:Caption[];section:string;panels:{beginFrame:number;code:string;notes:string[];output:string}[]};
export const Timeline=data as unknown as {totalFrames:number;scenes:Scene[];audioAvailable?:boolean};
const C={bg:'#0b1422',panel:'#122033',border:'#2a3b52',text:'#f0f3f7',muted:'#96a9c0',orange:'#ffba78',blue:'#80d4e7',green:'#a5dfb4',red:'#ff9ca0'};
const mono='"Cascadia Code", Consolas, "Microsoft YaHei", monospace';
const smooth=(x:number)=>{const t=Math.max(0,Math.min(1,x));return t*t*(3-2*t);};
function Tokens({text}:{text:string}){
 const p=/(\/\/.*|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])'|'\w+|\b(?:fn|let|mut|const|if|else|return|for|in|struct|enum|impl|trait|where|use|as|Self|self|match|true|false)\b|\b(?:String|Vec|HashMap|Option|Some|None|Copy|Clone|Debug|PartialEq|PartialOrd|bool|char|u\d+|i\d+|usize|f64|T)\b|\b\d+(?:\.\d+)?\b)/g;
 return <>{text.split(p).filter(Boolean).map((v,i)=>{let color=C.text;if(v.startsWith('//'))color=C.muted;else if(v.startsWith('"')||v.startsWith("'"))color=C.green;else if(/^(fn|let|mut|const|if|else|return|for|in|struct|enum|impl|trait|where|use|as|Self|self|match|true|false)$/.test(v))color=C.orange;else if(/^(String|Vec|HashMap|Option|Some|None|Copy|Clone|Debug|PartialEq|PartialOrd|bool|char|u\d+|i\d+|usize|f64|T)$/.test(v))color=C.blue;else if(/^\d/.test(v))color='#d6b8f1';return <span key={i} style={{color}}>{v}</span>;})}</>;
}
function Diagram({type,stage}:{type:string;stage:number}){
 const t=(x:number,y:number,text:string,color=C.text,size=23)=><text x={x} y={y} fill={color} fontSize={size} fontFamily='Microsoft YaHei'>{text}</text>;
 const box=(x:number,y:number,w:number,label:string,color:string,opacity=1)=><g opacity={opacity}><rect x={x} y={y} width={w} height={53} rx={10} stroke={color} fill={C.bg} strokeWidth={2}/>{t(x+11,y+34,label,color,23)}</g>;
 if(type==='function')return <svg width='100%' viewBox='0 0 390 205'>{t(4,27,'输入 → 处理 → 结果',C.muted,22)}{box(8,60,143,'80 与 5',C.blue)}{box(236,60,145,'85',C.green)}<path d='M162 87 H225 M216 79 L225 87 L216 95' stroke={C.orange} strokeWidth={3} fill='none'/>{t(52,163,'add_bonus：增加奖励分',C.orange,23)}</svg>;
 if(type==='student'||type==='student-changing')return <svg width='100%' viewBox='0 0 390 218'>{t(4,28,'把相关信息放在一起',C.muted,22)}<rect x={8} y={51} width={374} height={137} rx={13} fill={C.bg} stroke={C.orange} strokeWidth={2}/>{t(23,84,'Student',C.orange,25)}{t(23,130,'name：小林',C.green,24)}{t(23,166,type==='student-changing'&&stage>=3?'score：85':'score：80',C.blue,24)}</svg>;
 if(type==='states'||type==='option')return <svg width='100%' viewBox='0 0 390 230'>{t(4,27,type==='states'?'当前只处于一种情况':'有值，与没有值',C.muted,22)}{type==='states'?<>{box(8,48,374,'还没交',C.muted,.7)}{box(8,108,374,'批改中',C.muted,.7)}{box(8,168,374,'已出分：85',C.green)}</>:<>{box(8,66,374,'Some(85)：有成绩',C.green)}{box(8,139,374,'None：还没有成绩',C.blue)}</>}</svg>;
 if(type==='vec')return <svg width='100%' viewBox='0 0 390 198'>{t(4,27,'成绩与位置',C.muted,22)}{[80,85,90].map((v,i)=><g key={v}>{box(8+i*129,58,115,String(v),i===1?C.orange:C.blue)}{t(48+i*129,148,String(i),C.muted,22)}</g>)}{t(15,190,'位置从 0 开始',C.green,23)}</svg>;
 if(type==='vec-changing'){const values=stage===2?[80,85,90]:[80,85];return <svg width='100%' viewBox='0 0 390 218'>{t(4,27,stage>=3?'pop 后，长度回到 2':stage===2?'push 后，长度变成 3':'最初有两个成绩',C.muted,22)}{values.map((v,i)=><g key={v}>{box(8+i*129,60,115,String(v),C.blue)}{t(47+i*129,145,String(i),C.muted,22)}</g>)}{stage>=3&&t(10,193,'取出的末尾成绩：90',C.orange,23)}</svg>;}
 if(type==='hashmap')return <svg width='100%' viewBox='0 0 390 207'>{t(4,27,'姓名 → 对应的值',C.muted,22)}{box(8,56,166,'小林',C.orange)}{box(225,56,158,'80',C.green)}{box(8,125,166,'小周',C.orange)}{box(225,125,158,'90',C.green)}<path d='M181 83 H216 M181 152 H216' stroke={C.blue} strokeWidth={3}/></svg>;
 if(type==='hashmap-update')return <svg width='100%' viewBox='0 0 390 183'>{t(4,27,'同一个键更新原来的值',C.muted,22)}{box(8,62,166,'小林',C.orange)}{box(225,62,158,stage>0?'85':'80',C.green)}<path d='M181 89 H216' stroke={C.blue} strokeWidth={3}/>{t(10,167,'不增加第二条同名记录',C.blue,22)}</svg>;
 if(type==='counts')return <svg width='100%' viewBox='0 0 390 208'>{t(4,27,'遍历完成后的计数',C.muted,22)}{box(8,58,165,'小林',C.orange)}{box(225,58,158,'2 次',C.green)}{box(8,126,165,'小周',C.orange)}{box(225,126,158,'1 次',C.green)}<path d='M181 85 H216 M181 153 H216' stroke={C.blue} strokeWidth={3}/></svg>;
 if(type==='generic')return <svg width='100%' viewBox='0 0 390 215'>{t(4,27,'同一种做法，不同类型',C.muted,22)}{box(110,52,170,'类型位置 T',C.orange)}{box(8,139,170,'整数',C.blue)}{box(212,139,170,'文字',C.green)}<path d='M185 110 L94 131 M205 110 L290 131' stroke={C.muted} strokeWidth={2}/></svg>;
 if(type==='trait')return <svg width='100%' viewBox='0 0 390 215'>{t(4,27,'共同约定：给出介绍',C.muted,22)}{box(8,63,170,'学生',C.blue)}{box(212,63,170,'课程',C.orange)}{box(54,151,283,'提供 introduction',C.green)}<path d='M92 122 L159 144 M292 122 L237 144' stroke={C.muted} strokeWidth={2}/></svg>;
 if(type==='utf8')return <svg width='100%' viewBox='0 0 390 205'>
  {t(4,28,'同一段文字：中 A',C.muted)}
  {[0,1,2,3].map(i=><g key={i}><rect x={8+i*96} y={53} width={87} height={56} rx={8} fill={i<3?'#164053':'#4b3825'} stroke={i<3?C.blue:C.orange}/>{t(22+i*96,89,['E4','B8','AD','41'][i])}{t(8+i*96,137,String(i),C.muted,20)}</g>)}
  {t(92,174,'中：3 字节',C.blue)}{t(301,174,'A：1',C.orange,21)}
  {stage>=2&&t(5,204,'len = 4，常见字符数 = 2',C.green,21)}
 </svg>;
 if(type==='utf8-hello')return <svg width='100%' viewBox='0 0 390 209'>{t(4,27,'这次的文字：你好',C.muted,22)}{['E4','BD','A0','E5','A5','BD'].map((v,i)=><g key={i}><rect x={5+i*65} y={61} width={59} height={54} rx={7} fill={i<3?'#164053':'#4b3825'} stroke={i<3?C.blue:C.orange}/>{t(13+i*65,95,v,C.text,23)}</g>)}{t(40,155,'你：3 字节',C.blue,22)}{t(226,155,'好：3 字节',C.orange,22)}{t(7,204,'len = 6，chars 得到 2 项',C.green,22)}</svg>;
 if(['conflict','nll','dangling','lifetime','lifetime-invalid','scope'].includes(type)){
  const borrow=type==='conflict'||type==='nll',invalid=['conflict','dangling','lifetime-invalid'].includes(type);
  const bars=borrow?[{label:'读取借用',x:108,w:invalid?265:120,c:C.blue},{label:'修改数据',x:258,w:113,c:C.orange}]:type==='scope'?[{label:'拥有数据',x:108,w:203,c:C.orange},{label:'清理以后',x:322,w:50,c:C.red}]:[{label:'原数据',x:108,w:invalid?153:265,c:C.orange},{label:'使用引用',x:invalid?286:180,w:invalid?84:128,c:invalid?C.red:C.blue}];
  return <svg width='100%' viewBox='0 0 390 210'>
   {t(4,28,borrow?'先完成读取，再修改':'使用时，原数据要有效',C.muted,22)}
   {bars.map((b,i)=><g key={b.label}>{t(3,76+i*56,b.label,C.muted,21)}<rect x={b.x} y={54+i*56} width={stage===0?Math.min(65,b.w):b.w} height={29} rx={6} fill={b.c} opacity={.9}/></g>)}
   <path d='M108 164 H370 M360 156 L370 164 L360 172' stroke={C.muted} strokeWidth={2} fill='none'/>
   {t(5,204,invalid?'这里的使用发生了冲突':type==='scope'?'范围结束后自动清理':'在有效范围里完成使用',invalid?C.red:C.green,22)}
  </svg>;
 }
 if(type==='copy')return <svg width='100%' viewBox='0 0 390 185'>{t(4,25,'整数复制成两个值',C.muted,22)}{box(7,53,171,'score = 80',C.orange)}{box(213,53,171,'another = 80',C.blue,stage>0?1:.25)}{t(22,162,'两个名字都可以继续使用',C.green,22)}</svg>;
 if(type==='shared')return <svg width='100%' viewBox='0 0 390 238'>{t(4,27,'多个引用一起读取',C.muted,22)}{box(111,51,170,'“小林”',C.green)}{box(8,157,163,'first',C.blue,stage>0?1:.3)}{box(219,157,163,'second',C.blue,stage>1?1:.3)}<path d='M87 150 L156 110 M301 150 L236 110' stroke={C.blue} strokeWidth={3} strokeDasharray='6 5'/>{t(26,237,'拥有者仍然是 name',C.orange,22)}</svg>;
 const move=type==='move'||type==='call',clone=type==='clone';
 const owner=type==='call'?'main 的 name':'name';const next=type==='move'?'another':type==='call'?'函数参数':type==='clone'?'another':'引用';
 return <svg width='100%' viewBox='0 0 390 238'>
  <defs><marker id='arrow' viewBox='0 0 10 10' refX='8' refY='5' markerWidth='6' markerHeight='6' orient='auto'><path d='M0 0 L10 5 L0 10Z' fill='context-stroke'/></marker></defs>
  {t(4,25,clone?'明确复制一份':move?'交出数据的管理责任':'借来使用，拥有者不变',C.muted,22)}
  {box(6,48,141,owner,C.orange,move&&stage>0?.3:1)}{box(229,68,153,'“小林”',C.green)}
  {!(move&&stage>0)&&<path d='M150 74 C180 74 192 92 220 92' stroke={C.orange} strokeWidth={3} markerEnd='url(#arrow)' fill='none'/>}
  {stage>0&&<>{box(6,156,141,next,move||clone?C.orange:C.blue)}{clone?<>{box(229,156,153,'独立副本',C.blue)}<path d='M150 183 H220' stroke={C.blue} strokeWidth={3} markerEnd='url(#arrow)'/></>:<path d='M150 183 C190 183 178 108 220 108' stroke={move?C.orange:C.blue} strokeWidth={3} strokeDasharray={move?undefined:'6 5'} markerEnd='url(#arrow)' fill='none'/>}</>}
  {t(5,235,move?'原来的值不能继续使用':clone?'两个独立拥有者':type==='mut-borrow'?'&mut：借来修改':'&：借来读取',move?C.muted:C.blue,21)}
 </svg>;
}
export const Course:React.FC<{includeAudio:boolean;includeCaptions:boolean}>=({includeAudio,includeCaptions})=>{
 const frame=useCurrentFrame();const original=Timeline.scenes.find(x=>frame>=x.startFrame&&frame<x.startFrame+x.durationFrames)??Timeline.scenes[Timeline.scenes.length-1];
 const local=frame-original.startFrame;const panel=original.panels?.filter(p=>local>=p.beginFrame).slice(-1)[0];const s=panel?{...original,code:panel.code,notes:panel.notes,output:panel.output}:original;let stage=0;s.steps.forEach((v,i)=>{if(local>=v)stage=i;});
 const transition=smooth((local-s.steps[stage])/12);const question=s.kind==='question',pause=question&&local>=s.leadFrames+s.speechFrames;
 const lines=s.code.split('\n');const candidates=s.focus.length?s.focus:lines.map((r,i)=>/let |println!|if |fn |for |return |\.push|\.insert|\.get|\.clone|match |Some|None/.test(r)?i+1:0).filter(Boolean);
 const selected=candidates[Math.round(stage*Math.max(0,candidates.length-1)/3)]??1;const previous=candidates[Math.round(Math.max(0,stage-1)*Math.max(0,candidates.length-1)/3)]??selected;
 const caption=s.captions.find(c=>(local-s.leadFrames)/30>=c.start&&(local-s.leadFrames)/30<c.end);
 const status=question?'先自己想一想':s.kind==='answer'?'一起看答案':s.error?'这段代码需要修改':s.panic?'运行时会失败':s.code?'跟着例子看':'从具体问题开始';
 const statusColor=question?C.blue:s.error||s.panic?C.red:s.kind==='answer'?C.green:C.muted;
 const hasCode=Boolean(s.code);
 React.useLayoutEffect(()=>{
  const code=document.querySelector('[data-code-lines]');const side=document.querySelector('[data-side-panel]');
  if(code&&code.getBoundingClientRect().width>1000){if(code.getBoundingClientRect().bottom>915)throw new Error(`${s.key}: code overflows vertically`);const count=code.querySelector('[data-row-container]')?.getBoundingClientRect().height??0;if(count/36>16.05)throw new Error(`${s.key}: more than 16 visible code lines (${count/36})`);}
  if(side&&side.clientWidth>350&&side.scrollHeight>side.clientHeight+4)throw new Error(`${s.key}: annotations overflow (${side.scrollHeight}/${side.clientHeight})`);
 },[frame,s.key]);
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:'"Microsoft YaHei", sans-serif'}}>
  <div style={{position:'absolute',top:0,left:0,right:0,height:6,background:C.border}}><div style={{height:6,width:`${(s.startFrame+s.steps[stage])/Timeline.totalFrames*100}%`,background:C.orange}}/></div>
  <div style={{position:'absolute',left:64,top:35,fontSize:25,color:C.orange}}>{project.languageLabel} · {String(s.chapterIndex).padStart(2,'0')}　{s.chapter}</div>
  <div style={{position:'absolute',right:64,top:39,fontSize:22,color:C.muted}}>{project.rightLabel}</div>
  <div style={{position:'absolute',left:64,top:87,fontSize:46,fontWeight:600}}>{s.title}</div>
  <div style={{position:'absolute',left:64,top:157,fontSize:22,color:statusColor}}>{status}</div>
  <div style={{position:'absolute',left:64,top:208,width:1336,height:700,borderRadius:18,overflow:'hidden',border:`1px solid ${C.border}`,background:C.panel}}>
   {hasCode?<><div style={{height:42,background:'#192a40',display:'flex',alignItems:'center',padding:'0 22px',gap:9}}>{['#ed908a','#efd081','#91d4b0'].map(color=><span key={color} style={{width:10,height:10,borderRadius:10,background:color}}/>)}<span style={{marginLeft:15,fontSize:19,color:C.muted}}>{s.kind==='question'?'课堂练习':'示例代码'}　{s.section}</span></div>
    <div data-code-lines style={{padding:'17px 18px 10px 8px',fontFamily:mono,fontSize:34,lineHeight:'36px'}}><div data-row-container>{lines.map((r,i)=>{const strength=i+1===selected?transition:i+1===previous?1-transition:0;return <div key={i} style={{display:'flex',minHeight:36,borderLeft:`3px solid ${strength>.02?C.orange:'transparent'}`,background:`rgba(255,186,120,${strength*.085})`}}><div style={{width:59,flexShrink:0,textAlign:'right',paddingRight:17,fontSize:21,color:strength>.1?C.orange:'#6e829e'}}>{String(i+1).padStart(2,'0')}</div><div style={{whiteSpace:'pre-wrap',overflowWrap:'anywhere',flex:1}}><Tokens text={r}/></div></div>;})}</div></div>
   </>:<div style={{padding:'48px 48px'}}>
    <div style={{fontSize:24,color:C.orange,marginBottom:25}}>{s.chapterIndex===0?'同学们，我们从这里开始':'先把问题想清楚'}</div>
    <div style={{fontSize:s.chapterIndex===0?86:54,lineHeight:1.3,fontWeight:600,marginBottom:32}}>{s.chapterIndex===0?<>{project.coverTitle}<br/><span style={{color:C.orange}}>{project.coverSubtitle}</span></>:s.title}</div>
    {s.notes.map((n,i)=><div key={i} style={{fontSize:35,lineHeight:1.65,marginBottom:14,opacity:i<=stage?1:.22}}><span style={{color:C.orange,marginRight:20}}>{i+1}.</span>{n}</div>)}
   </div>}
  </div>
  <div data-side-panel style={{position:'absolute',left:1432,right:64,top:215,height:691,display:'flex',flexDirection:'column'}}>
   <div style={{fontSize:23,color:C.blue,marginBottom:22,flexShrink:0}}>{question?'想一想':s.kind==='answer'?'答案与原因':'这一步记住什么'}</div>
   {s.notes.map((n,i)=><div key={i} style={{display:'flex',gap:12,marginBottom:17,flexShrink:0,opacity:i<stage?1:i===stage?.27+.73*transition:.27}}><span style={{color:C.orange,fontSize:26}}>•</span><div style={{fontSize:27,lineHeight:1.45}}>{n}</div></div>)}
   {s.diagram&&!question&&<div style={{marginTop:3,flexShrink:0,width:376,alignSelf:'center'}}><Diagram type={s.diagram} stage={stage}/></div>}
   {s.chapterIndex===0&&stage>=2&&<pre style={{fontFamily:mono,fontSize:34,lineHeight:1.5,color:C.green,marginTop:'auto'}}>{'fn main() {\n  println!("你好");\n}'}</pre>}
   {!question&&stage>=2&&(s.output!==null||s.error||s.panic)&&<div style={{marginTop:'auto',background:'#17283a',border:`1px solid ${s.error||s.panic?'#704049':'#345848'}`,borderRadius:12,padding:'12px 16px',flexShrink:0}}><div style={{fontSize:20,color:statusColor,marginBottom:9}}>{s.error?'修改提示':s.panic?'运行结果':'看到的结果'}</div><pre style={{fontSize:25,fontFamily:mono,lineHeight:1.35,whiteSpace:'pre-wrap',overflowWrap:'anywhere',margin:0,color:s.error||s.panic?C.red:C.green}}>{s.error?`${s.notes[0]}\n${s.error}`:s.panic?'取不到值，发生 panic':s.output?.trimEnd()}</pre></div>}
   {pause&&<div style={{marginTop:'auto',border:`1px solid ${C.blue}`,borderRadius:14,padding:22,background:'#133342',textAlign:'center'}}><div style={{fontSize:25,color:C.blue}}>给自己四秒钟</div><div style={{fontSize:78,fontFamily:mono,lineHeight:1.2,marginTop:8}}>{Math.max(1,Math.ceil((s.durationFrames-local)/30))}</div><div style={{fontSize:21,color:C.muted,marginTop:8}}>随后一起看答案</div></div>}
  </div>
  <div style={{position:'absolute',top:915,left:66,fontSize:17,color:'#7186a1'}}>本节第 {s.sceneIndex+1} / {s.sceneCount} 个片段 · 每次理解一个新点</div>
  <div style={{position:'absolute',top:942,bottom:0,left:0,right:0,background:'#09111e',borderTop:`1px solid ${C.border}`}}/>
  {includeCaptions&&caption&&<div style={{position:'absolute',left:90,right:90,bottom:53,textAlign:'center',fontSize:40,lineHeight:1.4}}>{caption.text}</div>}
  {includeAudio&&<Sequence from={s.startFrame+s.leadFrames} durationInFrames={s.speechFrames}><Audio src={staticFile(s.audio)}/></Sequence>}
 </AbsoluteFill>;
};
