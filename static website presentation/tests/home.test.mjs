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
  //
  // 2026-10-06: presentation date moved from 5 to 6 October in the opening
  // kicker, the Fullbright College disclosure and the acknowledgement. Both
  // fall inside `rest` (the acknowledgement closes the tail), so the hash
  // moved with them. No structural change: still 15 scenes, same ids, same
  // order, and the honesty guards below are untouched.
  //
  // 2026-10-07: Chapter 08 AI prediction now carries a 4-step
  // "How our system predicts" explainer (GATHER → READ TREND → PROJECT →
  // PROVE IT) above the chart, so the panel reads the process instead of
  // only the display. Chart, honesty labels and evaluation wording untouched.
  //
  // 2026-10-07 (2): explainer grounded in edge/falcon_edge/forecast.py —
  // last-120 SQLite waveLevel records, damped linear trend, change cap +
  // 0–15 m clamp, 35–94% confidence, CALM/MODERATE/ROUGH thresholds,
  // wave-short-term v1.0.0-demo vs persistence with MAE/RMSE/bias.
  //
  // 2026-10-08 (3): 09 now embeds the live edge dashboard (iframe src set
  // from JS with ?edge= override) with a static edge snapshot as the
  // offline fallback — no more mock tabs.
  //
  // 2026-10-09 (4): content polish for the 6 Oct DOST proposal — ch02
  // buoy copy turned into a scannable shore/buoy split, ch09 presenter
  // plumbing (edge service instructions) replaced with panel-facing
  // "BUILT AND RUNNING ALREADY" disclosure, ch10 Implemented list leads
  // with the live edge service, ch14 closes in plain language (no
  // internal doc reference).
  //
  // 2026-10-09 (5): ch08 explainer rewritten in plain English for the
  // panel — the 4-step Taglish predict-steps cards ("SAAN GALING /
  // PAANO KINOCOMPUTE / SAFETY LIMITS / ANO BASEHAN") and the second
  // "BAKIT" evaluation grid are replaced by one readable 4-step flow
  // (data source → trend → safety caps → judged vs "no change"
  // baseline). Same method, same honesty labels; jargon like raw
  // SQL/field names and version strings removed from the stage.
  // 2026-10-09 (8): finale page stripped to pure animation (copy removed
  // per presenter; aria-label kept). Chapters 0–14 untouched.
  assert.equal(createHash('sha256').update(rest).digest('hex'),'16de13d84afc9003610820d3144fcc52b82cb879e34e785b3f52e7484eecbe2d');
  // The opening kicker was rewritten to the DOST title slide; the presenter
  // build keeps the cinematic "Listen to the ocean" phrasing.
  assert.match(html,/DOST PRESENTATION · 6 OCTOBER 2026/);assert.match(html,/id="begin-journey"/);
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
