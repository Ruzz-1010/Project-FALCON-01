import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {pressureSequence,morphSignal,morphStep,stageFromScroll,deviation} from '../wave-estimation.js';
test('Raw, cleaned and derived sequences share one sample window and morph continuously',()=>{
  const samples=pressureSequence(3);for(const key of ['raw','clean','hs']){assert.equal(samples[key].length,160);assert.ok(samples[key].every(Number.isFinite));}
  assert.deepEqual(morphSignal(samples,0),samples.raw);
  assert.ok(morphSignal(samples,1).every((v,i)=>Math.abs(v-samples.clean[i])<1e-12));
  assert.ok(Math.abs(samples.result-4*deviation(samples.clean))<1e-12);
  const roughness=a=>a.slice(1).reduce((sum,v,i)=>sum+Math.abs(v-a[i]),0);
  assert.ok(roughness(samples.clean)<roughness(samples.raw),'Filtering reduces sample-to-sample noise');
  for(const boundary of [0,1,2]){const a=morphSignal(samples,boundary-1e-6),b=morphSignal(samples,boundary+1e-6);assert.ok(a.every((v,i)=>Math.abs(v-b[i])<1e-4));}
});
test('Scroll, reverse-click and stop/resume transitions are bounded and frame-rate independent',()=>{
  assert.equal(stageFromScroll(0),0);assert.equal(stageFromScroll(.6),2);assert.equal(stageFromScroll(1),2);
  let stage=0;for(let i=0;i<300;i++){const target=i<100?2:i<200?0:2;const next=morphStep(stage,target,1/30);assert.ok(next>=0&&next<=2);assert.ok(Math.abs(next-stage)<.31);stage=next;}
  const advance=fps=>{let s=0;for(let i=0;i<fps;i++)s=morphStep(s,2,1/fps);return s;};assert.ok(Math.abs(advance(30)-advance(60))<1e-10);
  assert.equal(morphStep(1,2,0),1);
});
test('Page 06 labels simulated pressure separately from derived, uncalibrated Hs',()=>{
  const html=readFileSync(new URL('../index.html',import.meta.url),'utf8');const section=html.slice(html.indexOf('id="waves"'),html.indexOf('id="prediction"'));
  assert.match(section,/MEASURED QUANTITY/);assert.match(section,/NOT CALIBRATED METRES/);assert.match(section,/CALIBRATION REQUIRED/);
  assert.doesNotMatch(section,/wave.height sensor|direct wave.height measurement|accurate wave height/i);
  assert.equal((section.match(/data-process=/g)||[]).length,3);
});
