"""Pipeline chapter encoding behind an active, resumable still-frame render."""
import concurrent.futures,json,time
import render
def ready(c):
    while True:
        try:
            cache=json.loads((render.BUILD/'still-cache.json').read_text(encoding='utf-8'))
            expected=(render.BUILD/'current-source-hash.txt').read_text().strip()
            if all(cache.get(v['path'])==expected and (render.ROOT/'public'/v['path']).exists() for v in c['images']):break
        except (FileNotFoundError,json.JSONDecodeError):pass
        time.sleep(5)
    while True:
        try:render.chapter(c);break
        except json.JSONDecodeError:time.sleep(.2)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(ready,render.T['chapters']))
render.mux()
