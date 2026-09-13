// Run against the built preview or deployed site; no native desktop interaction.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const crypto=require('node:crypto');
const base=process.argv[2]||'http://127.0.0.1:4322';
const output=process.argv[3]||'output/verification-qa';
(async()=>{
 fs.mkdirSync(output,{recursive:true});
 const browser=await chromium.launch({headless:true});
 const errors=[];const failures=[];
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000},colorScheme:'dark'});
  page.on('pageerror',e=>errors.push(e.message));
  page.on('response',r=>{if(r.status()>=400&&r.url().startsWith(base))failures.push(r.status()+' '+r.url());});
  await page.goto(base+'/software/aero/verification/',{waitUntil:'networkidle'});
  assert.equal(await page.locator('h1').innerText(),'A finished solve can still be wrong.');
  assert.equal(await page.locator('tbody tr').count(),5);
  assert.equal(await page.locator('tbody .pass').count(),3);
  assert.equal(await page.locator('tbody .fail').count(),2);
  await page.selectOption('[data-case-choice]','pipe-underresolved');
  assert.match(await page.locator('[data-case-result]').innerText(),/REJECTED.*13\.963%/);
  assert.equal(await page.locator('[data-case-checks] .fail').count(),1);
  await page.selectOption('[data-case-choice]','pipe-wrong-viscosity');
  assert.equal(await page.locator('[data-case-checks] .fail').count(),2);
  await page.selectOption('[data-case-choice]','pipe-fine');
  assert.match(await page.locator('[data-case-result]').innerText(),/ACCEPTED.*0\.053%/);
  assert.match(await page.locator('#nozzle').innerText(),/negligible transverse/);
  assert.match(await page.locator('#cad').innerText(),/SOLVER NOT SUBMITTED/);
  for(const detail of await page.locator('details').all())await detail.locator('summary').click();
  for(const img of await page.locator('.bench img').all()){await img.scrollIntoViewIfNeeded();await img.evaluate(async e=>{if(!e.complete)await new Promise(r=>{e.onload=r;e.onerror=r;});});assert(await img.evaluate(e=>e.naturalWidth>0));}
  await page.evaluate(()=>scrollTo(0,0));
  await page.screenshot({path:output+'/desktop.png',fullPage:true});
  const asset=base+'/demos/aero/verification-bench-v1/';
  const manifest=await (await page.request.get(asset+'manifest.json')).json();
  let checked=0;
  for(const [name,hash] of Object.entries(manifest.files)){
    const response=await page.request.get(asset+name,{timeout:120000});assert.equal(response.status(),200,name);
    const body=await response.body();assert.equal(crypto.createHash('sha256').update(body).digest('hex'),hash,name);checked++;
  }
  for(const width of [390,768]){
    await page.setViewportSize({width,height:900});
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'horizontal overflow '+width);
    await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:output+'/viewport-'+width+'.png'});
  }
  await page.goto(base+'/software/aero/',{waitUntil:'networkidle'});
  assert.equal(await page.locator('#capability-papers a[href="/software/aero/verification/"]').count(),1);
  assert(!(await page.locator('body').innerText()).includes('each generated wall-resolved mesh'));
  await page.goto(base+'/software/aero/current/?case=verification-pipe-underresolved-v1',{waitUntil:'networkidle'});
  assert.match(await page.locator('[data-example-summary]').innerText(),/13\.963%.*REJECTED/);
  await page.locator('[data-stage]').nth(4).click();
  assert.match(await page.locator('[data-stage-needs]').innerText(),/REJECTED/);
  await page.locator('[data-stage]').nth(5).click();
  const frame=page.frameLocator('[data-proof-frame]');
  await frame.locator('tbody').waitFor();
  assert.equal(await frame.locator('tbody .fail').count(),2);
  assert.match(await frame.locator('tbody').innerText(),/underresolved/);
  assert.deepEqual(errors,[]);assert.deepEqual(failures,[]);
  const proof={base,checked_at:new Date().toISOString(),passed:true,public_assets_hash_verified:checked,pipe_passes:3,pipe_failures:2,gate_inspector:true,saved_case_and_embedded_proof:true,mobile_widths:[390,768],console_errors:errors,http_errors:failures};
  fs.writeFileSync(output+'/proof.json',JSON.stringify(proof,null,2));console.log(JSON.stringify(proof,null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
