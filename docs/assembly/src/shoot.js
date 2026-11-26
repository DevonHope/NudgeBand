// usage: node shoot.js scenes.json outdir
const {chromium}=require('playwright'); const fs=require('fs'); const http=require('http'); const path=require('path');
const root=process.argv[4]||'/';
const srv=http.createServer((q,s)=>{let p=decodeURIComponent(q.url.split('?')[0]); let f=p.startsWith('/fs/')?p.slice(3):path.join(__dirname,p);
 fs.readFile(f,(e,d)=>{if(e){s.writeHead(404);s.end();return} s.writeHead(200,{'Content-Type':f.endsWith('.js')?'text/javascript':f.endsWith('.html')?'text/html':'application/octet-stream'}); s.end(d)})}).listen(8765);
(async()=>{
 const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const pg=await b.newPage(); pg.on('console',m=>console.log('console:',m.text())); pg.on('pageerror',e=>console.log('ERR',e.message));
 await pg.goto('http://localhost:8765/render.html'); await pg.waitForFunction(()=>window.ready);
 const scenes=JSON.parse(fs.readFileSync(process.argv[2])); const out=process.argv[3]; fs.mkdirSync(out,{recursive:true});
 const anchors={};
 for(const [name,spec] of Object.entries(scenes)){
   const r=await pg.evaluate(s=>window.renderScene(s),spec);
   fs.writeFileSync(path.join(out,name+'.png'),Buffer.from(r.png.split(',')[1],'base64')); anchors[name]=r.anchors; console.log('rendered',name);
 }
 fs.writeFileSync(path.join(out,'anchors.json'),JSON.stringify(anchors,null,1));
 await b.close(); srv.close();
})();
