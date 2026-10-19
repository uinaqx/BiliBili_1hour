/* Measured narration overlay; the supplied mechanisms remain the visual source. */
const sourceRenderAt=window.renderAt;
window.renderVoicedAt=function(seconds){
 const frame=Math.max(0,Math.min(VOICED.totalFrames-1,Math.floor(seconds*30+.001)));
 const scene=VOICED.scenes.find(s=>frame>=s.startFrame&&frame<s.startFrame+s.durationFrames)||VOICED.scenes.at(-1);
 const local=frame-scene.startFrame;
 let originalTime,phase;
 if(local<scene.questionStart){originalTime=Math.min(89.95,Math.max(0,(local-scene.lessonStart)/(scene.lessonEnd-scene.lessonStart)*90));phase=local<scene.lessonEnd?'机制 / 演算':'整理过程，再做自测';}
 else if(local<scene.thinkStart){originalTime=90+6*(local-scene.questionStart)/(scene.thinkStart-scene.questionStart);phase='自测 · 请听题';}
 else if(local<scene.answerStart){originalTime=96+(local-scene.thinkStart)/30;phase='自测 · 独立思考 '+Math.ceil((scene.answerStart-local)/30)+' 秒';}
 else {originalTime=102+Math.min(17.95,18*(local-scene.answerStart)/(scene.answerEnd-scene.answerStart));phase=local<scene.answerEnd?'答案与解释':'回看答案，连接下一步';}
 sourceRenderAt((Number(scene.id.slice(1))-1)*120+originalTime);
 const svg=document.querySelector('#stage svg');
 const q=local>=scene.questionStart&&local<scene.answerStart,answered=local>=scene.answerStart;
 svg.querySelectorAll('text').forEach(n=>{if(n.textContent==='静音学习版')n.textContent='中文配音版';});
 const side=svg.querySelector('#sidebar');let sideText=rect(1330,230,500,625,'#121f32',C.line)+text(1360,280,answered?'自测答案与要点':q?'独立思考':'本镜头要点',27,C.muted);
 const items=q?['先独立预测，再查看解释。','检查位宽、单位与模型前提。','读题结束后保留六秒思考。']:answered?[...scene.on_screen.slice(0,2),'自测答案：'+scene.answer]:scene.on_screen;
 let size=30;while(size>24&&items.reduce((n,s)=>n+wrap(s,440/size).length*size*1.4+23,0)>490)size-=1;
 let y=338;items.forEach((item,i)=>{sideText+=lines(1360,y,item,440/size,size,[C.blue,C.gold,C.purple][i%3],1.4);y+=wrap(item,440/size).length*size*1.4+23;});side.innerHTML=sideText;
 const caption=scene.captions.find(c=>local/30>=c.start&&local/30<c.end)?.text||'';
 let footer=rect(0,875,1920,205,C.bg,C.bg,0)+rect(96,880,1728,140,q?'#27301e':'#142236',q?C.gold:C.line)+text(122,916,phase,22,q?C.gold:C.muted);
 if(caption)footer+=lines(122,966,caption,45,36,C.ink,1.24);
 else if(local>=scene.thinkStart&&local<scene.answerStart)footer+=text(122,969,'先把结果写下来，再看答案。',34,C.gold);
 footer+=`<rect x="96" y="1045" width="1728" height="4" fill="${C.line}"/><rect x="96" y="1045" width="${1728*local/scene.durationFrames}" height="4" fill="${C.blue}"/>`+text(96,1073,'教学模型 · 按条件解释结果 · 中文字幕依据实际配音',17,C.muted)+text(1824,1073,formatTime(frame/30)+' / '+formatTime(VOICED.displayFrames/30),18,C.muted,'end',mono);
 const g=document.createElementNS('http://www.w3.org/2000/svg','g');g.id='voice-footer';g.innerHTML=footer;svg.appendChild(g);
 window.voicedState={id:scene.id,frame,local,phase,originalTime,caption,question:q,answer:answered};return window.voicedState;
};
window.auditVoicedLayout=function(){
 const bad=[];const svg=document.querySelector('#stage svg');
 for(const n of svg.querySelectorAll('text')){
  if(!n.textContent.trim())continue;const b=n.getBBox();
  if(b.x<0||b.y<0||b.x+b.width>1921||b.y+b.height>1081)bad.push({kind:'canvas',text:n.textContent,box:[b.x,b.y,b.width,b.height]});
 }
 for(const [id,bounds] of [['mechanism',[90,205,1290,863]],['sidebar',[1328,225,1835,866]]]){
  for(const n of svg.querySelectorAll('#'+id+' text')){const b=n.getBBox();if(b.x<bounds[0]||b.y<bounds[1]||b.x+b.width>bounds[2]||b.y+b.height>bounds[3])bad.push({kind:id,text:n.textContent,box:[b.x,b.y,b.width,b.height]});}
 }
 return bad;
};
