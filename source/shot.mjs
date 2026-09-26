// Screenshot an HTML mockup page to JPG: node shot.mjs <page.html> <out.jpg> <width> <height>
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';

const [html, out, w, h] = process.argv.slice(2);
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: +w, height: +h } });
await page.goto('file://' + html);
await page.evaluate(() => document.fonts.ready);
await page.waitForLoadState('networkidle');
await page.screenshot({ path: out, type: 'jpeg', quality: 92, clip: { x: 0, y: 0, width: +w, height: +h } });
await browser.close();
