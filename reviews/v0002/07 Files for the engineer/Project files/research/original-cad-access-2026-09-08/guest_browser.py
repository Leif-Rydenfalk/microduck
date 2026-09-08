from pathlib import Path
import json,hashlib
from playwright.sync_api import sync_playwright
p=Path(__file__).resolve().parent
url='https://cad.onshape.com/documents/804927696f06d877f3f1803e/w/5b75db19292e71970de02dee/e/ef6e972847fec8d82570b35e'
with sync_playwright() as play:
 browser=play.chromium.launch(channel='chrome',headless=True)
 context=browser.new_context(viewport={'width':1400,'height':1000})
 page=context.new_page();res=page.goto(url,wait_until='domcontentloaded',timeout=45000)
 try:page.wait_for_load_state('networkidle',timeout=15000)
 except Exception:pass
 page.wait_for_timeout(3000)
 text=page.locator('body').inner_text();(p/'guest-visible.txt').write_text(text)
 page.screenshot(path=str(p/'guest-document.png'),full_page=True)
 r={'date':'2026-09-08','requested_url':url,'final_url':page.url,'title':page.title(),'navigation_status':res.status if res else None,'isolation':'Fresh nonpersistent Playwright context, channel chrome, headless. No profile/cookies/credentials imported.','visible_text_file':'guest-visible.txt','visible_text_sha256':hashlib.sha256((p/'guest-visible.txt').read_bytes()).hexdigest(),'screenshot':'guest-document.png','screenshot_sha256':hashlib.sha256((p/'guest-document.png').read_bytes()).hexdigest()}
 (p/'guest-browser.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r));print(text[:1200]);browser.close()
