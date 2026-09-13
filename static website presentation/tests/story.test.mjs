import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,readdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {chapters,components,createLink,setLink,tickLink,waveSamples,forecastSamples,linePath} from '../story.js';
const read=path=>readFileSync(new URL(path,import.meta.url),'utf8');

test('Every required chapter exists exactly once in the new static story',()=>{
  const html=read('../index.html');
  assert.equal(chapters.length,10);
  assert.equal([...html.matchAll(/data-chapter="\d"/g)].length,10);
  for(let i=0;i<10;i++)assert.equal(html.split(`data-chapter="${i}"`).length,2);
  for(const id of ['ocean','buoy','sensors','controller','radio','shore','waves','prediction','dashboard','connected'])assert.ok(html.includes(`id="${id}"`));
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
  const html=read('../index.html');assert.match(html,/SIMULATED \/ NOT A TRAINED MODEL RESULT/);assert.match(html,/Persistence baseline/);assert.match(html,/MEASURED QUANTITY \/ SIMULATED PRESSURE/);
});
test('Only local static resources; no React, operational API, database or live telemetry',()=>{
  for(const file of ['../main.js','../world.js','../story.js']){
    const js=read(file);assert.doesNotMatch(js,/from ['"]react|fetch\(|WebSocket\(|EventSource\(|indexedDB|localStorage/);
  }
  assert.equal([...read('../index.html').matchAll(/data-tab="/g)].length,4);
  const html=read('../dist/index.html');assert.doesNotMatch(html,/(?:src|href)="https?:/);assert.match(html,/\.\/assets\//);
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
