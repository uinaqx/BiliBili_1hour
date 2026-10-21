import assert from 'node:assert/strict';
import {activeCodeLines,diagramStateAt} from '../assets/persistent-sync.ts';
let cases=0;
const same=(value,want)=>{assert.deepEqual(value,want);cases++;};
const scene={durationFrames:200,code:'a = 1\nb = 2\nprint(a, b)',initialCodeLines:[1],codeCues:[
  {beginFrame:10,endFrame:20,lines:[2]},
  {beginFrame:50,endFrame:60,lines:[1,3]},
  {beginFrame:90,endFrame:100,lines:[3]},
]};
for(let frame=0;frame<200;frame++)same(activeCodeLines(scene,frame),frame<10?[1]:frame<50?[2]:frame<90?[1,3]:[3]);
// A sentence ending and four-second thinking hold have no independent clearing event.
same(activeCodeLines({...scene,durationFrames:400},399),[3]);
const multi={...scene,codeCues:[{beginFrame:10,lines:[1]},{beginFrame:10,lines:[3]}]};
same(activeCodeLines(multi,10),[1,3]);
same(activeCodeLines({...scene,codeCues:[]},199),[1]);
const panels={...scene,panels:[{id:'second',beginFrame:50,code:'x = 10\nprint(x)',initialCodeLines:[2]}],codeCues:[
  {beginFrame:10,endFrame:20,lines:[3],panelId:'root'},
  {beginFrame:60,endFrame:65,lines:[3],panelId:'root'}, // stray old-panel event must not leak
  {beginFrame:90,endFrame:100,lines:[1],panelId:'second'},
]};
same(activeCodeLines(panels,49),[3]);same(activeCodeLines(panels,50),[2]);
same(activeCodeLines(panels,60),[2]);same(activeCodeLines(panels,89),[2]);
same(activeCodeLines(panels,90),[1]);same(activeCodeLines(panels,199),[1]);
assert.throws(()=>activeCodeLines(scene,-1));assert.throws(()=>activeCodeLines(scene,200));cases+=2;
assert.throws(()=>activeCodeLines({...scene,initialCodeLines:[4]},0));cases++;
const diagrams=[{beginFrame:10,patch:{focus:'alu',result:20},groupId:'cpu'},
  {beginFrame:40,patch:{focus:'register',r3:20},groupId:'cpu'},
  {beginFrame:80,patch:{focus:'memory',memory108:20},groupId:'cpu'}];
same(diagramStateAt(diagrams,9,{r3:0,memory108:0},'cpu'),{r3:0,memory108:0});
same(diagramStateAt(diagrams,39,{r3:0,memory108:0},'cpu'),{r3:0,memory108:0,focus:'alu',result:20});
same(diagramStateAt(diagrams,40,{r3:0,memory108:0},'cpu'),{r3:20,memory108:0,focus:'register',result:20});
same(diagramStateAt(diagrams,999,{r3:0,memory108:0},'cpu'),{r3:20,memory108:20,focus:'memory',result:20});
same(diagramStateAt(diagrams,999,{focus:'cache'},'cache'),{focus:'cache'});
assert.equal(scene.codeCues.length,3);cases++;
console.log(JSON.stringify({allPassed:true,cases,checks:['phrase-end hold','gap and thinking hold','backward multi-line','simultaneous targets','panel reset and isolation','invalid positions','independent diagram states']}));
