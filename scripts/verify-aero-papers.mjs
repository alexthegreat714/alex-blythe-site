import assert from 'node:assert/strict';
import {mkdir} from 'node:fs/promises';
import {chromium} from 'playwright';
const origin=process.env.AERO_VERIFY_ORIGIN||'https://alex-blythe.com';
await mkdir('.qa/cooling/papers',{recursive:true});
const b=await chromium.launch({headless:true,channel:'chrome'});
try{const c=await b.newContext(),p=await c.newPage();await p.setViewportSize({width:1440,height:1000});await p.goto(origin+'/software/aero/#capability-papers');const section=p.locator('#capability-papers');assert.equal(await section.locator('article').count(),2);
for(const a of await section.locator('a').all()){const href=await a.getAttribute('href'),r=await c.request.get(origin+href);assert.equal(r.status(),200,href);}
await p.waitForFunction(()=>[...document.querySelectorAll('#capability-papers img')].every(i=>i.complete&&i.naturalWidth>0));await section.screenshot({path:'.qa/cooling/papers/desktop.png'});
for(const width of [900,390]){await p.setViewportSize({width,height:950});assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await section.screenshot({path:'.qa/cooling/papers/'+width+'.png'});}
await p.goto(origin+'/software/aero/current/');assert.ok(await p.getByRole('link',{name:'Cooling study',exact:true}).isVisible());assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
console.log('Both paper cards, all paper/evidence/study links, chart images, 900/390 px layouts and main-workspace cooling link: PASS');}finally{await b.close();}
