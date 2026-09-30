import test from 'node:test';
import assert from 'node:assert/strict';
import {signals,signalTrace} from '../acquisition.js';
import {instrumentPrefixes} from '../instrument.js';
import {readFileSync} from 'node:fs';
test('Acquisition has an honest source → signal → record explanation for all five physical targets',()=>{
  assert.deepEqual(Object.keys(signals),Object.keys(instrumentPrefixes));
  for(const s of Object.values(signals)){
    assert.match(s.raw,/illustrative/);assert.ok(s.record.length<65);assert.ok(s.result.length<75);
    for(const t of [0,.5,20,3600]){const path=signalTrace(s.kind,t);assert.equal(path.match(/[ML]/g).length,100);assert.doesNotMatch(path,/NaN|Infinity/);}
  }
  assert.match(signals.pressure.result,/On shore.*pressure-derived estimated wave height/);
  assert.notEqual(signalTrace('wave',0),signalTrace('wave',1));
  assert.notEqual(signalTrace('streams',0,0),signalTrace('streams',0,1));
});
test('Acquisition connection uses projected CAD geometry, not a hand-positioned floating source',()=>{
  const world=readFileSync(new URL('../world.js',import.meta.url),'utf8');
  assert.match(world,/projection.copy\(halo.position\).project\(camera\)/);
  assert.match(world,/querySelector\('#acquisition-signal'\).getBoundingClientRect\(\)/);
  const main=readFileSync(new URL('../main.js',import.meta.url),'utf8');
  assert.match(main,/if\(active===2&&moving\)acquisition.draw/);
  assert.match(main,/if\(inspecting&&state.chapter!==active\)endInspection/);
});
