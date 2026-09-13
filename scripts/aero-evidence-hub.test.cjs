// Headless local/deployed QA. Never controls the native desktop.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const crypto=require('node:crypto');
const base=(process.argv[2]||'http://127.0.0.1:4322').replace(/\/$/,'');
const output=process.argv[3]||'output/evidence-qa';
const digest=b=>crypto.createHash('sha256').update(b).digest('hex');
(async()=>{
 fs.mkdirSync(output,{recursive:true});
 const browser=await chromium.launch({headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000},colorScheme:'dark'});
  const errors=[],links=new Set();page.on('pageerror',e=>errors.push(e.message));
  async function get(path){const r=await page.request.get(base+path,{timeout:120000});assert.equal(r.status(),200,path);return r;}
  const root='/software/aero/evidence/';
  for(const route of [root,root+'benchmarks/',root+'benchmarks/blind-validation-01/']){
   await page.goto(base+route,{waitUntil:'networkidle'});
   assert.equal(await page.locator('h1').count(),1);
   assert.equal(await page.locator('nav[aria-label="Aero public navigation"] a').count(),4);
   assert.equal(await page.locator('nav[aria-label="Aero public navigation"] a').last().getAttribute('href'),'https://sky.alex-blythe.com/aero/');
   for(const href of await page.locator('.evidence-shell a').evaluateAll(xs=>xs.map(x=>x.getAttribute('href'))))if(href.startsWith('/'))links.add(href);
   if(route===root){
    assert.equal(await page.locator('[data-disciplines]').count(),5);
    for(const [name,count] of [['CFD',2],['Thermal',2],['Structural',1],['CAD / Geometry',1],['All',5]]){
     const button=page.getByRole('button',{name,exact:true});await button.focus();await page.keyboard.press('Enter');
     assert.equal(await page.locator('[data-disciplines]:visible').count(),count);
     assert.equal(await button.getAttribute('aria-pressed'),'true');
    }
   }
   if(route.includes('blind-validation')){
    assert.equal(await page.locator('.timeline li').count(),6);
    assert.deepEqual(await page.locator('.timeline span').allTextContents(),Array(6).fill('NOT OCCURRED'));
    assert.match(await page.locator('body').innerText(),/13 synthetic software tests/);
   }
   for(const width of [1440,768,390]){
    await page.setViewportSize({width,height:1000});
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'overflow '+route+' '+width);
    await page.screenshot({path:output+'/'+(route===root?'hub':route.includes('blind-validation')?'challenge':'register')+'-'+width+'.png',fullPage:width===1440});
   }
  }
  for(const href of links){await get(href.split('#')[0]);}
  const index=await(await get('/demos/aero/evidence-index-v1/index.json')).json();
  assert.equal(index.structural.solves,21);assert.equal(index.channel.solves,9);
  assert.equal(index.channel.paper_artifacts,200);assert.equal(index.thermal.paper_artifacts,41);
  let oldHashes=0;
  for(const [path,a] of Object.entries(index.artifacts)){
   const b=await(await get(path)).body();assert.equal(b.length,a.size,path);assert.equal(digest(b),a.sha256,path);oldHashes++;
  }
  assert.equal(oldHashes,62);
  const prep='/demos/aero/blind-validation-01-preparation-v1/';
  const manifest=await(await get(prep+'manifest.json')).json();
  for(const a of manifest.files){const b=await(await get(prep+a.path)).body();assert.equal(b.length,a.size,a.path);assert.equal(digest(b),a.sha256,a.path);}
  const state=await(await get(prep+'status.json')).json();
  assert.equal(state.production_runs,0);assert.equal(state.scientific_result,null);assert.equal(state.status,'NOT_EVALUATED');
  assert(Object.values(state.scientific_hashes).every(x=>x===null));assert(Object.values(state.scientific_commits).every(x=>x===null));
  await page.goto(base+'/software/aero/',{waitUntil:'networkidle'});
  assert(await page.locator('#capability-papers a[href="/software/aero/evidence/"]').count()>0);
  assert(!(await page.locator('body').innerText()).includes('each generated wall-resolved mesh'));
  assert.deepEqual(errors,[]);
  const proof={base,checked_at:new Date().toISOString(),passed:true,routes:3,existing_source_hashes_verified:oldHashes,preparation_hashes_verified:manifest.files.length,internal_links_checked:links.size,mobile_widths:[390,768],keyboard_filters:true,scientific_challenge:'NOT_EVALUATED',console_errors:errors};
  fs.writeFileSync(output+'/proof.json',JSON.stringify(proof,null,2));console.log(JSON.stringify(proof,null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
