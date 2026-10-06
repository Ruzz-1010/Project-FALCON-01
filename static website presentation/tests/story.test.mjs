import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,readdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {chapters,chapterCount,components,createLink,setLink,tickLink,waveSamples,forecastSamples,linePath,phases,funding,fundingRange} from '../story.js';
const read=path=>readFileSync(new URL(path,import.meta.url),'utf8');

test('Every required chapter exists exactly once in the new static story',()=>{
  const html=read('../index.html');
  assert.equal(chapters.length,chapterCount);
  assert.equal([...html.matchAll(/data-chapter="\d{1,2}"/g)].length,chapterCount);
  // Every chapter index appears exactly once as a data-chapter attribute.
  // Fifteen chapters: the wrap-up merges Validation+Status, Scope+Risks and
  // Impact+Funding into single pages, so the CAD-tuned chapters 0–9 keep
  // their original numbers and only the tail was renumbered.
  for(let i=0;i<chapterCount;i++)assert.equal(html.split(`data-chapter="${i}"`).length,2);
  for(const id of ['ocean','objectives','buoy','sensors','controller','radio','shore','waves','prediction','dashboard','validation','risks','roadmap','funding','connected'])assert.ok(html.includes(`id="${id}"`));
  const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);assert.equal(new Set(ids).size,ids.length);
});
test('LoRa outage keeps sensing and original timestamps without accepting packets at shore',()=>{
  let state=tickLink(createLink(),'initial');state=setLink(state,false);
  for(let i=0;i<12;i++)state=tickLink(state,`sample-${i}`);
  assert.equal(state.received.length,1);assert.equal(state.buffer.length,12);
  assert.equal(state.buffer[0].timestamp,'sample-0');assert.equal(state.buffer.at(-1).id,13);
});
test('Recovery drains backlog, prevents duplicates and restores chronological IDs',()=>{
  let state=setLink(createLink(),false);
  for(let i=0;i<20;i++)state=tickLink(state,`original-${i}`);
  const original=state.buffer.map(p=>({...p}));
  state=setLink(state,true);
  for(let i=0;i<10;i++)state=tickLink(state,`recovery-${i}`);
  assert.equal(state.buffer.length,0);assert.equal(state.received.length,30);
  assert.deepEqual(state.received.slice(0,20),original);
  state={...state,buffer:[original[0],original[0]]};state=tickLink(state,'retry');
  assert.equal(state.received.length,31);
  assert.deepEqual(state.received.map(p=>p.id),Array.from({length:31},(_,i)=>i+1));
});
test('Repeated interruptions do not reset packet sequence or lose the queue',()=>{
  let state=createLink();
  for(let i=0;i<5;i++){state=setLink(state,false);state=tickLink(state,`offline-${i}`);state=setLink(state,true);state=tickLink(state,`online-${i}`);}
  assert.equal(state.received.length,10);assert.equal(state.sequence,10);assert.equal(state.buffer.length,0);
});
test('Forecast meets history at NOW without a fabricated jump; data remain explicitly illustrative',()=>{
  const h=waveSamples(),f=forecastSamples(h.at(-1));assert.equal(f[0],h.at(-1));
  assert.ok(h.every(Number.isFinite));assert.ok(f.every(Number.isFinite));assert.ok(new Set(f).size>1);
  assert.match(linePath(h),/^M/);assert.doesNotMatch(linePath(h),/NaN|Infinity/);
  const html=read('../index.html');assert.match(html,/SIMULATED \/ NOT A TRAINED MODEL RESULT/);assert.match(html,/Persistence baseline/);assert.match(html,/MEASURED QUANTITY/);assert.match(html,/Relative pressure · simulated/);
});
test('Only local static resources; no React, operational API, database or live telemetry',()=>{
  for(const file of ['../main.js','../world.js','../story.js']){
    const js=read(file);assert.doesNotMatch(js,/from ['"]react|fetch\(|WebSocket\(|EventSource\(|indexedDB|localStorage/);
  }
  // Chapter 09 embeds the live edge dashboard via an iframe whose src is
  // set from JS (with `?edge=` override), so the static build carries no
  // hard-coded host. A static snapshot with the same edge field names is
  // the offline fallback, never a mock with invented tabs.
  assert.ok(!read('../index.html').includes('data-tab="'));
  for(const id of ['edge-frame','edge-fallback','edge-open','edge-retry','edge-status'])assert.ok(read('../index.html').includes(`id="${id}"`));
  for(const id of ['edge-frame','edge-fallback','edge-open','edge-retry','edge-status'])assert.ok(read('../present.html').includes(`id="${id}"`));
  const html=read('../dist/index.html');assert.doesNotMatch(html,/(?:src|href)="https?:/);assert.match(html,/\.\/assets\//);
});
test('Both pages carry one camera pose per chapter and the same chapter count',()=>{
  // A pose/chapter mismatch would silently stretch or compress the whole camera
  // timeline, which is the failure the pose list warns about in a comment.
  const world=read('../world.js');
  const block=world.slice(world.indexOf('const poses = ['),world.indexOf('// The poses array and the chapter list'));
  const poses=[...block.matchAll(/\{eye:/g)].length+[...block.matchAll(/homeShots\[|coastCamera\[/g)].length;
  assert.equal(poses,chapterCount);
  // The presenter build is a separate document and must stay in step with it.
  const present=read('../present.html');
  assert.equal([...present.matchAll(/data-chapter="\d{1,2}"/g)].length,chapterCount);
  for(const id of ['roadmap','funding'])assert.ok(present.includes(`id="${id}"`));
  for(const id of ['team-grid','beneficiary-grid','funding-body'])assert.ok(present.includes(`id="${id}"`));
});
test('The funding plan is internally consistent and never quoted as a firm price',()=>{
  // The headline figure must always equal the sum of the visible categories, so
  // the total can never drift away from the table above it.
  assert.equal(fundingRange(),'₱75,000 – ₱120,000');
  assert.equal(fundingRange(funding.filter(r=>r.kind!=='installed')),'₱19,000 – ₱28,000');
  const html=read('../index.html');
  assert.match(html,/Planning range only, not a supplier quotation/);
  assert.match(html,/subject to supplier quotations|replaced with current quotations/);
  // Every category has to carry one of the three filterable kinds.
  for(const row of funding)assert.ok(['installed','reusable','process'].includes(row.kind));
  for(const phase of phases)assert.match(phase.claim,/./);
});
test('All original geometry is shipped byte-identically; no pretend replacement buoy',()=>{
  const bytes=readFileSync(new URL('../../dashboard-next/public/models/PROJECT-FALCON-V2.glb',import.meta.url));
  assert.equal(createHash('sha256').update(bytes).digest('hex'),'d8674ce9415ce4b85b69ddddfd0a33609923146c191cabd915d5a6e8845d30ce');
  const folder=new URL('../dist/assets/',import.meta.url);const name=readdirSync(folder).find(f=>f.endsWith('.glb'));assert.ok(name);assert.deepEqual(readFileSync(new URL(name,folder)),bytes);
  const length=bytes.readUInt32LE(12),gltf=JSON.parse(bytes.subarray(20,20+length).toString('utf8'));
  assert.equal(gltf.nodes.length,622);assert.equal(gltf.meshes.length,251);
  for(const component of Object.values(components))assert.ok(gltf.nodes.some(n=>n.name?.toUpperCase().startsWith(component.prefix)),component.label);
});
test('Keyboard equivalents, readable fallback and reduced motion are present',()=>{
  const html=read('../index.html'),css=read('../style.css');
  assert.match(html,/Skip to story/);assert.match(html,/aria-label="Story chapters"/);assert.match(html,/id="sensor-menu"/);
  assert.match(css,/prefers-reduced-motion:reduce/);assert.match(css,/:focus-visible/);
  assert.match(read('../world.js'),/3D unavailable/);assert.match(read('../main.js'),/document.hidden/);
});
