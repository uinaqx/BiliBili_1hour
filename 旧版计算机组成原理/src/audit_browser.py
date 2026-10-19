"""Load all 60 scenes, test controls and collect review frames / layout evidence."""
import asyncio
import hashlib
import json
import shutil
from pathlib import Path
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]

async def main():
    errors=[];review=[];bounds=[]
    shots=ROOT/'output/review';shots.mkdir(exist_ok=True)
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path=shutil.which('chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
        page=await browser.new_page(viewport={'width':1920,'height':1080})
        page.on('pageerror',lambda e:errors.append(str(e)))
        await page.set_content((ROOT/'output/index.html').read_text(),wait_until='load')
        await page.evaluate("document.body.classList.add('export')")
        await page.evaluate('document.fonts.ready')
        for i in range(60):
            states=[]
            for local in (18,68,96,110):
                await page.evaluate('(t)=>window.renderAt(t)',i*120+local)
                svg=await page.evaluate('window.getFrameSVG()')
                states.append(hashlib.sha256(svg.encode()).hexdigest())
                bad=await page.evaluate('''()=>Array.from(document.querySelectorAll('#stage svg text')).map(e=>{let b=e.getBBox(),zone=e.closest('#mechanism')?'mechanism':e.closest('#sidebar')?'sidebar':'canvas';return {text:e.textContent,zone,x:b.x,y:b.y,right:b.x+b.width,bottom:b.y+b.height}}).filter(b=>b.x<0||b.y<0||b.right>1920||b.bottom>1080||(b.zone==='mechanism'&&(b.x<96||b.right>1250||b.y<210||b.bottom>870))||(b.zone==='sidebar'&&(b.x<1348||b.right>1815||b.y<240||b.bottom>840)))''')
                bounds.extend(dict(scene=f'S{i+1:02d}',time=local,**b) for b in bad)
            await page.evaluate('(t)=>window.renderAt(t)',i*120+68)
            await page.locator('#stage').screenshot(path=str(shots/f'S{i+1:02d}.png'))
            review.append(dict(id=f'S{i+1:02d}',rendered_states=4,distinct_svg_states=len(set(states)),layout='ok' if not any(b['scene']==f'S{i+1:02d}' for b in bounds) else 'out_of_bounds'))
        # Seek is deterministic even after viewing another scene.
        await page.evaluate('window.renderAt(2468)');a=await page.evaluate('window.getFrameSVG()')
        await page.evaluate('window.renderAt(5);window.renderAt(2468)');b=await page.evaluate('window.getFrameSVG()')
        deterministic=a==b
        await page.evaluate("document.body.classList.remove('export')")
        await page.locator('nav button').nth(20).click()
        navigation=await page.evaluate('window.currentScene')=='S21'
        await page.locator('#next').click();next_ok=await page.evaluate('window.currentScene')=='S22'
        await page.locator('#prev').click();prev_ok=await page.evaluate('window.currentScene')=='S21'
        await page.locator('#play').click();await page.wait_for_timeout(250)
        playing=await page.evaluate('window.currentLocalTime')>0
        await page.locator('#play').click()
        await browser.close()
    result=dict(page_errors=errors,out_of_bounds=bounds,deterministic_seek=deterministic,navigation=navigation,next=next_ok,previous=prev_ok,playback=playing,scenes=review)
    (ROOT/'output/browser_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k!='scenes'},ensure_ascii=False))
    if errors or bounds or not all((deterministic,navigation,next_ok,prev_ok,playing)):raise SystemExit(1)

if __name__=='__main__':asyncio.run(main())
