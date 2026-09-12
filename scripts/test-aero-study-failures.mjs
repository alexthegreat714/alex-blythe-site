// Explicit failure fixtures only. This script never submits a real solver job.
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require('playwright');
const browser=await chromium.launch({headless:true,channel:'chrome'});
const page=await browser.newPage({viewport:{width:1440,height:950}});
let mode='quota',posts=[];const id='c'.repeat(48);
await page.route('**/study/**',async route=>{
  const request=route.request(),url=new URL(request.url());let status=200,body={};
  if(url.pathname.endsWith('/health'))body={ready:true};
  else if(request.method()==='POST'){
    posts.push(request.postDataJSON());
    if(mode==='quota'){status=429;body={error:'Fixture: study budget reached'};}else{status=202;body={id};}
  }else if(mode==='expired'){status=404;body={error:'Fixture: evidence expired'};}
  else body={id,state:'running',worker_offline:true,completed:1,progress:11,message:'Fixture: worker unavailable'};
  await route.fulfill({status,contentType:'application/json',body:JSON.stringify(body)});
});
try{
  await page.goto('http://127.0.0.1:4322/software/aero/current/?study=channel');
  await page.locator('[data-study-confirm]').check();await page.locator('[data-stage="4"]').click();
  await page.locator('[data-study-run]').click();
  await page.waitForFunction(()=>document.querySelector('[data-study-notice]').textContent.includes('budget reached'));
  assert.equal(await page.locator('[data-study-run]').isEnabled(),true);
  mode='offline';await page.locator('[data-study-run]').click();
  await page.waitForFunction(()=>document.querySelector('[data-study-job-message]').textContent.includes('worker unavailable'));
  assert.equal(posts[0].request_id,posts[1].request_id,'Retry after uncertain submission must be idempotent');
  assert.equal(await page.locator('[data-stage="4"] i').evaluate(el=>getComputedStyle(el).backgroundColor),'rgb(228, 120, 120)');
  await page.locator('[data-stage="0"]').click();assert.equal(await page.locator('[data-study-input="gap_mm"]').isDisabled(),true);
  mode='expired';await page.reload();await page.locator('[data-stage="4"]').click();
  await page.waitForFunction(()=>document.querySelector('[data-study-notice]').textContent.includes('unavailable'));
  assert.equal(await page.locator('[data-study-run]').isEnabled(),true);
  mode='offline';await page.locator('[data-study-run]').click();
  await page.waitForFunction(()=>document.querySelector('[data-study-job-message]').textContent.includes('worker unavailable'));
  assert.notEqual(posts[2].request_id,posts[1].request_id,'A terminal failed run needs a fresh submission UUID');
  console.log('PASS explicit UI fixtures: quota preservation, idempotent retry, offline red bars, in-flight input lock, expired result failure, fresh retry UUID. No real solver calls.');
}finally{await browser.close();}
