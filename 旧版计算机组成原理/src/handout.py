"""Reproducible printable reading companion, without external assets or services."""
import html
from pathlib import Path

def build_handout(root,course):
    esc=html.escape
    parts=['''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>计算机组成原理完整讲义</title><style>body{max-width:980px;margin:40px auto;padding:0 22px;font:17px/1.9 system-ui;color:#203045;background:#f5f7fb}h1{line-height:1.3}h2{margin-top:70px;border-top:3px solid #45a4cf;padding-top:25px}h3{font-size:25px}article{padding:24px;background:white;border:1px solid #dce2e8;border-radius:12px;margin:25px 0}p{white-space:pre-line}small{color:#657889}summary{cursor:pointer;color:#1378a8}img{width:100%;border-radius:8px}li{margin:5px 0}a{color:#0879ac}@media print{body{font-size:12pt;background:white;max-width:none}article{break-inside:avoid}details,details>*{display:block}}</style><h1>两小时建立计算机组成原理的完整框架</h1><p>大学课程学习 · 60镜完整讲稿 · 120分钟时间轴<br>配音暂不处理；本讲义包含全部教学文案与自测答案。</p><nav>''']
    for ch in course['chapters']:parts.append(f'<a href="#{ch["id"]}">{esc(ch["title"])}</a>　')
    parts.append('</nav>')
    for ch in course['chapters']:
        parts.append(f'<h2 id="{ch["id"]}">{esc(ch["title"])} <small>{ch["start"]//60}–{(ch["start"]+ch["duration"])//60}分钟</small></h2>')
        for s in course['scenes']:
            if s['chapter']!=ch['id']:continue
            parts.append(f'<article id="{s["id"]}"><h3>{s["id"]} {esc(s["title"])}</h3><details><summary>查看机制图</summary><img loading="lazy" src="review/{s["id"]}.png" alt="{esc(s["title"])}机制图"></details><p>{esc(s["narration"])}</p><details><summary>分镜说明</summary><p>{esc(s["visual"])}</p></details><p><strong>自测：</strong>{esc(s["question"])}</p><details><summary>查看答案</summary><p>{esc(s["answer"])}</p></details></article>')
    parts.append('<p>完整工程与练习见项目README及docs文件夹。所有模型的条件以分镜和技术说明为准。</p></html>')
    (root/'output/完整讲义.html').write_text(''.join(parts),encoding='utf-8')
