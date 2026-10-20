// Headless website QA only: no model, solver, desktop or private-run interaction.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const base=(process.argv[2]||'http://127.0.0.1:4339').replace(/\/$/,'');
const out=process.argv[3]||'qa/aero-candidate002-progress';
const initial=JSON.parse(fs.readFileSync('public/demos/aero/fea-candidate002-validation/status.json','utf8'));
const endpoint=/^https?:\/\/[^/]+\/demos\/aero\/fea-candidate002-validation\/status\.json(?:\?.*)?$/;
(async()=>{
  fs.mkdirSync(out,{recursive:true});
  const browser=await chromium.launch({headless:true});
  try{
    for(const viewport of [{width:390,height:844},{width:1440,height:1000}]){
      const page=await browser.newPage({viewport,colorScheme:'dark'});
      const errors=[];page.on('pageerror',e=>errors.push(e.message));
      let current=structuredClone(initial);
      current.observed_at=new Date().toISOString();current.published_at=current.observed_at;
      await page.route(endpoint,route=>route.fulfill({json:current}));
      await page.goto(base+'/software/aero/progress/',{waitUntil:'networkidle'});
      await page.waitForFunction(()=>document.getElementById('state-pill').textContent==='Last observed running');
      assert.equal(await page.locator('#saved').textContent(),String(current.saved_outputs));
      assert.equal(await page.locator('#percent').textContent(),`${current.percent}%`);
      assert.equal(await page.locator('[data-phase]').count(),10);
      assert.equal(await page.locator('#training-count').textContent(),'858 / 858 steps');
      assert.match(await page.locator('#snapshot-note').textContent(),/every 15 minutes/);
      assert.match(await page.locator('footer').first().textContent(),/not candidate002 live progress/);
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
      const bar=await page.locator('#progress-bar').boundingBox();
      assert(bar.y+bar.height<viewport.height,'Progress should be above fold');
      await page.screenshot({path:`${out}/${viewport.width}-running.png`,fullPage:true});
      // Time passing alone invalidates a running claim; no new snapshot required.
      await page.evaluate(()=>{window.__realNow=Date.now;Date.now=()=>window.__realNow()+1_300_000;});
      await page.locator('#refresh').click();
      await page.waitForFunction(()=>document.getElementById('state-pill').textContent==='Observation stale');
      assert.match(await page.locator('#activity-text').textContent(),/current execution is not asserted/);
      await page.screenshot({path:`${out}/${viewport.width}-stale.png`,fullPage:true});
      await page.evaluate(()=>{Date.now=window.__realNow;});
      const saved=current.saved_outputs;current.saved_outputs=-1;
      await page.locator('#refresh').click();
      await page.waitForFunction(()=>document.getElementById('state-pill').textContent==='Refresh unavailable');
      assert.equal(await page.locator('#saved').textContent(),String(saved));
      current=structuredClone(initial);current.observed_at=new Date().toISOString();
      current.state='INITIALIZING';current.saved_outputs=null;current.percent=null;
      current.phases[0].saved=null;current.phases[0].state='initializing';
      await page.locator('#refresh').click();
      await page.waitForFunction(()=>document.getElementById('state-pill').textContent==='Model initializing');
      assert.equal(await page.locator('#saved').textContent(),'Unknown');
      assert.equal(await page.locator('#progress-bar').getAttribute('aria-valuenow'),null);
      current.state='UNKNOWN';current.observed_at=null;current.last_phase=null;current.gate_breach_count=null;
      current.phases.forEach(p=>{p.saved=null;p.state='unknown';});
      await page.locator('#refresh').click();
      await page.waitForFunction(()=>document.getElementById('state-pill').textContent==='Status unknown');
      current=structuredClone(initial);current.observed_at=new Date().toISOString();
      current.state='COLLECTED_REVIEW_PENDING';current.collection_complete=true;
      current.saved_outputs=864;current.percent=100;current.gate_breach_count=0;
      current.phases.forEach(p=>{p.saved=p.total;p.state='outputs_saved';});
      await page.locator('#refresh').click();
      await page.waitForFunction(()=>document.getElementById('saved').textContent==='864');
      assert.match(await page.locator('#activity-text').textContent(),/Scoring and review are separate/);
      assert.match(await page.locator('.meaning').textContent(),/does not mean the model passed/);
      assert.equal(await page.locator('[data-closure] strong').filter({hasText:'Verified'}).count(),0);
      current.state='INCOMPLETE_STOPPED';current.collection_complete=false;
      await page.locator('#refresh').click();
      await page.waitForFunction(()=>document.getElementById('state-pill').textContent==='Stopped · incomplete');
      assert.match(await page.locator('#next-text').textContent(),/separate authorization/);
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
    console.log(JSON.stringify({state:'PASS',viewports:2,running_stale_initialization_unknown_corrupt_terminal_offline:true,overview_link:true,models_called:0}));
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
