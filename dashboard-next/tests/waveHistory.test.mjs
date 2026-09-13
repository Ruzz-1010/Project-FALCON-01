import {readFileSync} from 'node:fs';
import assert from 'node:assert/strict';
import test from 'node:test';
import {stripTypeScriptTypes} from 'node:module';

const source=readFileSync(new URL('../src/waveHistory.ts',import.meta.url),'utf8');
const js=stripTypeScriptTypes(source);
const {recentWaveSession,timedLinePath}=await import(`data:text/javascript;base64,${Buffer.from(js).toString('base64')}`);
const row=(time,value=.5)=>({recordedAt:new Date(time).toISOString(),waveHeight:value});

test('hours-apart sessions do not compress the current trace',()=>{
  const rows=[row(0),row(2000),row(13*3600000),row(13*3600000+2000)];
  assert.deepEqual(recentWaveSession(rows),rows.slice(2));
  assert.equal(rows.length,4);
});
test('sorts timestamps, removes duplicates and rejects invalid samples',()=>{
  assert.deepEqual(recentWaveSession([row(2000),row(0),row(0,.6),row(3000,NaN),{recordedAt:'invalid',waveHeight:.4}]),[row(0,.6),row(2000)]);
});
test('single reading and empty restart are safe',()=>{
  assert.deepEqual(recentWaveSession([]),[]);
  assert.deepEqual(recentWaveSession([row(0),row(60000)]),[row(60000)]);
});
test('AI paths break at missing intervals rather than drawing diagonals',()=>{
  assert.equal(timedLinePath([[0,1],[1,2],[9,3],[10,4]],[0,2000,60000,62000]),'M 0 1 L 1 2 M 9 3 L 10 4');
});
