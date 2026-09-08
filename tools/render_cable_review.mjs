// Render actual offline WebGL output; no photographic or synthetic robot imagery.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {resolve,join} from 'node:path';
import {pathToFileURL} from 'node:url';
const dir=resolve(process.argv[2]),cad=resolve(process.argv[3]);
const {launch,sleep,collectErrors}=await import(pathToFileURL(join(cad,'web/_cdp.mjs')).href);
const b=await launch({url:'about:blank',port:9494,windowSize:'1500,1050',args:['--headless=new']});
const evidence={source:JSON.parse(readFileSync(join(dir,'PROVENANCE.json'),'utf8')),scope:'Offline Chrome on macOS; no claim of native Windows execution',checks:[],images:[],errors:collectErrors(b)};
try{
 await b.send('Page.enable');await b.send('Runtime.enable');await b.send('Network.enable');
 await b.send('Network.emulateNetworkConditions',{offline:true,latency:0,downloadThroughput:0,uploadThroughput:0});
 const document=process.argv.includes('--document');
 for(const name of document?['START HERE']:['Whole robot and cables','Inside and cables','Head connections','Leg connections','Cable routes only']){
  await b.send('Page.navigate',{url:pathToFileURL(join(dir,name+'.html')).href});
  let ready=false;for(let n=0;n<200;n++){ready=await b.evaluate(document?'document.images.length===5&&Array.from(document.images).every(i=>i.complete&&i.naturalWidth>100)':'!!window.__review');if(ready)break;await sleep(100)}assert.ok(ready,name+' draws offline');
  if(!document){assert.ok(await b.evaluate('__review.triangles>0&&__review.visible===__review.total'));const counts=await b.evaluate('window.__review');evidence.checks.push({view:name,...counts});}
  const rect=document?null:await b.evaluate('(()=>{let r=document.querySelector("canvas").getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,scale:1}})()');
  const shot=await b.send('Page.captureScreenshot',{format:'png',...(rect?{clip:rect}:{})});writeFileSync(join(dir,name+'.png'),Buffer.from(shot.data,'base64'));evidence.images.push(name+'.png');
  if(document){const pdf=await b.send('Page.printToPDF',{printBackground:true,paperWidth:8.27,paperHeight:11.69});writeFileSync(join(dir,'Cables and connections.pdf'),Buffer.from(pdf.data,'base64'));evidence.checks.push('All 5 embedded images render with browser offline; PDF exported');}
 }
 assert.deepEqual(evidence.errors,[]);
}finally{writeFileSync(join(dir,process.argv.includes('--document')?'DOCUMENT CHECK.json':'RENDER CHECK.json'),JSON.stringify(evidence,null,2));await b.close()}
