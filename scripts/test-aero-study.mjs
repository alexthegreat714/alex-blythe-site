// Staged static assets may be served on the real website origin; all study/model
// calls remain real public calls. No solver responses are mocked in this test.
import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require('playwright');
const browser=await chromium.launch({headless:true,channel:'chrome'});
const context=await browser.newContext({viewport:{width:1440,height:960}});
const page=await context.newPage();
const errors=[];page.on('pageerror',error=>errors.push(error.message));
const output='.qa/channel-study/browser';await mkdir(output,{recursive:true});
const preview=process.env.AERO_PREVIEW_ORIGIN;
if(preview)await page.route('https://alex-blythe.com/**',async route=>{
  const url=new URL(route.request().url());const response=await fetch(preview+url.pathname+url.search);
  await route.fulfill({status:response.status,headers:{'content-type':response.headers.get('content-type')||'text/plain'},body:Buffer.from(await response.arrayBuffer())});
});
const state=()=>page.evaluate(()=>{const library=JSON.parse(localStorage.getItem('aero.current.caseLibrary.v1'));return library.cases.find(c=>c.id===library.activeCaseId).study;});
const stage=async i=>{await page.locator(`[data-stage="${i}"]`).click();};
try{
  await page.goto('https://alex-blythe.com/software/aero/current/?study=channel');
  await page.locator('[data-channel-study]').waitFor();
  await page.waitForFunction(()=>document.querySelector('[data-solver-state]').dataset.online==='true');
  assert.equal(await page.locator('[data-study-run]').isDisabled(),true);
  if(process.env.AERO_STUDY_FLOW)await page.locator('[data-study-input="flow_ml_s"]').fill(process.env.AERO_STUDY_FLOW);
  if(process.env.AERO_STUDY_BUDGET)await page.locator('[data-study-input="budget_pa"]').fill(process.env.AERO_STUDY_BUDGET);
  await page.locator('[data-study-confirm]').check();
  const briefDownload=page.waitForEvent('download');await page.locator('[data-study-brief]').click();await (await briefDownload).saveAs(output+'/brief.md');
  await page.screenshot({path:output+'/01-requirements.png'});
  await page.locator('[data-study-prepare]').click();
  assert.equal(await page.locator('[data-study-math] .katex').count(),2);
  await page.screenshot({path:output+'/02-math.png'});
  if(process.env.AERO_STUDY_CHAT==='1'){
    await page.waitForFunction(()=>document.querySelector('[data-model-state]').dataset.state==='ready');
    await page.locator('#message').fill('Given this channel brief, why does changing the gap have such a strong effect on pressure drop? Keep all supplied values unchanged and show the parallel-plate relation.');
    await page.locator('[data-send]').click();
    await page.locator('.turn.assistant').waitFor({timeout:125000});
    const reply=await page.locator('.turn.assistant').last().textContent();
    assert.ok(reply.length>40);await writeFile(output+'/model-before.txt',reply);
    assert.match(reply,/invers|one eighth|divid.*eight/i,'The model must explain the checked inverse-cubic trend');
    assert.ok(!/increases with gap|directly related to the gap|equation_ids/.test(reply),'The observed wrong trend/internal identifier must not return');
    assert.equal((await state()).reviewed,true,'Chat cannot silently rewrite the reviewed solver controls');
  }
  for(const [i,name] of [[2,'03-geometry'],[3,'04-mesh']]){
    await stage(i);await page.locator('[data-study-viewport] canvas').waitFor();
    assert.ok(await page.locator('[data-study-viewport] canvas').evaluate(canvas=>canvas.width>100));
    await page.screenshot({path:output+'/'+name+'.png'});
  }
  await stage(4);
  assert.equal(await page.locator('[data-study-run]').isDisabled(),false);
  if(process.env.AERO_STUDY_RUN!=='1')throw Error('Set AERO_STUDY_RUN=1 to authorize this real bounded test run.');
  await page.locator('[data-study-run]').click();
  await page.waitForFunction(()=>{const l=JSON.parse(localStorage.getItem('aero.current.caseLibrary.v1'));return l.cases.find(c=>c.id===l.activeCaseId).study.runId;});
  const id=(await state()).runId;
  await page.screenshot({path:output+'/05-running.png'});
  await page.reload();await stage(4);
  assert.equal((await state()).runId,id,'Refresh must resume the same job');
  await page.waitForFunction(()=>{const l=JSON.parse(localStorage.getItem('aero.current.caseLibrary.v1'));return l.cases.find(c=>c.id===l.activeCaseId).study.result;},null,{timeout:330000});
  const completed=await state();assert.equal(completed.result.source,'LIVE_OPENFOAM');assert.equal(completed.result.checks_passed,true);
  if(process.env.AERO_STUDY_FLOW==='25'&&process.env.AERO_STUDY_BUDGET==='40'){
    assert.equal(completed.result.selected_gap_mm,2.5,'Changed conditions must change the selected gap');
    assert.ok(Math.abs(completed.result.variants[1].pressure_drop_pa/60.06269040045428-1.25)<.01,'Computed nominal pressure must respond to the higher flow');
  }
  await stage(5);await page.locator('[data-study-viewport] canvas').waitFor();
  assert.ok((await page.locator('[data-study-decision]').textContent()).includes('mm'));
  await page.screenshot({path:output+'/06-result.png'});
  await page.locator('[data-study-field]').selectOption('pressure_pa');
  assert.match(await page.locator('[data-study-viewport-caption]').textContent(),/Computed pressure/);
  await page.locator('[data-study-inspect]').click();
  await page.frameLocator('[data-study-proof]').getByRole('heading',{name:'Which channel gap meets the pressure-drop budget?'}).waitFor();
  await page.screenshot({path:output+'/07-proof.png'});
  const reportDownload=page.waitForEvent('download');await page.locator('[data-study-report]').click();await (await reportDownload).saveAs(output+'/report.html');
  if(process.env.AERO_STUDY_CHAT==='1'){
    await page.locator('#message').fill('Explain the completed channel study result: which gap should I choose for my budget and what does the analytical comparison actually prove? Use the attached verified result.');
    await page.locator('[data-send]').click();
    await page.waitForFunction(()=>document.querySelectorAll('.turn.assistant').length>=2,null,{timeout:125000});
    const reply=await page.locator('.turn.assistant').last().textContent();
    assert.ok(!reply.includes('I have not run or verified'),'Verified solver result must remain available for explanation');
    await writeFile(output+'/model-after.txt',reply);
  }
  await page.reload();await stage(5);assert.equal((await state()).result.id,id);
  await context.storageState({path:output+'/storage.json'});
  // An edited case must not continue presenting an old run as current proof.
  await stage(0);await page.locator('[data-study-input="budget_pa"]').fill('43');await page.locator('[data-study-input="budget_pa"]').blur();
  assert.equal((await state()).reviewed,false);assert.equal((await state()).result,undefined);
  assert.equal((await state()).history[0].id,id);
  await stage(5);assert.ok(await page.locator('[data-study-downloads]').isHidden());assert.ok(await page.locator('[data-study-history]').isVisible());
  for(const width of [900,390]){await page.setViewportSize({width,height:900});await stage(0);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.screenshot({path:output+`/width-${width}.png`,fullPage:true});}
  assert.deepEqual(errors,[]);
  const summary={id,inputs:completed.inputs,selected_gap_mm:completed.result.selected_gap_mm,elapsed_seconds:completed.result.elapsed_seconds,checks_passed:completed.result.checks_passed,staged_assets:Boolean(preview),real_public_model:process.env.AERO_STUDY_CHAT==='1',real_public_solver:true,refresh_resume:true,changed_inputs_invalidated:true,errors};
  await writeFile(output+'/acceptance.json',JSON.stringify(summary,null,2));console.log(JSON.stringify(summary));
}finally{await browser.close();}
