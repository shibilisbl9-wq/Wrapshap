// Prints every page in jobs.json to a vector PDF and records logo-slot positions.
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import fs from 'fs';
import path from 'path';

const here = path.dirname(new URL(import.meta.url).pathname);
const JOBS = process.env.JOBS || 'jobs.json', SLOTS = process.env.SLOTS || 'slots.json';
const jobs = JSON.parse(fs.readFileSync(path.join(here, JOBS), 'utf8'));
const only = process.argv.slice(2);
fs.mkdirSync(path.join(here, 'raw'), { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage();
const slots = fs.existsSync(path.join(here, SLOTS))
  ? JSON.parse(fs.readFileSync(path.join(here, SLOTS), 'utf8')) : {};
for (const j of jobs) {
  if (only.length && !only.includes(j.name)) continue;
  await page.goto('file://' + j.html);
  await page.evaluate(() => document.fonts.ready);
  await page.emulateMedia({ media: 'print' });
  slots[j.name] = await page.$$eval('.logo-slot', els => els.map(e => {
    const r = e.getBoundingClientRect();
    return { id: e.id, x: r.x, y: r.y, w: r.width, h: r.height };
  }));
  await page.pdf({
    path: path.join(here, 'raw', j.name + '.pdf'),
    width: j.w + 'mm', height: j.h + 'mm', printBackground: true, preferCSSPageSize: true,
  });
  console.log('printed', j.name);
}
fs.writeFileSync(path.join(here, SLOTS), JSON.stringify(slots, null, 1));
await browser.close();
