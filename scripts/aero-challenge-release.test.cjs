// Final-release QA: real downloads, byte hashes, chronology and browser usability.
// Runs headlessly; never interacts with the owner's native desktop or private VM.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const crypto=require('node:crypto');
const fs=require('node:fs');
const base=(process.argv[2]||'http://127.0.0.1:4325').replace(/\/$/,'');
const output=process.argv[3]||'output/challenge01/final-release-qa';
const prefix='/demos/aero/blind-validation-01-run-v1/';
const route='/software/aero/evidence/benchmarks/blind-validation-01/';
async function json(path){const r=await fetch(base+path,{signal:AbortSignal.timeout(120000)});assert.equal(r.status,200,path);return r.json();}
async function hash(path){
 const r=await fetch(base+path,{signal:AbortSignal.timeout(180000)});assert.equal(r.status,200,path);
 const h=crypto.createHash('sha256');let bytes=0;
 for await(const chunk of r.body){h.update(chunk);bytes+=chunk.length;}
 return {sha256:h.digest('hex'),size:bytes};
}
(async()=>{
 fs.mkdirSync(output,{recursive:true});
 const status=await json(prefix+'current-status.json');
 assert.equal(status.stage,'COMPARED_ANCHORED');assert.equal(status.completed,54);
 assert.equal(status.complete_predictions,54);assert(status.has_paper&&status.has_reproduction&&status.has_manifest);
 assert.equal(status.phases.length,6);assert(status.phases.every(p=>p.status==='COMPLETE'));
 const ledger=await json(prefix+'state.json');
 const stages=ledger.events.map(e=>e.stage);
 for(const [before,after] of [['CRITERIA_FROZEN_ANCHORED','SOLVE'],['PREDICTION_FROZEN_ANCHORED','REFERENCE_UNSEALED'],['REFERENCE_UNSEALED','COMPARED']])assert(stages.indexOf(before)>=0&&stages.indexOf(before)<stages.indexOf(after));
 assert(ledger.events.every((e,i,a)=>i===0||Date.parse(e.time)>=Date.parse(a[i-1].time)));
 const criteria=await json(prefix+'preregistration.json');
 const comparison=await json(prefix+'comparison.json');
 const prediction=await json(prefix+'blind_prediction.json');
 assert.equal(comparison.all_points.length,36);assert.equal(prediction.values.length,36);
 assert.equal(status.result,comparison.status);assert.equal(status.numerical_status,comparison.numerical_status);
 assert.equal(new Set(comparison.all_points.map(p=>p.quantity+'/'+p.station)).size,36);
 for(const q of criteria.quantities){
  const points=comparison.all_points.filter(p=>p.quantity===q);assert.equal(points.length,18);
  const rmse=Math.sqrt(points.reduce((s,p)=>s+(p.prediction-p.reference)**2,0)/points.length);
  assert(Math.abs(rmse-comparison.metrics[q].rmse)<1e-12);
 }
 if(prediction.numerical_status!=='PASS')assert.equal(comparison.status,'FAIL');
 const manifest=await json(prefix+'manifest.json');let files=0,bytes=0;
 assert.equal(manifest.file_count,manifest.files.length);
 assert.equal(new Set(manifest.files.map(x=>x.path)).size,manifest.file_count);
 for(const row of manifest.files){
  assert(!row.path.includes('..')&&!row.path.includes('\\')&&!/\.(env|key|pyc)$/.test(row.path));
  const actual=await hash(prefix+row.path);assert.equal(actual.sha256,row.sha256,row.path);assert.equal(actual.size,row.size,row.path);files++;bytes+=actual.size;
  if(files%15===0)console.log(JSON.stringify({verified_files:files,total:manifest.file_count}));
 }
 const index=await json(prefix+'evidence/run-index.json');assert.equal(index.cases.length,54);
 for(const row of index.cases){const m=manifest.files.find(x=>x.path===row.path);assert.equal(m.sha256,row.sha256);assert.equal(m.size,row.size);}
 const bundle=await hash(prefix+'reproduction.zip');assert(bundle.size>10000);
 const localBundle='public'+prefix+'reproduction.zip';
 assert.equal(bundle.sha256,crypto.createHash('sha256').update(fs.readFileSync(localBundle)).digest('hex'));
 const browser=await chromium.launch({headless:true});const errors=[];
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000},colorScheme:'dark'});page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base+route,{waitUntil:'networkidle'});
  assert.match(await page.locator('body').innerText(),/not fully blinded/);
  assert.equal(await page.locator('.timeline li').count(),6);
  assert(await page.getByRole('link',{name:'Read the technical paper'}).count());
  assert(await page.getByRole('link',{name:'Download reproduction package'}).count());
  const disclosure=page.getByText('Inspect convergence, conservation, wall resolution and actual meshes',{exact:true});await disclosure.focus();await page.keyboard.press('Enter');
  for(const w of [1440,768,390]){
   await page.setViewportSize({width:w,height:1000});
   const figs=page.locator('.challenge-figure img');
   for(let i=0;i<await figs.count();i++){await figs.nth(i).scrollIntoViewIfNeeded();await figs.nth(i).evaluate(img=>img.decode());}
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
   await page.screenshot({path:output+'/challenge-'+w+'.png',fullPage:true});
  }
  await page.goto(base+'/software/aero/current/?case=external-challenge01-run-v1',{waitUntil:'networkidle'});
  assert.match(await page.locator('[data-example-summary]').innerText(),/18 angles/);
  await page.locator('[data-stage]').nth(5).click();
  assert.equal(await page.locator('[data-proof-frame]').getAttribute('src'),route);
  assert(await page.locator('[data-proof-frame]').isVisible());
  await page.screenshot({path:output+'/saved-case.png',fullPage:true});
  assert.deepEqual(errors,[]);
 }finally{await browser.close();}
 const proof={passed:true,base,checked_at:new Date().toISOString(),stage:status.stage,result:status.result,all_points:36,case_archives:54,release_files_verified:files,release_bytes_verified:bytes,reproduction_sha256:bundle.sha256,chronology_verified:true,rmse_independently_recalculated:true,widths:[1440,768,390],saved_case_verified:true,console_errors:errors};
 fs.writeFileSync(output+'/proof.json',JSON.stringify(proof,null,2));console.log(JSON.stringify(proof,null,2));
})().catch(e=>{console.error(e);process.exit(1);});
