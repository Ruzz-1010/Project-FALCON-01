import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,readdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {stripTypeScriptTypes} from 'node:module';
import {fileURLToPath} from 'node:url';
import {createServer} from 'vite';
import React from 'react';
import {renderToString} from 'react-dom/server';

const source=readFileSync(new URL('../thesis/content.ts',import.meta.url),'utf8');
const content=await import(`data:text/javascript;base64,${Buffer.from(stripTypeScriptTypes(source)).toString('base64')}`);
test('Internet failure does not disable local monitoring or AI',()=>{
 const s=content.scenarios.internet;assert.equal(s.internet,false);assert.equal(s.lora,true);assert.equal(s.ai,true);assert.equal(s.pressure,true);
});
test('Pressure failure withholds prediction and maintenance remains disarmed',()=>{
 assert.equal(content.scenarios.pressure.ai,false);assert.equal(content.scenarios.pressure.pressure,false);assert.equal(content.scenarios.maintenance.security,'DISARMED');assert.equal(content.scenarios.ai.pressure,true);
});
test('Thesis coverage and no fictional LoRa CAD placement',()=>{
 assert.equal(content.sensors.length,8);assert.equal(content.stages.length,16);assert.equal(content.validation.length,8);assert.equal(content.milestones.length,6);assert.equal(content.sensors.find(s=>s.id==='lora').prefix,'');
 assert.match(content.sensors.find(s=>s.id==='pressure').state,/candidate/);
});
test('Original CAD and shipped model are byte-identical',()=>{
 const original=readFileSync(new URL('../public/models/PROJECT-FALCON-V2.glb',import.meta.url));
 assert.equal(createHash('sha256').update(original).digest('hex'),'d8674ce9415ce4b85b69ddddfd0a33609923146c191cabd915d5a6e8845d30ce');
 const folder=new URL('../../thesis-dist/assets/',import.meta.url),name=readdirSync(folder).find(f=>f.endsWith('.glb'));assert.ok(name);assert.deepEqual(readFileSync(new URL(name,folder)),original);
});
test('Static entry uses bundled local assets and no external service',()=>{
 const html=readFileSync(new URL('../../thesis-dist/index.html',import.meta.url),'utf8');assert.doesNotMatch(html,/(?:src|href)="https?:/);assert.match(html,/\.\/assets\//);
 const code=readFileSync(new URL('../thesis/main.tsx',import.meta.url),'utf8');assert.doesNotMatch(code,/fetch\(|WebSocket\(/);
});
test('Presentation renders all key chapters and four-page preview',async()=>{
 const server=await createServer({configFile:fileURLToPath(new URL('../thesis.config.ts',import.meta.url)),server:{middlewareMode:true},appType:'custom'});
 try{
  const {App}=await server.ssrLoadModule('/main.tsx');
  const html=renderToString(React.createElement(App));
  for(const id of ['explore','architecture','pressure','ai','dashboard','power','resilience','validation','limitations','roadmap','demonstration'])assert.ok(html.includes(`id="${id}"`),id);
  assert.match(html,/SIMULATED DATA/);assert.match(html,/Logs &amp; Alerts/);assert.match(html,/CALIBRATION REQUIRED/);
  await server.ssrLoadModule('/BuoyModel.tsx');
 }finally{await server.close()}
});
