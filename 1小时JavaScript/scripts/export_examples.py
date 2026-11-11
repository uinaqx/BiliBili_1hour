import json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]

def main():
    course=json.loads((ROOT/'public/course.json').read_text(encoding='utf8'));rows=['# JavaScript课程配套示例','','普通例子在对应目录执行 `node main.mjs`；网页例子打开 index.html。完整项目使用本地服务器，操作步骤见项目 README。','','|编号|内容|','|---|---|']
    for c in course['chapters']:
        for s in c['scenes']:
            d=ROOT/'examples'/s['key'];d.mkdir(parents=True,exist_ok=True)
            (d/s['filename']).write_text(s['code']+'\n',encoding='utf8')
            for f,text in s['fixtures'].items():(d/f).write_text(text,encoding='utf8')
            if s['kind']=='module':
                (d/'budget.mjs').write_text(s['code']+'\n',encoding='utf8')
                (d/'main.mjs').write_text('import {remaining} from "./budget.mjs";\nconsole.log(remaining(30, 25));\n',encoding='utf8')
            (d/'预期结果.txt').write_text(s['output'].replace('\\n','\n')+'\n',encoding='utf8')
            rows.append(f"| [{s['key']}]({s['key']}/) | {s['title']} |")
    (ROOT/'examples/README.md').write_text('\n'.join(rows)+'\n',encoding='utf8')
    print('EXAMPLES_EXPORTED',sum(len(c['scenes']) for c in course['chapters']),flush=True)

if __name__=='__main__':main()
