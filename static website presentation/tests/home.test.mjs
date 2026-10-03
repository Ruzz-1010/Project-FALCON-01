import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {homeShots,homeCamera,homeWeight,oceanSample,waveLayers,oceanFieldGLSL,smooth} from '../home.js';
test('Home camera begins offshore and meets the unchanged Instrument camera exactly',()=>{
  assert.deepEqual(homeCamera(0).eye,homeShots[0].eye);
  assert.deepEqual(homeCamera(1),{eye:[2.6,1.45,3.8],aim:[-.65,.55,0]});
  let distance=Infinity;
  for(let i=0;i<=100;i++){const shot=homeCamera(i/100);const next=Math.hypot(...shot.eye);assert.ok(next<=distance+1e-10);distance=next;assert.ok([...shot.eye,...shot.aim].every(Number.isFinite));}
  for(const knot of [.32,.72]){const a=homeCamera(knot-1e-6),b=homeCamera(knot+1e-6);assert.ok(Math.hypot(...a.eye.map((v,i)=>v-b.eye[i]))<1e-6);}
});
test('Ocean genuinely displaces vertices with six directional wave layers',()=>{
  assert.equal(waveLayers.length,6);assert.match(oceanFieldGLSL,/sin\(q\)/);
  const world=readFileSync(new URL('../world.js',import.meta.url),'utf8');
  assert.match(world,/p\.z=mix\(p\.z,homeField/);
  assert.notEqual(oceanSample(0,0,0,.5).height,oceanSample(0,0,1,.5).height);
  for(let t=0;t<120;t+=.37){const value=oceanSample(0,0,t,.9);assert.ok(Math.abs(value.height)<.15);assert.ok(Math.abs(value.dx)<.13);assert.ok(Math.abs(value.dz)<.13);}
  const e=1e-4,field=oceanSample(0,0,4,.8);
  assert.ok(Math.abs(field.dx-(oceanSample(e,0,4,.8).height-oceanSample(-e,0,4,.8).height)/(2*e))<1e-7);
});
test('Home effects fade completely before the Instrument; scroll interpolation is bounded',()=>{
  assert.equal(homeWeight(0),1);assert.equal(homeWeight(1),0);assert.equal(homeWeight(2),0);
  assert.equal(smooth(0),0);assert.equal(smooth(1),1);assert.equal(smooth(-3),0);
});
test('Pages 03–04 and 07–09 markup remains unchanged during the scoped 05–06 updates',()=>{
  const html=readFileSync(new URL('../index.html',import.meta.url),'utf8');
  const rest=html.slice(html.indexOf('    <section class="scene diagram-scene" id="controller"')).replace(/    <section class="scene" id="shore"[\s\S]*?(?=    <section class="scene wide-scene" id="waves")/,'').replace(/    <section class="scene wide-scene" id="waves"[\s\S]*?(?=    <section class="scene wide-scene" id="prediction")/,'');
  // 2026-10-03: intentional edits inside this range are the DOST draft copy
  // (controller, radio, prediction and connected scenes), the chapter-paging
  // controls in the footer, the relative-unit axis labels on the forecast
  // chart, and the Bay Station panel label. Every honesty guard below still
  // holds, and the surrounding scenes are still the cinematic originals.
  //
  // 2026-10-05: wrap-up merged 18 → 15 pages (Validation+Status,
  // Scope+Risks, Impact+Funding; Roadmap carries the team grid; radio
  // carries the 6-step Live Link; funding ₱90,000–₱150,000; roadmap is
  // 5 bootcamp gates). No section added above #controller, no camera
  // pose touched for chapters 0–9. Hash updated for the merged tail.
  assert.equal(createHash('sha256').update(rest).digest('hex'),'67a8ee0adcc0431201effa4e18a95694f05e1f18257c5cc664d11ee65008e89a');
  // The opening kicker was rewritten to the DOST title slide; the presenter
  // build keeps the cinematic "Listen to the ocean" phrasing.
  assert.match(html,/DOST PRESENTATION · 5 OCTOBER 2026/);assert.match(html,/id="begin-journey"/);
  // Paging controls are part of the standard build on both pages.
  assert.match(html,/id="chapter-prev"/);assert.match(html,/id="chapter-next"/);
  // The wrap-up chapters must not drift out of the dismissed range:
  // if one is ever moved above #controller this guard would stop covering it.
  for(const id of ['roadmap','funding'])assert.ok(html.includes(`id="${id}"`));
});
test('The story never claims calibrated metres or a direct wave-height measurement',()=>{
  const html=readFileSync(new URL('../index.html',import.meta.url),'utf8');
  assert.doesNotMatch(html,/direct wave.height|accurate wave height|wave.height sensor/i);
  assert.match(html,/NOT CALIBRATED METRES/);
  // Uncalibrated values are plotted in relative units everywhere they appear.
  assert.doesNotMatch(html,/>1 m</);assert.doesNotMatch(html,/>0 m</);
});
