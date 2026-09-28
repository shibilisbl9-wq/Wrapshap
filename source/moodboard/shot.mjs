// Usage: node shot.mjs <page.html> <out.png> <width> <height> [scale] [transparent]
// Pages are served over a local http server: CSS masks refuse file:// images.
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import http from 'http';
import fs from 'fs';
import path from 'path';

const [,, html, out, w, h, scale = '1', transparent = ''] = process.argv;
const root = path.resolve(path.dirname(html), '..', '..');   // repo root, so ../../fonts resolves
const types = { '.html': 'text/html', '.svg': 'image/svg+xml', '.png': 'image/png', '.webp': 'image/webp',
  '.ttf': 'font/ttf', '.json': 'application/json', '.jpg': 'image/jpeg' };
const server = http.createServer((req, res) => {
  const p = path.join(root, decodeURIComponent(new URL(req.url, 'http://x').pathname));
  if (!p.startsWith(root) || !fs.existsSync(p)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': types[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
});
await new Promise(r => server.listen(0, '127.0.0.1', r));
const url = `http://127.0.0.1:${server.address().port}/` + path.relative(root, path.resolve(html));

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: Math.ceil(+w), height: Math.ceil(+h) }, deviceScaleFactor: +scale });
await page.goto(url, { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(300);
await page.screenshot({ path: out, omitBackground: !!transparent, clip: { x: 0, y: 0, width: +w, height: +h } });
await browser.close();
server.close();
