import React from 'react';
export const C={bg:'#0b1422',panel:'#122033',border:'#2a3b52',text:'#f0f3f7',muted:'#96a9c0',orange:'#ffba78',blue:'#80d4e7',green:'#a5dfb4',red:'#ff9ca0'};
export type Panel={kind:string;title:string;footer:string;focus:number;[key:string]:any};
function wrap(s:string,width:number,size:number){
 const lines:string[]=[];let line='',used=0;
 for(const ch of String(s)){const unit=/[\u2e80-\uffff]/.test(ch)?1:.58;if(ch==='\n'||(used+unit>width/size&&line)){lines.push(line);line='';used=0;if(ch==='\n')continue;}line+=ch;used+=unit;}
 if(line)lines.push(line);return lines;
}
const Text:React.FC<{x:number;y:number;value:any;width?:number;size?:number;color?:string;anchor?:'start'|'middle';maxLines?:number}>=({x,y,value,width=1200,size=30,color=C.text,anchor='start',maxLines=3})=>{
 const lines=wrap(String(value),width,size);if(lines.length>maxLines)throw Error('Diagram text overflow: '+String(value));
 return <text x={x} y={y} fill={color} fontSize={size} textAnchor={anchor} fontFamily='Microsoft YaHei'>{lines.map((line,i)=><tspan key={i} x={x} dy={i?size*1.25:0}>{line}</tspan>)}</text>;
};
export const VisualCanvas:React.FC<{panel:Panel;stage:number;progress:number}>=({panel:p,stage,progress})=>{
 const rect=(x:number,y:number,w:number,h:number,color=C.blue)=><rect x={x} y={y} width={w} height={h} rx={14} fill={C.bg} stroke={color} strokeWidth={2}/>;
 const arrow=(x:number,y:number,x2:number,y2:number,color=C.muted)=><path d={`M${x} ${y} L${x2} ${y2}`} fill='none' stroke={color} strokeWidth={3} markerEnd='url(#co-arrow)'/>;
 const txt=(x:number,y:number,value:any,width=1200,size=30,color=C.text,anchor:'start'|'middle'='start',maxLines=3)=><Text {...{x,y,value,width,size,color,anchor,maxLines}}/>;
 let body:React.ReactNode;
 if(p.kind==='flow'){
  const n=p.nodes.length,w=(1220-(n-1)*30)/n;
  body=<>{p.nodes.map(([label,value]:string[],i:number)=>{const x=25+i*(w+30),active=i===Math.min(stage,n-1);return <g key={i}>{rect(x,95,w,230,active?C.orange:C.border)}{txt(x+22,133,String(i+1).padStart(2,'0'),w-44,23,active?C.orange:C.muted)}{txt(x+w/2,185,label,w-32,28,C.blue,'middle',2)}{txt(x+w/2,258,value,w-32,32,active?C.orange:C.text,'middle',2)}{i<n-1&&arrow(x+w+3,211,x+w+27,211,stage>=i?C.orange:C.border)}{active&&<circle cx={x+18+(w-36)*progress} cy={345} r={5} fill={C.orange}/>}</g>;})}{txt(640,403,p.title,1150,28,C.green,'middle',1)}</>;
 }else if(p.kind==='branches'){
  const n=p.branches.length,w=1140/n;
  body=<>{rect(410,15,460,112,C.blue)}{txt(640,57,p.root[0],430,31,C.blue,'middle',1)}{txt(640,103,p.root[1],430,28,C.text,'middle',1)}{p.branches.map(([label,value]:string[],i:number)=>{const x=70+i*w,active=i===Math.min(stage,n-1);return <g key={i}><path d={`M640 127 V175 H${x+(w-28)/2} V215`} stroke={active?C.orange:C.border} strokeWidth={3} fill='none' markerEnd='url(#co-arrow)'/>{rect(x,218,w-28,155,active?C.orange:C.blue)}{txt(x+(w-28)/2,267,label,w-60,30,C.blue,'middle',2)}{txt(x+(w-28)/2,328,value,w-60,31,C.text,'middle',2)}</g>;})}</>;
 }else if(p.kind==='join'){
  const carry=stage>=2?1:0;
  body=<>{[['输入 A',1],['输入 B',1],['输入进位',carry]].map(([label,value],i)=><g key={i}>{rect(30,16+i*132,275,98,C.blue)}{txt(167,57+i*132,label,245,27,C.blue,'middle',1)}{txt(167,99+i*132,value,245,34,C.text,'middle',1)}{arrow(305,65+i*132,490,160+i*42,C.orange)}</g>)}{rect(490,114,285,210,C.orange)}{txt(632,189,'一位全加器',255,35,C.orange,'middle',1)}{txt(632,258,carry?'1＋1＋1':'1＋1＋0',255,34,C.text,'middle',1)}{arrow(775,176,970,144,C.orange)}{arrow(775,260,970,300,C.orange)}{rect(970,95,270,95,C.green)}{txt(1105,155,'和位：'+carry,240,34,C.green,'middle',1)}{rect(970,251,270,95,C.green)}{txt(1105,311,'进位：1',240,34,C.green,'middle',1)}</>;
 }else if(p.kind==='bus'){
  body=<>{rect(30,70,260,320,C.blue)}{txt(160,202,'CPU',235,44,C.blue,'middle',1)}{txt(160,270,'当前发起方',235,29,C.text,'middle',1)}{rect(980,70,260,320,C.blue)}{txt(1110,225,'主存 / 设备',235,35,C.text,'middle',1)}
   {arrow(290,132,980,132,stage===0?C.orange:C.border)}{txt(635,113,'地址：访问哪里',650,29,C.muted,'middle',1)}
   {arrow(980,210,290,210,stage===1?C.orange:C.blue)}{txt(635,192,'读：数据返回发起方',650,29,C.muted,'middle',1)}
   {arrow(290,285,980,285,stage===2?C.orange:C.blue)}{txt(635,267,'写：数据送到目标',650,29,C.muted,'middle',1)}
   {arrow(290,360,610,360,stage===3?C.orange:C.border)}{arrow(980,360,660,360,stage===3?C.orange:C.border)}{txt(635,342,'控制请求与状态反馈',650,29,C.muted,'middle',1)}{txt(640,432,'本例每次数据传输 64 bit = 8 B',1200,28,C.green,'middle',1)}</>;
 }else if(p.kind==='table'){
  const cols=p.headers.length,w=1220/cols,rows=p.rows.length,h=Math.min(83,320/rows);
  body=<>{rect(25,25,1220,70+rows*h,C.border)}{p.headers.map((s:string,i:number)=><g key={i}>{txt(45+i*w,68,s,w-38,27,C.blue,'start',1)}</g>)}{p.rows.map((row:string[],i:number)=><g key={i}><rect x={27} y={88+i*h} width={1216} height={h-2} fill={i===Math.min(stage,rows-1)?'#263447':C.panel}/>{row.map((s,j)=><g key={j}>{txt(45+j*w,117+i*h,s,w-38,28,i===Math.min(stage,rows-1)?C.orange:C.text,'start',2)}</g>)}</g>)}</>;
 }else if(p.kind==='bits'){
  const rows=p.rows as string[][];const h=Math.min(92,360/rows.length);
  body=<>{rows.map(([label,bits,value],r)=>{const width=Math.min(76,670/bits.length),start=245,active=r===Math.min(stage,rows.length-1);return <g key={r}>{txt(20,66+r*h,label,212,27,active?C.orange:C.muted,'start',2)}{bits.split('').map((bit,i)=><g key={i}>{rect(start+i*width,25+r*h,width-6,63,active?C.orange:C.border)}{txt(start+i*width+(width-6)/2,69+r*h,bit,width-6,36,bit==='?'?C.muted:C.text,'middle',1)}</g>)}{txt(945,66+r*h,value,290,28,C.green,'start',2)}</g>;})}{txt(25,419,'固定宽度下，先操作位模式，再按约定解释。',1200,25,C.muted,'start',1)}</>;
 }else if(p.kind==='fields'){
  const sum=p.parts.reduce((a:number,v:any)=>a+v[2],0);let x=25;
  body=<>{txt(25,45,p.annotation,1220,27,C.muted,'start',2)}{p.parts.map(([label,value,weight]:any,i:number)=>{const w=1220*weight/sum,at=x;x+=w;return <g key={i}>{rect(at+3,133,w-6,174,i===stage%p.parts.length?C.orange:C.blue)}{txt(at+w/2,192,label,w-22,31,C.blue,'middle',2)}{txt(at+w/2,258,value,w-22,32,C.text,'middle',2)}</g>;})}{txt(640,386,'字段的含义与宽度，都要结合题目模型。',1190,29,C.green,'middle',1)}</>;
 }else if(p.kind==='hierarchy'){
  body=<>{p.labels.map((s:string,i:number)=>{const w=550+i*195;return <g key={i}>{rect(640-w/2,15+i*100,w,75,i===stage?C.orange:C.blue)}{txt(640,64+i*100,s,w-40,30,i===stage?C.orange:C.text,'middle',1)}{i<3&&arrow(640,94+i*100,640,110+i*100,C.muted)}</g>;})}</>;
 }else if(p.kind==='register'){
  const select=p.selects[stage];const value=p.inputs[select];
  body=<>{rect(25,58,230,89,select===0?C.orange:C.border)}{txt(140,114,'左路 '+p.inputs[0],210,34,C.text,'middle',1)}{rect(25,245,230,89,select===1?C.orange:C.border)}{txt(140,302,'右路 '+p.inputs[1],210,34,C.text,'middle',1)}{rect(425,125,245,160,C.blue)}{txt(547,180,'二选一',220,34,C.blue,'middle',1)}{txt(547,241,'S = '+select,220,34,C.orange,'middle',1)}{arrow(255,102,425,171,select===0?C.orange:C.border)}{arrow(255,290,425,241,select===1?C.orange:C.border)}{arrow(670,204,842,204,C.orange)}{txt(755,180,String(value),100,36,C.orange,'middle',1)}{rect(850,124,355,163,C.green)}{txt(1027,179,p.showRegister?'寄存器已保存':'选择器输出',330,30,C.blue,'middle',1)}{txt(1027,248,String(p.showRegister?p.stored[stage]:value),330,44,C.text,'middle',1)}{txt(640,392,p.showRegister?'写入允许 ＋ 有效时钟边沿 → 更新状态':'选择信号决定哪路数据通过',1200,30,C.green,'middle',1)}</>;
 }else if(p.kind==='cache'){
  body=<>{txt(25,48,'两行直接映射：行号 = 主存块号 mod 2',1220,30,C.blue,'start',1)}{['行 0','行 1'].map((s,i)=><g key={i}>{rect(300,96+i*125,715,100,i===0?C.orange:C.border)}{txt(75,158+i*125,s,180,35,C.text)}{txt(660,158+i*125,i===0?p.contents[stage]:'无效 / 空',650,39,i===0?C.orange:C.muted,'middle',1)}</g>)}{txt(640,397,'块 0 与块 2 都必须进入行 0。',1200,30,C.green,'middle',1)}</>;
 }else if(p.kind==='cpu'){
  const fetch=p.mode==='fetch',store=p.mode==='store';const r3=store||(!fetch&&stage>=(p.writeAt??3))?'20':'—';const mem=store&&stage>=1?'20':'0';const alu=store?'有效地址 108':!fetch&&stage>=(p.resultAt??2)?'13＋7 = 20':'加法 / 地址计算';
  body=<>{rect(10,10,190,70,C.blue)}{txt(105,54,store?'PC（略）':'PC '+(p.pc??8),170,30,C.blue,'middle',1)}{rect(460,10,300,70,C.orange)}{txt(610,54,'控制器',280,31,C.orange,'middle',1)}{rect(1000,10,240,70,C.blue)}{txt(1120,53,'IR：'+(fetch?'ADD':store?'STORE':'当前指令'),220,27,C.blue,'middle',1)}
   <path d='M105 80 V114 H1110 V150' stroke={fetch?C.orange:C.border} strokeWidth={3} fill='none' markerEnd='url(#co-arrow)'/>{txt(790,104,'取指地址',180,22,C.muted,'middle',1)}{arrow(1200,150,1200,80,fetch?C.orange:C.border)}{arrow(610,80,610,180,C.orange)}{txt(628,143,'操作与写入控制',290,23,C.muted)}
   {rect(10,150,280,200,C.blue)}{txt(150,188,'寄存器组',260,30,C.blue,'middle',1)}{txt(36,231,'R1 = 13',240,31)}{txt(36,277,'R2 = 7',240,31)}{txt(36,326,'R3 = '+r3,240,31,C.green)}{rect(475,180,270,140,C.orange)}{txt(610,227,'ALU',240,34,C.orange,'middle',1)}{txt(610,282,alu,244,29,C.text,'middle',2)}
   {arrow(290,201,475,216,fetch||store?C.border:C.orange)}{arrow(290,282,475,282,fetch||store?C.border:C.orange)}{rect(990,150,250,200,C.blue)}{txt(1115,190,'存储系统',230,30,C.blue,'middle',1)}{txt(1010,239,'M32[100] = 13',220,25)}{txt(1010,282,'M32[104] = 7',220,25)}{txt(1010,325,'M32[108] = '+mem,220,25,C.green)}
   <path d='M610 320 V395 H150 V350' stroke={!fetch&&!store&&stage>=2?C.orange:C.border} strokeWidth={3} fill='none' markerEnd='url(#co-arrow)'/>{txt(390,424,'写回寄存器',250,23,C.muted,'middle',1)}{arrow(290,339,990,339,store?C.orange:C.border)}{txt(858,324,'存出',170,23,store?C.orange:C.muted,'middle',1)}{arrow(990,161,290,161,store||fetch?C.border:C.blue)}{txt(850,149,'读入数据',170,22,C.muted,'middle',1)}</>;
 }else if(p.kind==='pipeline'){
  const stages=p.stages as string[];const maxCycle=stage<2?4:8;
  body=<>{Array.from({length:8},(_,i)=><g key={i}>{txt(262+i*120,42,'C'+(i+1),108,25,C.muted,'middle',1)}</g>)}{Array.from({length:4},(_,r)=><g key={r}>{txt(32,107+r*72,'指令 '+(r+1),150,30,C.blue)}{Array.from({length:8},(_,col)=><g key={col}><rect x={204+col*120} y={65+r*72} width={112} height={60} rx={8} fill={C.bg} stroke={C.border}/>{col>=r&&col<r+5&&col<maxCycle&&<><rect x={204+col*120} y={65+r*72} width={112} height={60} rx={8} fill={col===maxCycle-1?'#4b392d':'#193747'} stroke={C.blue}/>{txt(260+col*120,105+r*72,stages[col-r],105,25,col===maxCycle-1?C.orange:C.text,'middle',1)}</>}</g>)}</g>)}{txt(25,391,p.annotation,1220,27,C.muted,'start',1)}</>;
 }else if(p.kind==='bar'){
  const max=Math.max(...p.bars.map((b:any)=>b[1]));body=<>{p.bars.map(([label,value]:any,i:number)=><g key={i}>{txt(30,98+i*135,label,210,31,C.blue)}<rect x={250} y={48+i*135} width={840*value/max} height={80} rx={10} fill={i===0?'#27465a':'#466141'}/>{txt(270+840*value/max,101+i*135,value+' '+p.unit,160,33,C.orange)}</g>)}{txt(25,397,p.annotation,1220,30,C.green,'start',1)}</>;
 }else throw Error('Unknown diagram '+p.kind);
 return <svg width='100%' height='100%' viewBox='0 0 1280 440'><defs><marker id='co-arrow' markerWidth='8' markerHeight='8' refX='7' refY='4' orient='auto'><path d='M0 0 L8 4 L0 8Z' fill={C.muted}/></marker></defs>{body}</svg>;
};
