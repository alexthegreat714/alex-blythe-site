// Existing headless browser QA: no native desktop, model or solver interaction.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const base=(process.argv[2]||'http://127.0.0.1:4339').replace(/\/$/,'');
const out=process.argv[3]||'qa/aero-fea-progress';
const initial=JSON.parse(fs.readFileSync('public/demos/aero/fea-diagnostic-progress/status.json','utf8'));
(async()=>{
  fs.mkdirSync(out,{recursive:true});
  const browser=await chromium.launch({headless:true});
  const checks=[];
  try{
    for(const viewport of [{width:390,height:700},{width:1440,height:1000}]){
      const page=await browser.newPage({viewport,colorScheme:'dark'});
      const errors=[];page.on('pageerror',e=>errors.push(e.message));
      let current=structuredClone(initial);
      current.observed_at=new Date().toISOString();current.snapshot_source_fresh=true;
      current.state='RUNNING';current.activity_at_observation='recent_output_progress';
      current.saved_outputs=12;current.percent=6.3;current.phases[0].saved=12;
      await page.route('**/demos/aero/fea-diagnostic-progress/status.json*',route=>route.fulfill({json:current}));
      await page.goto(base+'/software/aero/progress/',{waitUntil:'networkidle'});
      await page.waitForFunction(()=>document.getElementById('saved').textContent==='12');
      assert.equal(await page.locator('#percent').textContent(),'6.3%');
      assert.equal(await page.locator('#spinner').isVisible(),true);
      assert.equal(await page.locator('[data-phase]').count(),4);
      const bar=await page.locator('#progress-bar').boundingBox();
      const activity=await page.locator('.activity').boundingBox();
      assert(bar.y+bar.height<viewport.height,'Progress must be above fold');
      assert(activity.y+activity.height<viewport.height,'Activity must be above fold');
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
      await page.screenshot({path:`${out}/${viewport.width}-running.png`,fullPage:true});
      current.observed_at=new Date(Date.now()-180000).toISOString();
      await page.locator('#refresh').click();
      await page.waitForFunction(()=>document.getElementById('spinner').hidden);
      assert.match(await page.locator('#activity-text').textContent(),/No fresh liveness/);
      current.observed_at=new Date().toISOString();current.state='INCOMPLETE_STOPPED';current.gate_breach_count=1;
      await page.locator('#refresh').click();
      await page.waitForFunction(()=>document.getElementById('state-pill').textContent==='Stopped · incomplete');
      assert.equal(await page.locator('#spinner').isVisible(),false);
      assert.equal(await page.locator('#saved').textContent(),'12');
      current.state='OUTPUTS_SAVED_SCORING_PENDING';current.collection_complete=true;current.saved_outputs=192;current.percent=100;
      current.phases.forEach(p=>{p.saved=48;p.state='outputs_saved';});
      await page.locator('#refresh').click();
      await page.waitForFunction(()=>document.getElementById('saved').textContent==='192');
      assert.match(await page.locator('#activity-text').textContent(),/Scoring and review are separate/);
      assert.match(await page.locator('.meaning').textContent(),/does not mean the model passed/);
      await page.unroute('**/demos/aero/fea-diagnostic-progress/status.json*');
      await page.route('**/demos/aero/fea-diagnostic-progress/status.json*',r=>r.fulfill({status:503,body:'offline fixture'}));
      await page.locator('#refresh').click();
      await page.waitForFunction(()=>document.getElementById('state-pill').textContent==='Refresh unavailable');
      assert.equal(await page.locator('#saved').textContent(),'192');
      assert.equal(await page.locator('#spinner').isVisible(),false);
      assert.deepEqual(errors,[]);
      checks.push({viewport,above_fold:true,no_horizontal_overflow:true,stale_stops_spinner:true,
        stopped_retains_progress:true,completion_not_quality:true,refresh_failure_retains_snapshot:true,page_errors:errors});
      await page.close();
    }
    const page=await browser.newPage();
    await page.goto(base+'/software/aero/',{waitUntil:'networkidle'});
    assert.equal(await page.locator('a[href="/software/aero/progress/"]').count(),1);
    fs.writeFileSync(`${out}/receipt.json`,JSON.stringify({state:'PASS',checks,overview_link:true,models_called:0},null,2));
    console.log(JSON.stringify({state:'PASS',viewports:checks.length,checks_per_viewport:7,overview_link:true}));
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
