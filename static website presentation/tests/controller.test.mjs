import test from 'node:test';
import assert from 'node:assert/strict';
import {controllerInputs,controllerStep} from '../controller.js';
import {intersects,placeCallout} from '../composition.js';
test('Each controller input travels, timestamps, validates, packages and then exits to LoRa',()=>{
  for(let i=0;i<4;i++){
    const stages=[0,.45,.65,.8,.95].map(p=>controllerStep(i*4.8+p*4.8));
    assert.deepEqual(stages.map(s=>s.stage),['ACQUIRE','TIMESTAMP','VALIDATE','PACKAGE','TO LoRa']);
    stages.forEach(s=>{assert.equal(s.input,i);assert.equal(s.sequence,i+1);});
  }
  assert.equal(controllerInputs.length,4);assert.equal(controllerStep(19.2).input,0);
});
test('Callouts avoid geometry, text, adjacent labels and viewport edges',()=>{
  for(const width of [390,768,1440]){
    const silhouette={left:width*.4,right:width*.6,top:180,bottom:550};
    const viewport={left:20,right:width-20,top:115,bottom:650};
    const source={x:width*.5,y:300},occupied=[];
    const first=placeCallout(source,silhouette,occupied,viewport);assert.ok(first);
    assert.equal(intersects(first.rect,silhouette),false);occupied.push(first.rect);
    const second=placeCallout(source,silhouette,occupied,viewport);assert.ok(second);assert.equal(intersects(first.rect,second.rect,12),false);
    occupied.push(second.rect);assert.equal(placeCallout(source,silhouette,occupied,viewport),null);
    assert.equal(placeCallout({...source,y:90},silhouette,[],viewport),null);
  }
});
