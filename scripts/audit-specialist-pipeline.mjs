import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.AERO_QA_PLAYWRIGHT_MODULE || 'playwright');
const base=process.argv[2] || 'http://127.0.0.1:4337';
const output=process.argv[3] || path.resolve('qa/specialist-pipeline-2026-10-10');
const route='/software/aero/evidence/reports/specialist-pipeline-2026-10-10/';
const assets='/demos/aero/specialist-pipeline-2026-10-10/';
await fs.mkdir(output,{recursive:true});
const browser=await chromium.launch({headless:true});
const results=[];const errors=[];
try {
  for(const width of [390,1440]) {
    for(const theme of ['light','dark']) {
      const context=await browser.newContext({viewport:{width,height:1000},colorScheme:theme});
      const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
      const response=await page.goto(base+route,{waitUntil:'networkidle'});
      if(response.status()!==200)throw new Error('Report route HTTP '+response.status());
      await page.locator('h1').waitFor();await page.evaluate(()=>document.fonts.ready);
      await page.evaluate(()=>{for(const image of document.images)image.loading='eager';});
      await page.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0));
      const proof=await page.evaluate(()=>({title:document.title,date:document.querySelector('time')?.dateTime,
        overflow:document.documentElement.scrollWidth>innerWidth+1,
        images:[...document.images].map(i=>({src:i.getAttribute('src'),loaded:i.complete&&i.naturalWidth>0})),
        canonical:document.querySelector('link[rel=canonical]')?.href,
        links:[...document.querySelectorAll('a[href]')].map(a=>a.getAttribute('href'))}));
      if(proof.date!=='2026-10-10'||proof.overflow||proof.images.some(i=>!i.loaded))throw new Error('Layout/image/date failure: '+JSON.stringify(proof));
      if(proof.canonical!=='https://alex-blythe.com'+route)throw new Error('Wrong canonical URL');
      await page.screenshot({path:path.join(output,`${width}-${theme}.png`),fullPage:true});
      await page.screenshot({path:path.join(output,`${width}-${theme}-top.png`),fullPage:false});
      if(theme==='light')await page.locator('.field-grid').screenshot({path:path.join(output,`${width}-fields.png`)});
      results.push({width,theme,...proof});await context.close();
    }
  }
  const context=await browser.newContext();const page=await context.newPage();
  for(const route2 of ['/software/aero/','/software/aero/evidence/']) {
    const response=await page.goto(base+route2,{waitUntil:'domcontentloaded'});
    if(response.status()!==200 || await page.locator(`a[href="${route}"]`).count()===0)throw new Error('Missing discovery link on '+route2);
  }
  const manifestResponse=await page.request.get(base+assets+'manifest.json');
  if(manifestResponse.status()!==200)throw new Error('Manifest unavailable');
  const manifest=await manifestResponse.json();let verified=0;
  for(const item of manifest.files) {
    const response=await page.request.get(base+assets+item.path);
    if(response.status()!==200)throw new Error('Asset missing: '+item.path);
    const data=await response.body();const digest=createHash('sha256').update(data).digest('hex');
    if(digest!==item.sha256||data.length!==item.bytes)throw new Error('Public asset mismatch: '+item.path);verified++;
  }
  if(errors.length)throw new Error('Browser errors: '+errors.join('; '));
  await fs.writeFile(path.join(output,'acceptance.json'),JSON.stringify({base,route,state:'passed',layouts:results,assets_verified:verified,browser_errors:errors,at:new Date().toISOString()},null,2));
  console.log(JSON.stringify({state:'passed',base,layouts:4,assets_verified:verified,output}));
} finally { await browser.close(); }
