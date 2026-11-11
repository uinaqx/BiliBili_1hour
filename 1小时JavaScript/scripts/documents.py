import json,pathlib,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out'
def main():
    course=json.loads((ROOT/'public/course.json').read_text(encoding='utf8'));rows=['# 一小时学完JavaScript：完整讲稿',''];answers=['# 课堂练习与答案','']
    for c in course['chapters']:
        rows+=['## '+c['title'],'']
        for s in c['scenes']:
            rows+=['### '+s['key']+' '+s['title'],'','```'+('html' if s['kind']=='html' else 'javascript'),s['code'],'```','']
            for i,p in enumerate(s['parts']):
                rows += [p['text'],'']
                if p.get('think'):rows+=['（思考4秒）','']
            rows+=['本页总结：','']+['- '+n for n in s['notes']]+['','运行结果或操作预期：','','```text',s['output'].replace('\\n','\n'),'```','']
            if s['parts'][0].get('think'):
                answers+=['## '+s['key']+' '+s['title'],'',s['parts'][0]['text'],'','```javascript',s['code'],'```','',s['parts'][1]['text'],'','```text',s['output'].replace('\\n','\n'),'```','']
    for filename,data in [('完整讲稿.md',rows),('课堂练习与答案.md',answers)]:
        text='\n'.join(data)+'\n';(ROOT/'docs'/filename).write_text(text,encoding='utf8');(DEL/filename).write_text(text,encoding='utf8')
    (ROOT/'docs/参考资料.md').write_text('''# 内容核验资料

- [MDN：语法与类型](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Grammar_and_types)
- [MDN：函数](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Functions)
- [MDN：Promise](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Using_promises)
- [MDN：DOM入门](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Introduction)

示例在本机 Node.js v24.13.0 和 Chromium 中实际验证。浏览器交互由 Playwright 操作实际网页，包括记录新增、删除、刷新持久化及输入边界。
''',encoding='utf8')
    for n in ['章节目录.txt','逐页目录.txt']:
        if (DEL/n).exists():shutil.copy2(DEL/n,ROOT/'docs'/n)
    print('DOCUMENTS_READY',flush=True)
if __name__=='__main__':main()
