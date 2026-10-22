import fs from 'node:fs';
import ts from 'typescript';
const source=fs.readFileSync(new URL('../src/sync.ts',import.meta.url),'utf8');
const compiled=ts.transpileModule(source,{compilerOptions:{target:ts.ScriptTarget.ES2020,module:ts.ModuleKind.ES2020}}).outputText;
const {codeLinesAt}=await import('data:text/javascript;base64,'+Buffer.from(compiled).toString('base64'));
const timeline=JSON.parse(fs.readFileSync(new URL('../public/timeline.json',import.meta.url),'utf8'));
let checked=0,cues=0;
for(const s of timeline.scenes){
 if(!s.code)continue;
 const lines=s.code.split('\n');
 for(let f=0;f<s.durationFrames;f++){
  const current=s.codeCues.filter(c=>c.beginFrame<=f).at(-1);
  const expected=current?.lines??s.initialCodeLines;
  const actual=codeLinesAt(s.codeCues,f,s.initialCodeLines);
  if(!actual.length||actual.some(n=>n<1||n>lines.length||!lines[n-1].trim())||JSON.stringify(actual)!==JSON.stringify(expected))throw Error(`Persistent highlight mismatch ${s.key} frame ${f}`);
  checked++;
 }
 for(const c of s.codeCues){if(c.beginFrame<0||c.beginFrame>=c.endFrame||c.endFrame>s.durationFrames)throw Error('Invalid cue '+s.key);cues++;}
 if(s.kind==='question'&&s.output!==null)throw Error('Quiz answer revealed early '+s.key);
}
console.log(JSON.stringify({allPassed:true,framesChecked:checked,authoredCodeCues:cues,mode:'persistent-until-next-spoken-unit'}));
