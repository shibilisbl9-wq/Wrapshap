const {chromium}=require('playwright');const path=require('path');
(async()=>{const b=await chromium.launch();
for(const m of['black','white']){const f=path.resolve(__dirname,`wrapshap-sticker-${m}.svg`);
const pg=await b.newPage({viewport:{width:496,height:898},deviceScaleFactor:6});
await pg.goto('file://'+f);await pg.waitForTimeout(600);
await pg.screenshot({path:f.replace('.svg','.png')});
await pg.pdf({path:f.replace('.svg','.pdf'),width:'496px',height:'898px',printBackground:true});}
await b.close();})();
