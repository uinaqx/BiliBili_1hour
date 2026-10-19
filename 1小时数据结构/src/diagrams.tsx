import React from 'react';
const C={bg:'#0b1422',panel:'#122033',border:'#2a3b52',text:'#f0f3f7',muted:'#96a9c0',orange:'#ffba78',blue:'#80d4e7',green:'#a5dfb4',red:'#ff9ca0'};
export const DataDiagram:React.FC<{type:string;stage:number;sceneKey:string;progress?:number}>=({type,stage,sceneKey,progress=1})=>{
 const t=(x:number,y:number,s:string,color=C.text,size=23,anchor='start')=><text x={x} y={y} fill={color} fontSize={size} textAnchor={anchor as any} fontFamily='Microsoft YaHei'>{s}</text>;
 const box=(x:number,y:number,w:number,s:string,color=C.blue,h=48)=><g><rect x={x} y={y} width={w} height={h} rx={8} stroke={color} fill={C.bg} strokeWidth={2}/>{t(x+w/2,y+h/2+8,s,color,23,'middle')}</g>;
 const arrow=(x:number,y:number,x2:number,y2:number,color=C.muted)=><path d={`M${x} ${y} L${x2} ${y2}`} stroke={color} strokeWidth={2.5} fill='none' markerEnd='url(#ds-arrow)'/>;
 const row=(values:(string|number)[],y=75,active=-1)=>values.map((v,i)=>{const w=Math.min(80,370/values.length);const x=8+i*w;return <g key={i}>{box(x,y,w-6,String(v),i===active?C.orange:C.blue)}{t(x+(w-6)/2,y+78,String(i),C.muted,19,'middle')}</g>});
 const tree=(values:number[],path:number[]=[])=>{
  const pos=[[195,55],[95,135],[295,135],[45,222],[145,222],[245,222],[345,222]];
  return <>{values.map((v,i)=>{const p=Math.floor((i-1)/2);return <g key={i}>{i>0&&<line x1={pos[p][0]} y1={pos[p][1]+23} x2={pos[i][0]} y2={pos[i][1]-23} stroke={C.border} strokeWidth={3}/>}</g>})}{values.map((v,i)=><g key={i}><circle cx={pos[i][0]} cy={pos[i][1]} r={24} fill={C.bg} stroke={path.includes(i)?C.orange:C.blue} strokeWidth={3}/>{t(pos[i][0],pos[i][1]+8,String(v),path.includes(i)?C.orange:C.text,23,'middle')}</g>)}</>;
 };
 let body:React.ReactNode;
 if(type==='overview'||type==='choose')body=<>{t(0,25,'按任务选择工具',C.muted)}{['按位置 → 动态数组','按姓名 → 哈希表','取最大 → 优先队列','看连接 → 图'].map((s,i)=><g key={s}>{box(8,48+i*64,372,s,i<=stage?C.green:C.blue)}</g>)}</>;
 else if(type==='workflow')body=<>{box(20,17,350,'原始成绩 · vector')}{arrow(195,74,195,98)}{box(20,110,350,'次数统计 · 哈希表',C.orange)}{arrow(195,168,195,192)}{box(20,204,350,'取出高分 · 优先队列',C.green)}</>;
 else if(type==='complexity')body=<>{t(0,25,'规模变大，次数怎样增长？',C.muted,22)}{['O(1)       直接定位','O(n)       完整扫描','O(n²)     所有配对'].map((s,i)=><g key={s}>{box(8,55+i*75,372,s,i===stage%3?C.orange:C.blue)}</g>)}</>;
 else if(type==='halving')body=<>{t(0,25,'每一步把范围减半',C.muted)}{[16,8,4,2,1].map((v,i)=><g key={v}><rect x={10+i*75} y={150-v*5} width={52} height={v*5+35} fill={i<=stage?C.blue:C.border} rx={6}/>{t(36+i*75,220,String(v),C.text,26,'middle')}</g>)}{t(12,278,'16 → 8 → 4 → 2 → 1',C.green,25)}</>;
 else if(type==='array'){
  const copy=sceneKey==='01-04';const values=copy?[3,5,7]:sceneKey==='02-05'?[10,20,30]:sceneKey==='02-02'?(stage===0||stage===3?[72,88,95]:[72,88,95,81]):[72,88,95,81];
  body=<>{t(0,25,copy?'原数组与副本分开保存':'连续存放 · 下标从 0 开始',C.muted,22)}{row(values,65,stage===3?2:stage%values.length)}{copy?<>{t(0,192,'副本',C.orange)}{row(stage>=2?[99,5,7]:[3,5,7],214,0)}</>:<>{t(0,215,'按下标直接定位',C.green,25)}{t(0,266,'访问前检查下标有效',C.muted,23)}</>}</>;
 } else if(type==='insert'){
  const question=sceneKey==='02-q'||sceneKey==='02-a';const final=question?[10,99,20,30]:[10,15,20,30];
  const values=stage===0?[10,20,30]:stage===3&&!question?[10,15,30]:final;
  body=<>{t(0,25,'插入需要为新元素让位',C.muted,22)}{row(values,73,1)}{arrow(140,192,225,192,C.orange)}{t(0,254,question?'下标 2 → 20':'保持顺序，需要移动元素',C.green,24)}</>;
 } else if(type==='capacity')body=<>{t(0,25,'预备空间 ≠ 有效元素',C.muted,22)}{box(10,65,370,'reserve(100)',C.blue)}{box(10,144,370,stage<2?'size = 0':'size = 1',C.orange)}{t(12,256,'capacity 至少为 100',C.green,24)}</>;
 else if(type==='linked'||type==='linkedInsert'||type==='linkedDelete'){
  const vals=type==='linkedDelete'&&stage>0?[10,30]:type==='linkedInsert'&&stage<2?[10,30]:[10,20,30];
  body=<>{t(0,25,'顺序由 next 连接决定',C.muted,22)}{vals.map((v,i)=><g key={v}>{box(9+i*130,88,95,String(v),v===20?C.orange:C.blue)}{i<vals.length-1&&arrow(108+i*130,112,133+i*130,112)}</g>)}{type==='linkedInsert'&&stage<2?<g opacity={stage===1?progress:0}>{box(140,191,95,'20',C.orange)}{t(10,289,'先接后面，再改前面',C.green,24)}</g>:<>{t(10,218,'head → 第一个节点',C.orange,24)}{t(10,273,'最后的 next 是 nullptr',C.muted,22)}</>}</>;
 } else if(type==='stack'||type==='stackQueue'){
  const exercise=sceneKey.startsWith('04-')&&(sceneKey.endsWith('-q')||sceneKey.endsWith('-a'));
  const vals=exercise?[3,7]:[10,20];
  body=<>{t(0,25,'最后放入的先取出',C.muted)}{box(95,180,190,String(vals[0]))}{stage<3&&box(95,112,190,String(vals[1]),C.orange)}{arrow(310,78,310,135,C.orange)}{t(300,199,'top',C.orange,22)}{t(22,285,exercise?'栈剩 3；队列剩 7':'pop 移除当前栈顶',C.green,23)}</>;
 } else if(type==='brackets')body=<>{t(0,25,'最近打开的先关闭',C.muted)}{t(18,89,'(  (  )  )',C.orange,48)}{box(60,140,270,stage<3?'还有待配对的左括号':'栈已清空',C.blue)}{t(0,258,'结束时仍非空 → 未配完',C.green,22)}</>;
 else if(type==='queue')body=<>{t(0,25,'最先到达的先处理',C.muted)}{row(stage<3?[10,20]:[20],90,0)}{t(10,217,'front · 队头',C.orange,24)}{arrow(155,210,38,155,C.orange)}{t(10,278,'push 在队尾，pop 在队头',C.green,22)}</>;
 else if(type==='ring')body=<>{t(0,25,'下标回绕，复用空位',C.muted)}{[[185,83,'40'],[72,200,'20'],[290,200,'30']].map(([x,y,v],i)=><g key={i}>{box(Number(x)-42,Number(y)-23,84,String(v),C.blue)}</g>)}<path d='M218 99 Q302 120 305 162 M264 220 Q188 273 112 220 M59 165 Q78 95 140 88' stroke={C.orange} fill='none' strokeWidth={3} markerEnd='url(#ds-arrow)'/>{t(38,310,'逻辑顺序：20 → 30 → 40',C.green,22)}</>;
 else if(type.startsWith('hash')||type==='frequency'){
  const vals=type==='hashCollision'?['桶 2：10 → 14','桶 3：7','碰撞后还要比较键']:type==='frequency'?['80 → 3 次','90 → 2 次','70 → 1 次']:sceneKey.endsWith('-q')||sceneKey.endsWith('-a')?['A → 3','B → 0','size = 2']:sceneKey==='05-03'?['Lin → 88','Missing → 0','find 不新增键']:['Lin → 88','Mei → 95','按键查找对应记录'];
  body=<>{t(0,25,type==='hashCollision'?'同一个桶可以有不同键':'键和值建立对应关系',C.muted,22)}{vals.map((v,i)=><g key={v}>{box(8,54+i*79,372,v,i===stage%3?C.orange:C.blue)}</g>)}</>;
 } else if(['tree','inorder','bst','heap','heapIndex','treeSmall','heapSmall'].includes(type)){
  const heap=type.startsWith('heap');const small=type==='treeSmall'||type==='heapSmall';
  const vals=type==='treeSmall'?[8,4,12]:type==='heapSmall'?(stage<2?[9,4,6]:[8,4,6]):type==='heapIndex'?[90,75,82,60,65]:heap?(stage===3?[82,75]:[90,75,82]):[8,4,12,2,6,10,14];
  const path=type==='bst'?[[0],[0,2],[0,2,5],[0,2,5]][stage]:type==='inorder'?[[3],[3,1,4],[3,1,4,0],[0,1,2,3,4,5,6]][stage]:heap?[0]:[stage%vals.length];
  body=<>{tree(vals,path)}{t(8,299,type==='bst'?'找 10：8 → 12 → 10':type==='inorder'?'2、4、6、8、10、12、14':type==='heapIndex'?'i=1 的孩子在下标 3、4':heap?'只保证父子间的优先关系':small?'左 → 根 → 右':'根、孩子、叶子',C.green,21)}</>;
 } else if(type==='skewTree')body=<>{t(0,25,'失衡后像一条长链',C.muted)}{[1,2,3,4].map((v,i)=><g key={v}>{i>0&&arrow(64+(i-1)*77,89+(i-1)*56,84+(i-1)*77,111+(i-1)*56)}{box(15+i*77,52+i*56,65,String(v),C.orange)}</g>)}{t(12,315,'查找可能退化成 O(n)',C.green,23)}</>;
 else if(['graph','adjacency','bfs','bfsDistance','dfs'].includes(type)){
  const pos=[[195,55],[70,139],[320,139],[195,221],[322,289]];const edges=[[0,1],[0,2],[1,3],[2,3],[3,4]];
  const active=type==='dfs'?[[0],[0,1],[0,1,3],[0,1,3,2,4]][stage]:[[0],[0,1,2],[0,1,2,3],[0,1,2,3,4]][stage];
  body=<>{edges.map(([a,b])=><line key={`${a}-${b}`} x1={pos[a][0]} y1={pos[a][1]} x2={pos[b][0]} y2={pos[b][1]} stroke={C.border} strokeWidth={4}/>)}{pos.map(([x,y],i)=><g key={i}><circle cx={x} cy={y} r={25} fill={C.bg} stroke={active.includes(i)?C.orange:C.blue} strokeWidth={3}/>{t(x,y+9,String.fromCharCode(65+i),C.text,26,'middle')}</g>)}{t(0,312,type==='bfsDistance'?'到 E：最少 3 条边':type==='dfs'?'DFS：A B D C E':type==='bfs'?'BFS：A B C D E':type==='adjacency'?'A 的清单：[B, C]':'5 个地点，5 条连接',C.green,21)}</>;
 } else if(type==='binary'||type==='binaryDuplicates'){
  const dup=type==='binaryDuplicates';const vals=dup?[1,2,2,2,5]:[3,8,12,20,27,31,40];const mids=dup?[2,1,0,1]:[3,5,4,4];
  body=<>{t(0,25,dup?'寻找第一个 2':'寻找 27',C.muted,24)}{row(vals,88,mids[stage])}{box(12,219,365,stage===3?`结果下标：${dup?1:4}`:'保持左闭右开区间',stage===3?C.green:C.orange)}</>;
 } else if(['selection','insertion','merge','partition','sorted','selectionQuestion','stable'].includes(type)){
  let vals:(string|number)[]=[5,2,4,1];
  if(type==='stable')vals=stage<2?['80A','70B','80C']:['70B','80A','80C'];
  else if(type==='insertion')vals=[[5,2,4,1],[2,5,4,1],[2,4,5,1],[1,2,4,5]][stage];
  else if(type==='selectionQuestion')vals=stage===0?[4,1,3,2]:[1,4,3,2];
  else if(type==='partition')vals=[[5,2,1,4],[2,5,1,4],[2,1,5,4],[2,1,4,5]][stage];
  else if(type==='merge')vals=stage<2?[5,2,4,1]:stage===2?[2,5,1,4]:[1,2,4,5];
  else if(stage>0)vals=[1,2,4,5];
  body=<>{t(0,25,type==='merge'?'分开排序，再线性合并':type==='partition'?'基准：4；这里只做一次划分':type==='stable'?'只按分数比较':'跟踪每一轮的变化',C.muted,21)}{row(vals,86,type==='partition'?stage===3?2:3:stage%vals.length)}{t(8,229,type==='stable'?'同分时，A 仍在 C 前面':type==='partition'?'左边较小，不代表内部有序':type==='selectionQuestion'?'只确定第 0 个位置':'看清当前已建立的顺序',C.green,22)}{t(8,285,type==='insertion'?'左侧是已经有序的部分':type==='merge'?'左右两段都要先有序':'小数据先手工推演',C.muted,21)}</>;
 } else body=<>{box(8,60,372,'看数据怎样保存')}{box(8,145,372,'看操作怎样执行',C.orange)}{box(8,230,372,'再比较增长的代价',C.green)}</>;
 return <svg width='100%' height={310} viewBox='0 0 390 335'><defs><marker id='ds-arrow' markerWidth='8' markerHeight='8' refX='7' refY='4' orient='auto'><path d='M0 0 L8 4 L0 8Z' fill={C.muted}/></marker></defs>{body}</svg>;
};
