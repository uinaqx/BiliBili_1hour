"""Keep the Rust second-lesson layout and adapt its vocabulary and diagram layer."""
import pathlib,json
ROOT=pathlib.Path(__file__).resolve().parents[1]
text=(ROOT/'templates/base_video.tsx').read_text(encoding='utf-8')
text=text.replace("import React from 'react';","import React from 'react';\nimport {DataDiagram} from './diagrams';")
start=text.index('function Tokens(');end=text.index('export const Course:')
tokens=r'''function Tokens({text}:{text:string}){
 const keywords=/^(int|bool|char|void|auto|const|if|else|return|for|while|struct|new|delete|nullptr|true|false|static_cast|using|namespace|sizeof|try|catch)$/;
 const types=/^(vector|string|queue|stack|priority_queue|unordered_map|unordered_set|Node|Tree|Student|out_of_range)$/;
 const p=new RegExp(__TOKEN_PATTERN__,'g');
 return <>{text.split(p).filter(Boolean).map((v,i)=>{let color=C.text;if(v.startsWith('//'))color=C.muted;else if(v.charCodeAt(0)===34||v.charCodeAt(0)===39)color=C.green;else if(keywords.test(v))color=C.orange;else if(types.test(v))color=C.blue;else if(v[0]>='0'&&v[0]<='9')color='#d6b8f1';return <span key={i} style={{color}}>{v}</span>;})}</>;
}
'''
pattern=r'''(//.*|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])'|\b(?:int|bool|char|void|auto|const|if|else|return|for|while|struct|new|delete|nullptr|true|false|static_cast|using|namespace|sizeof|try|catch)\b|\b(?:vector|string|queue|stack|priority_queue|unordered_map|unordered_set|Node|Tree|Student|out_of_range)\b|\b\d+\b)'''
tokens=tokens.replace('__TOKEN_PATTERN__',json.dumps(pattern))
text=text[:start]+tokens+text[end:]
text=text.replace('Rust 进阶基础 ·','数据结构 ·').replace('初学者课堂 · Rust 2024','初学者课堂 · C++')
text=text.replace('<Diagram type={s.diagram} stage={stage}/>','<DataDiagram type={s.diagram} stage={stage} sceneKey={s.key} progress={transition}/>')
text=text.replace('/let |println!|if |fn |for |return |\\.map|\\.filter|\\.join|match |Some|None|Ok|Err|pub |assert/','/cout|push|pop|if |for |return |while |sort|next|mid/')
line=next(line for line in text.splitlines() if 'const resultLabel=' in line)
text=text.replace(line," const resultLabel=s.excerpt?'完整程序运行结果':'运行结果';")
text=text.replace(" const resultLabel=s.excerpt?'完整程序运行结果':'运行结果';"," const resultLabel=s.excerpt?'完整程序运行结果':'运行结果';\n const compactResult=(s.output?.trimEnd().split('\\n').length??0)>3;")
text=text.replace("fontSize:32,fontFamily:mono,lineHeight:'36px'","fontSize:compactResult?30:32,fontFamily:mono,lineHeight:compactResult?'28px':'36px'")
text=text.replace("result.getBoundingClientRect().bottom>902","result.scrollHeight>117")
text=text.replace('Rust 进阶基础</div>','一小时学习数据结构</div>').replace('九个主题，继续学习','用 C++ 看懂数据与操作').replace('理解规则，再选择工具','先选结构，再说明理由')
text=text.replace("{s.chapterIndex===0?'从例子出发，逐步理解':'把知识点连成一个工作流程'}","{question?'最后一题：分别选择工具':'从具体问题出发，逐步理解'}")
(ROOT/'src/video.tsx').write_text(text,encoding='utf-8')
print('Approved second-lesson layout adapted to C++ and data-structure diagrams')
