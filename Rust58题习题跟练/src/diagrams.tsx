import React from 'react';
export type VisualSpec={title:string;rows:string[][];foot:string};
export const DataDiagram:React.FC<{spec:VisualSpec}>=({spec})=>{
 const units=(s:string)=>Array.from(s).reduce((n,c)=>n+(c.charCodeAt(0)>255?1:.55),0);
 const split=(s:string,limit:number)=>{const rows:string[]=[];let row='';for(const c of s){if(units(row+c)>limit){rows.push(row);row='';}row+=c;}if(row)rows.push(row);return rows;};
 const foot=split(spec.foot,21),title=split(spec.title,18);const top=title.length*26+20;
 return <svg data-diagram viewBox={`0 0 390 ${top+spec.rows.length*67+foot.length*23+15}`} width="100%" role="img" aria-label={spec.title} style={{display:'block',fontFamily:'Microsoft YaHei, sans-serif'}}>
  {title.map((r,i)=><text key={i} x="0" y={23+i*26} fontSize="22" fill="#80d4e7">{r}</text>)}
  {spec.rows.map((r,i)=>{const gap=10,w=(390-gap*(r.length-1))/r.length,y=top+i*67;return <g key={i}>
   {i>0&&<path d={`M195 ${y-18} L195 ${y-5} m-4 -4 l4 4 l4 -4`} fill="none" stroke="#80d4e7" strokeWidth="2"/>}
   {r.map((label,j)=><g key={j}><rect x={j*(w+gap)} y={y} width={w} height="45" rx="8" fill="#1b334b" stroke="#7bacc0" strokeWidth="1.3"/><text x={j*(w+gap)+w/2} y={y+29} fontSize={Math.min(22,(w-16)/Math.max(1,units(label)))} textAnchor="middle" fill="#f0f3f7">{label}</text></g>)}
  </g>;})}
  {foot.map((r,i)=><text key={i} x="0" y={top+spec.rows.length*67+8+i*23} fontSize="18" fill="#a5dfb4">{r}</text>)}
 </svg>;
};
