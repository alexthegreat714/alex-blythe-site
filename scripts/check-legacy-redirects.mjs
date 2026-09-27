import assert from 'node:assert/strict';
const origin='https://alex-blythe.com';
const targets=[['/my-projects/','/software/'],['/resume/','/#experience']];
const rows=[],errors=[];
for(const [old,destination] of targets){
 for(const variant of [old,old.slice(0,-1),old+'index.html',old+'?audit=portfolio']){
  const request=origin+variant;
  const first=await fetch(request,{method:'HEAD',redirect:'manual',signal:AbortSignal.timeout(20000)});
  const location=first.headers.get('location');
  const finalURL=location?new URL(location,request).href:request;
  const final=location?await fetch(finalURL,{method:'HEAD',redirect:'manual',signal:AbortSignal.timeout(20000)}):first;
  const expected=new URL(destination,origin);if(variant.includes('?'))expected.search='?audit=portfolio';
  rows.push({oldURL:request,status:first.status,location,finalURL,finalStatus:final.status});
  try{assert.ok([301,308].includes(first.status),'not a permanent HTTP redirect');assert.equal(finalURL,expected.href,'unexpected Location');assert.equal(final.status,200,'destination is not a one-hop 200');}catch(e){errors.push({url:request,error:e.message});}
 }
}
console.log(JSON.stringify({observedAt:new Date().toISOString(),rows,errors},null,2));
if(errors.length)process.exitCode=1;
