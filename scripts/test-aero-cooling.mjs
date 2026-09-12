import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
import {chromium} from 'playwright';
const output='.qa/cooling/browser';await mkdir(output,{recursive:true});
const browser=await chromium.launch({headless:true,channel:'chrome'});
try{
 const context=await browser.newContext({viewport:{width:1440,height:1040}}),page=await context.newPage(),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 const preview=process.env.AERO_PREVIEW_ORIGIN;
 if(preview)await page.route('https://alex-blythe.com/**',async route=>{const u=new URL(route.request().url()),r=await fetch(preview+u.pathname+u.search);await route.fulfill({status:r.status,headers:{'content-type':r.headers.get('content-type')||'text/plain'},body:Buffer.from(await r.arrayBuffer())});});
 const state=()=>page.evaluate(()=>JSON.parse(localStorage.getItem('aero.cooling.screen.v1')));
 await page.goto('https://alex-blythe.com/software/aero/cooling/');
 await page.waitForFunction(()=>document.querySelector('[data-model]').textContent.includes('live conversation'));
 assert.ok(await page.locator('[data-prepare]').isDisabled());assert.match(await page.locator('[data-missing]').textContent(),/Heated length/);
 if(process.env.AERO_COOLING_CHAT==='1'){
   await page.locator('#question').fill('What specific missing geometry do you need before this cooling-channel comparison, and why? Do not assume dimensions.');
   await page.locator('[data-send]').click();await page.waitForFunction(()=>JSON.parse(localStorage.getItem('aero.cooling.screen.v1')||'{}').messages?.some(m=>m.role==='assistant'),null,{timeout:125000});
   const reply=(await state()).messages.find(m=>m.role==='assistant').content;assert.match(reply,/length|width/i);assert.doesNotMatch(reply,/parallel.plate|circular_area|channel_reynolds/i);await writeFile(output+'/model-reply.txt',reply);
 }
 await page.locator('[data-example]').click();await page.locator('[data-confirm]').check();
 await page.screenshot({path:output+'/01-requirements.png'});
 await page.locator('[data-prepare]').click();assert.equal(await page.locator('.katex').count(),4);await page.screenshot({path:output+'/02-math.png'});
 await page.locator('[data-stage]').nth(2).click();await page.locator('[data-geometry] canvas').waitFor();await page.screenshot({path:output+'/03-layouts.png'});
 for(const value of ['0','2','1']){await page.locator('[data-layout]').selectOption(value);await page.locator('[data-geometry] canvas').waitFor();}
 await page.locator('[data-stage]').nth(3).click();await page.waitForFunction(()=>!document.querySelector('[data-run]').disabled);
 if(process.env.AERO_COOLING_RUN!=='1')throw Error('Set AERO_COOLING_RUN=1 to authorize the real analytical/report job');
 if(process.env.AERO_COOLING_RESUME){await page.evaluate(id=>{const k='aero.cooling.screen.v1',s=JSON.parse(localStorage.getItem(k));s.id=id;s.status={state:'queued',message:'Resuming retained analytical evidence'};localStorage.setItem(k,JSON.stringify(s));},process.env.AERO_COOLING_RESUME);await page.reload();await page.locator('[data-stage]').nth(3).click();}
 else await page.locator('[data-run]').click();
 await page.waitForFunction(()=>JSON.parse(localStorage.getItem('aero.cooling.screen.v1')||'{}').id);
 const id=(await state()).id;await page.screenshot({path:output+'/04-running.png'});await page.reload();await page.locator('[data-stage]').nth(3).click();assert.equal((await state()).id,id);
 await page.waitForFunction(()=>JSON.parse(localStorage.getItem('aero.cooling.screen.v1')||'{}').status?.state==='complete',null,{timeout:130000});
 const completed=await state();assert.equal(completed.result.selected_layout,'B');assert.equal(completed.result.source,'ANALYTICAL_SCREENING');assert.ok(completed.result.checks_passed);
 await page.locator('[data-stage]').nth(4).click();await page.screenshot({path:output+'/05-results.png'});
 for(const [name,selector] of [['paper.pdf','[data-pdf]'],['evidence.zip','[data-evidence]']]){const r=await context.request.get(await page.locator(selector).getAttribute('href'));assert.equal(r.status(),200);await writeFile(output+'/'+name,await r.body());}
 await writeFile(output+'/result.json',JSON.stringify(completed.result));await writeFile(output+'/status.json',JSON.stringify(completed.status));await context.storageState({path:output+'/storage.json'});
 await page.locator('[data-stage]').nth(0).click();await page.locator('[data-input=wall_limit_c]').fill('40');await page.locator('[data-input=wall_limit_c]').blur();assert.equal((await state()).result,undefined);assert.equal((await state()).reviewed,false);await page.locator('[data-stage]').nth(4).click();assert.ok(await page.locator('[data-downloads]').isHidden());
 for(const width of [900,390]){await page.setViewportSize({width,height:900});await page.locator('[data-stage]').nth(0).click();assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.screenshot({path:output+`/mobile-${width}.png`,fullPage:true});}
 assert.deepEqual(errors,[]);const receipt={id,source:completed.result.source,selected_layout:completed.result.selected_layout,real_public_job:true,live_model:process.env.AERO_COOLING_CHAT==='1',staged_assets:Boolean(preview),refresh_resume:true,edit_invalidates:true,errors};await writeFile(output+'/acceptance.json',JSON.stringify(receipt,null,2));console.log(JSON.stringify(receipt));
}finally{await browser.close();}
