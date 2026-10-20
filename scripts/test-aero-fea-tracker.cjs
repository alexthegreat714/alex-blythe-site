// Headless website QA only: no model, solver, desktop, or private-run interaction.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const base=(process.argv[2]||'http://127.0.0.1:4339').replace(/\/$/,'');
const out=process.argv[3]||'qa/aero-candidate002-progress';
const initial=JSON.parse(fs.readFileSync('public/demos/aero/fea-candidate002-validation/status.json','utf8'));
// Do not intercept Vite's /public/... JSON module import in development.
const endpoint=/^https?:\/\/[^/]+\/demos\/aero\/fea-candidate002-validation\/status\.json(?:\?.*)?$/;
(async()=>{
  fs.mkdirSync(out,{recursive:true});
  const browser=await chromium.launch({headless:true});
  try{
    for(const viewport of [{width:390,height:844},{width:1440,height:1000}]){
      const page=await browser.newPage({viewport,colorScheme:'dark'});
      const errors=[];page.on('pageerror',e=>errors.push(e.message));
      let current=structuredClone(initial);
      await page.route(endpoint,route=>route.fulfill({json:current}));
      await page.goto(base+'/software/aero/progress/',{waitUntil:'networkidle'});
      await page.waitForFunction(()=>document.getElementById('freshness').textContent.includes('terminal snapshot'));
      await page.waitForFunction(()=>document.getElementById('saved').textContent==='36');
      assert.equal(await page.locator('#percent').textContent(),'4.2%');
      assert.equal(await page.locator('#state-pill').textContent(),'Stopped · incomplete');
      assert.equal(await page.locator('[data-phase]').count(),10);
      assert.equal(await page.locator('#training-count').textContent(),'858 / 858 steps');
      assert.equal(await page.locator('.spinner').count(),0);
      assert.match(await page.locator('#activity-text').textContent(),/heartbeat/);
      assert.match(await page.locator('footer').first().textContent(),/not candidate002 live progress/);
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
      const bar=await page.locator('#progress-bar').boundingBox();
      assert(bar.y+bar.height<viewport.height,'Progress should be above fold');
      await page.screenshot({path:`${out}/${viewport.width}-stopped.png`,fullPage:true});
      // Corrupt updates retain last known snapshot; never turn into zero or running.
      current.saved_outputs=-1;
      await page.locator('#refresh').click();
      await page.waitForFunction(()=>document.getElementById('state-pill').textContent==='Refresh unavailable');
      assert.equal(await page.locator('#saved').textContent(),'36');
      current=structuredClone(initial);
      current.state='UNKNOWN';current.saved_outputs=null;current.percent=null;
      current.observed_at=null;current.last_phase=null;current.gate_breach_count=null;
      current.phases.forEach(p=>{p.saved=null;p.state='unknown';});
      Object.keys(current.closure).forEach(k=>current.closure[k]=false);
      await page.locator('#refresh').click();
      await page.waitForFunction(()=>document.getElementById('saved').textContent==='Unknown');
      assert.equal(await page.locator('#progress-bar').getAttribute('aria-valuenow'),null);
      assert.equal(await page.locator('#percent').textContent(),'Unknown');
      current=structuredClone(initial);
      current.state='COLLECTED_REVIEW_PENDING';current.collection_complete=true;
      current.saved_outputs=864;current.percent=100;current.gate_breach_count=0;
      current.phases.forEach(p=>{p.saved=p.total;p.state='outputs_saved';});
      await page.locator('#refresh').click();
      await page.waitForFunction(()=>document.getElementById('saved').textContent==='864');
      assert.match(await page.locator('#activity-text').textContent(),/Scoring and review are separate/);
      assert.match(await page.locator('.meaning').textContent(),/does not mean the model passed/);
      await page.unroute(endpoint);
      await page.route(endpoint,r=>r.fulfill({status:503,body:'offline fixture'}));
      await page.locator('#refresh').click();
      await page.waitForFunction(()=>document.getElementById('state-pill').textContent==='Refresh unavailable');
      assert.equal(await page.locator('#saved').textContent(),'864');
      assert.deepEqual(errors,[]);
      await page.close();
    }
    const page=await browser.newPage();
    await page.goto(base+'/software/aero/',{waitUntil:'networkidle'});
    assert.equal(await page.locator('a[href="/software/aero/progress/"]').count(),1);
    console.log(JSON.stringify({state:'PASS',viewports:2,terminal_unknown_corrupt_complete_and_offline:true,overview_link:true,models_called:0}));
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
