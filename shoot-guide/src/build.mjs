import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
import { C, esc, frame, phone, person, sparkle, crown, smiley, sticker, note, floorPlan, aspectSize } from './lib.mjs';
import { SCRIPTS, RUNSHEET } from './scripts.mjs';
import { POSTS } from './posts.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');
const out = path.join(root, 'build');
fs.mkdirSync(out, { recursive: true });

const totalFrames = SCRIPTS.reduce((n, s) => n + s.beats.length, 0) + POSTS.reduce((n, p) => n + p.frames.length, 0);

const CSS = `
@font-face{font-family:'DM Sans';src:url('../fonts/DMSans.ttf');font-weight:100 1000}
@font-face{font-family:'Anton';src:url('../fonts/Anton.ttf')}
@font-face{font-family:'Permanent Marker';src:url('../fonts/PermanentMarker.ttf')}
@font-face{font-family:'DM Mono';src:url('../fonts/DMMono-Regular.ttf')}
@page{size:1440px 810px;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:#fff}
body{font-family:'DM Sans',sans-serif;color:${C.ink};-webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{width:1440px;height:810px;position:relative;overflow:hidden;background:${C.paper};page-break-after:always;break-after:page}
.mono{font-family:'DM Mono',monospace}
.mk{font-family:'Permanent Marker',cursive}
.an{font-family:'Anton',sans-serif;letter-spacing:.02em}
.kick{font-size:12px;letter-spacing:.2em;font-weight:700;color:${C.grey};text-transform:uppercase}
.chip{display:inline-block;border:1.8px solid ${C.ink};border-radius:99px;padding:3px 11px;font-size:11.5px;font-weight:700;background:#fff;white-space:nowrap}
.chip.y{background:${C.Y}}.chip.k{background:${C.ink};color:${C.Y}}
.card{background:${C.card};border:2.5px solid ${C.ink};border-radius:16px;box-shadow:5px 6px 0 ${C.ink}}
.lab{display:inline-block;background:${C.Y};font-weight:800;font-size:10.5px;letter-spacing:.16em;padding:2.5px 8px;border-radius:3px;text-transform:uppercase}
.pgno{position:absolute;right:30px;bottom:14px;font-family:'DM Mono';font-size:10px;color:${C.grey}}
.foot{position:absolute;left:48px;bottom:14px;font-size:10.5px;color:${C.grey}}
.badge{display:flex;align-items:center;justify-content:center;background:${C.ink};color:${C.Y};font-family:'Anton';border-radius:14px;transform:rotate(-4deg)}
.dash{border:2px dashed ${C.ink};border-radius:10px;padding:8px 12px;font-size:11.5px;line-height:1.38;background:#fff}
.blk{background:${C.ink};color:${C.Y};border-radius:12px;padding:10px 14px}
.blk .lab{color:${C.ink}}
.frame{display:block;width:100%;height:auto}
.plan{display:block;width:100%;height:auto}
.cap{font-size:10.5px;line-height:1.32}
.cap .t{display:inline-block;font-family:'DM Mono';font-weight:500;font-size:10.5px;background:${C.Y};border:1.6px solid ${C.ink};border-radius:5px;padding:1px 6px;margin-bottom:4px}
.cap b{font-weight:800}
.cap .say{font-style:italic;color:#333}
.cap .txt{font-family:'Permanent Marker';font-size:10.5px;background:linear-gradient(transparent 55%, ${C.Y2} 55%);display:inline}
.rail{display:flex;height:22px;border:2px solid ${C.ink};border-radius:6px;overflow:hidden;background:#fff}
.rail div{display:flex;align-items:center;justify-content:center;font-family:'DM Mono';font-size:10px;border-right:1.6px solid ${C.ink};white-space:nowrap}
.rail div:last-child{border-right:0}
ul.tick{list-style:none}ul.tick li{position:relative;padding-left:16px;margin-bottom:4px;font-size:11.5px;line-height:1.35}
.big ul.tick li{font-size:13.5px;margin-bottom:9px;line-height:1.4}
.big ul.tick li:before{top:6px}
ul.tick li:before{content:'';position:absolute;left:0;top:4px;width:8px;height:8px;background:${C.Y};border:1.6px solid ${C.ink};border-radius:2px;transform:rotate(45deg)}
.reg{position:absolute;width:22px;height:22px}
`;

const reg = (x, y) => `<svg class="reg" style="left:${x}px;top:${y}px" viewBox="-11 -11 22 22"><circle r="7" fill="none" stroke="${C.ink}" stroke-width="1.6"/><line x1="-11" y1="0" x2="11" y2="0" stroke="${C.ink}" stroke-width="1.6"/><line x1="0" y1="-11" x2="0" y2="11" stroke="${C.ink}" stroke-width="1.6"/></svg>`;
const logoImg = (h) => `<img src="../assets/wrapshap-logo-sparkle.png" style="height:${h}px;display:block">`;
const inl = (svg) => svg;

let pageNo = 0;
const pages = [];
const addPage = (html, opts = {}) => { pageNo += 1; pages.push(`<section class="page" ${opts.style ? `style="${opts.style}"` : ''}>${html}<div class="pgno">${String(pageNo).padStart(2, '0')}</div></section>`); };

// ---------------- 1. COVER ----------------
{
  const ghost = (t, x, y, size, rot) => `<div class="an" style="position:absolute;left:${x}px;top:${y}px;font-size:${size}px;line-height:.9;transform:rotate(${rot}deg);transform-origin:left top;white-space:nowrap">
    <span style="position:absolute;left:9px;top:9px;color:${C.amber};opacity:.9">${t}</span><span style="position:relative;color:${C.ink}">${t}</span></div>`;
  addPage(`
    <div style="position:absolute;inset:0;background:${C.Y}"></div>
    ${[[24, 24], [1394, 24], [24, 764], [1394, 764]].map(([x, y]) => reg(x, y)).join('')}
    <div style="position:absolute;left:0;right:0;top:0;height:10px;background:${C.ink}"></div>
    <div class="kick" style="position:absolute;left:72px;top:64px;color:${C.ink}">WRAPSHAP · PAKISTAN · FIRST KIOSK · ORGANIC SOCIAL</div>
    ${ghost('SHOOT', 68, 106, 260, -3)}
    ${ghost('GUIDE', 68, 340, 260, -3)}
    <div style="position:absolute;right:76px;top:96px;background:#fff;border:3px solid ${C.ink};border-radius:22px;padding:18px 24px;transform:rotate(4deg);box-shadow:7px 8px 0 ${C.ink}">${logoImg(104)}</div>
    <svg style="position:absolute;right:292px;top:300px" width="112" height="90" viewBox="-2 -2 32 26">${crown(0, 0, 1)}</svg>
    <svg style="position:absolute;right:160px;top:330px" width="80" height="80" viewBox="-12 -12 24 24">${smiley(0, 0, 10, C.ink, '#fff')}</svg>
    <div style="position:absolute;left:72px;top:624px;width:760px">
      <div style="font-size:30px;font-weight:800;line-height:1.1">Frames, timings and set-ups for the Day-1 factory shoot and every launch post.</div>
      <div style="display:flex;gap:10px;margin-top:20px;flex-wrap:wrap">
        <span class="chip k">${SCRIPTS.length} FACTORY SCRIPTS</span><span class="chip k">${POSTS.length} LAUNCH POSTS</span><span class="chip k">${totalFrames} DRAWN FRAMES</span><span class="chip">9:16 · 4:5</span>
      </div>
    </div>
    <div style="position:absolute;right:76px;bottom:62px;width:430px;font-size:12px;line-height:1.45;background:rgba(255,255,255,.65);border:2px dashed ${C.ink};border-radius:10px;padding:10px 14px">
      <b>Read this first.</b> Frames are drawn composition guides, not final looks. Timings for S1–S8 and S10 and every on-screen line come from the launch plan; shot sizes, camera moves and the schedule are suggestions. Post beats marked <b>PROPOSED</b> are new.
    </div>
    <svg style="position:absolute;left:72px;bottom:30px" width="760" height="14" viewBox="0 0 760 14">${Array.from({ length: 77 }, (_, i) => `<line x1="${i * 10}" y1="${i % 5 === 0 ? 0 : 6}" x2="${i * 10}" y2="14" stroke="${C.ink}" stroke-width="1.4"/>`).join('')}</svg>
  `);
}

// ---------------- 2. RUN SHEET ----------------
{
  const mins = [['09:00', 'Call. Kit check, consent forms, light the machine area.'], ['09:30', 'Machine block: S1, S2, S3, S9, S10 (about 4.5 h)'], ['14:00', 'Lunch and reset to the table.'], ['14:30', 'Table block: S4, S5, S6, S7'], ['16:50', 'Window block: S8 (needs daylight)'], ['17:30', 'Wrap. Back up cards twice. Log every real timer.']];
  const slot = { S1: '09:30', S2: '10:30', S3: '11:15', S9: '12:15', S10: '13:15', S4: '14:30', S5: '15:00', S6: '15:40', S7: '16:10', S8: '16:50' };
  addPage(`
    <div style="position:absolute;left:48px;top:34px"><div class="kick">FACTORY SHOOT · DAY 1 · RUN SHEET</div><div style="font-size:40px;font-weight:800;letter-spacing:-.01em;margin-top:2px">Ten scripts, one factory, one day</div></div>
    <div style="position:absolute;right:48px;top:44px;display:flex;gap:8px"><span class="chip y">ORDER FROM THE PLAN</span><span class="chip">TIMES ARE PROPOSED</span></div>
    ${RUNSHEET.map((b, i) => `
      <div class="card" style="position:absolute;left:${48 + i * 330}px;top:122px;width:314px;height:392px;padding:16px 16px;background:${i === 0 ? C.Y : i === 1 ? '#fff' : C.card}">
        <div class="an" style="font-size:22px;letter-spacing:.06em">${b.blk}</div>
        <div style="font-size:11.5px;margin:2px 0 10px;color:#333">${b.note}</div>
        ${b.items.map(([id, t, s]) => `<div style="display:flex;align-items:center;gap:10px;background:#fff;border:2px solid ${C.ink};border-radius:10px;padding:7px 9px;margin-bottom:7px"><div class="badge" style="width:42px;height:32px;font-size:17px;flex:none">${id}</div><div style="flex:1;font-size:12.5px;font-weight:700;line-height:1.15">${t}</div><div class="mono" style="font-size:10.5px;text-align:right;line-height:1.3">${s}s<br><span style="color:${C.grey}">${slot[id]}</span></div></div>`).join('')}
      </div>`).join('')}
    <div class="card" style="position:absolute;left:1038px;top:122px;width:354px;height:392px;padding:16px">
      <div class="lab">PROPOSED DAY</div>
      <div style="margin-top:10px">${mins.map(([t, d]) => `<div style="display:flex;gap:10px;padding:6px 0;border-bottom:1.5px solid ${C.line}"><div class="mono" style="font-weight:500;font-size:12.5px;width:46px;flex:none">${t}</div><div style="font-size:12px;line-height:1.3">${d}</div></div>`).join('')}</div>
      <div class="dash" style="margin-top:12px;font-size:10.5px"><b>Check first:</b> the plan puts S8 last. If the window loses light before then, swap it earlier. Sunset in early October is close to 18:00.</div>
    </div>
    <div class="card" style="position:absolute;left:48px;top:540px;width:640px;height:190px;padding:14px 16px">
      <div class="lab">KIT LIST</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:0 24px;margin-top:8px">
        <ul class="tick"><li><b>From the plan:</b> 1–2 dummy phones</li><li>CLEAR, PRIVACY, MATTE and TUFF films</li><li>Kiosk cutter, dust wipes, microfiber cloth</li><li>A glossy dummy (S6), a window (S8)</li><li>Real stopwatch for every cut</li></ul>
        <ul class="tick"><li><b>Suggested:</b> 2 tripods, 1 gimbal, clip-on macro lens</li><li>2 lav mics or one phone mic on a boom</li><li>Tape to mark 35° and the phone position</li><li>Spare film sheets and a spare dummy</li><li>Consent forms and a pen on a clipboard</li></ul>
      </div>
    </div>
    <div class="card" style="position:absolute;left:712px;top:540px;width:680px;height:190px;padding:14px 16px">
      <div class="lab">CREW (SUGGESTED)</div>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px 14px;margin-top:10px;font-size:11.5px;line-height:1.35">
        ${[['Director / DOP', 'Owns the frames in this guide and the 9:16 crop.'], ['Camera B / macro', 'Inserts, slow-mo, the kiosk screen.'], ['Sound', 'Room tone, ASMR (S5), voiceovers (S2, S10).'], ['Continuity', 'Timer log, film used, which half is CLEAR (S4).'], ['Talent wrangler', 'Casting, wardrobe, consent forms.'], ['Runner', 'Reset props between takes, snacks, chai.']].map(([t, d]) => `<div style="border:2px solid ${C.ink};border-radius:10px;padding:8px 10px;background:#fff"><b>${t}</b><br>${d}</div>`).join('')}
      </div>
    </div>
    <div class="foot">wrapshap · shoot guide · run sheet</div>
  `);
}

// ---------------- 3. HOW TO READ + RULES ----------------
{
  const legend = frame({ shot: 'CU', mv: 'push', num: '1', bg: 'factory', body: phone(34, 60, 112, 214, { film: 'flush', screen: 'lit' }) + `<rect x="6" y="32" width="168" height="230" fill="none" stroke="${C.ink}" stroke-width="0.8" stroke-dasharray="3 4" opacity="0.4"/>` });
  const L = (x, y, t, d) => `<div style="position:absolute;left:${x}px;top:${y}px;width:230px"><b style="font-size:12.5px">${t}</b><div style="font-size:11px;line-height:1.35;color:#333">${d}</div></div>`;
  addPage(`
    <div style="position:absolute;left:48px;top:34px"><div class="kick">HOW TO READ THE FRAMES</div><div style="font-size:40px;font-weight:800;letter-spacing:-.01em;margin-top:2px">One frame, one decision</div></div>
    <div style="position:absolute;left:300px;top:130px;width:188px">${inl(legend)}</div>
    ${L(60, 160, 'Yellow ghost offset', 'The “almost”. Every frame carries one. Our film closes the gap.')}
    ${L(60, 270, 'Frame number', 'Yellow disc, top right. Matches the caption below.')}
    ${L(60, 360, 'Shot chip', 'Shot size: MACRO, CU, MCU, MS, WS. Black chip, top left.')}
    ${L(520, 170, 'Dashed box', 'Safe zone for 9:16. Keep faces and text inside it, clear of the platform buttons.')}
    ${L(520, 300, 'Camera move icon', 'White pill, top right under the number: LOCKED, PUSH IN, PULL OUT, TILT, PAN, GIMBAL ARC, HANDHELD, OVERHEAD.')}
    ${L(520, 400, 'Timeline rail', 'Top of every script page. Width is the real duration of each beat.')}
    <div class="card" style="position:absolute;left:48px;top:490px;width:716px;height:216px;padding:14px 16px">
      <div class="lab">DELIVERY SPEC (SUGGESTED)</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px 22px;margin-top:10px">
        <ul class="tick"><li>Vertical 9:16, 1080×1920, 30 fps</li><li>120 fps or more for slow-mo beats only</li><li>Phone on a tripod unless the frame says HANDHELD</li><li>Clean the lens and the dummy before every take</li></ul>
        <ul class="tick"><li>Dialogue in Roman Urdu, English subtitles burned in</li><li>Record 30 s of room tone per location</li><li>Shoot every beat three times, keep rolling on cuts</li><li>Carousels and photos: 4:5, 1080×1350</li></ul>
      </div>
      <div class="dash" style="margin-top:8px">Timers are real. Nothing on screen is sped up, slowed down or faked except where this guide says SLOW-MO.</div>
    </div>
    <div class="card" style="position:absolute;left:800px;top:34px;width:592px;height:738px;padding:18px 20px;background:${C.ink};color:#fff;border-color:${C.ink};box-shadow:5px 6px 0 ${C.Y}">
      <div class="lab">RULES THAT LIVE ON EVERY SET</div>
      <div style="margin-top:12px">${[
        ['01', 'Sparkle logo only.', 'The original has six-point stars that many in Pakistan read as a Star of David. Use the four-point sparkle on every file and the kiosk sign. No close-up of any logo that still has the stars.'],
        ['02', 'Say it by the spec sheet.', '“Scratch-resistant (3H–5H)”, never “scratch-proof”. Impact talk is TUFF’s alone: never “unbreakable” or “shatterproof”. “99%+ light transmittance” (CLEAR).'],
        ['03', 'Receipts, or it didn’t happen.', 'Real timers. No speed-ramps. The “under 60 seconds” line only goes out if the take really is. The privacy film goes dark at 35° for real, in camera.'],
        ['04', 'Consent.', 'Written permission from every person filmed (A3 winners, C4, D1). Cast a friend as the neighbour in D3. No broken phones for A2.'],
        ['05', 'Dummy screens don’t light up.', 'Only the film’s own behaviour is shown as proof. Skits play as comedy.'],
        ['06', 'Every post points to the kiosk.', 'Location, hours, opening day, or “will it fit mine?”.'],
      ].map(([n, t, d]) => `<div style="display:flex;gap:12px;margin-bottom:14px"><div class="an" style="font-size:24px;color:${C.Y};width:34px;flex:none">${n}</div><div><div style="font-weight:800;font-size:15px">${t}</div><div style="font-size:12px;line-height:1.4;color:#ddd;margin-top:2px">${d}</div></div></div>`).join('')}</div>
      <div style="position:absolute;left:20px;right:20px;bottom:16px;font-size:10.5px;color:#aaa">Source: launch plan pp. 4–6 and 32.</div>
    </div>
  `);
}

// ---------------- 4. SCRIPT PAGES ----------------
const colW = 168, gap = 24, fx = 48, fy = 150;
for (const [si, s] of SCRIPTS.entries()) {
  const n = s.beats.length;
  const rail = s.beats.map((b, i) => `<div style="width:${((b.b - b.a) / s.len * 100).toFixed(2)}%;background:${i % 2 ? C.Y2 : C.Y}">${b.a}–${b.b}s</div>`).join('');
  const cols = s.beats.map((b, i) => `
    <div style="position:absolute;left:${fx + i * (colW + gap)}px;top:${fy}px;width:${colW}px">
      ${inl(b.art())}
      <div class="cap" style="margin-top:6px"><span class="t">${b.a}–${b.b}s</span>
        <div><b>${esc(b.shot)}</b> · ${esc(b.act)}</div>
        ${b.say ? `<div class="say" style="margin-top:3px">${esc(b.say)}</div>` : ''}
        ${b.text ? `<div style="margin-top:3px"><span class="txt">TEXT: ${esc(b.text)}</span></div>` : ''}
      </div>
    </div>`).join('');
  const planSvg = floorPlan({ w: 400, h: 150, ...s.plan, label: 'TOP-DOWN · SUGGESTED' });
  const freeX = fx + n * (colW + gap);
  const freeW = 1392 - freeX;
  const side = n <= 5 ? `
    <div style="position:absolute;left:${freeX + 4}px;top:${fy}px;width:${freeW - 4}px">
      <div class="lab" style="margin-bottom:6px">FLOOR PLAN · ${esc(s.block)}</div>
      <div style="border:2.5px solid ${C.ink};border-radius:12px;overflow:hidden;background:#fff">${planSvg}</div>
      <div class="lab" style="margin:12px 0 6px">CAMERA AND EDIT NOTES</div>
      <ul class="tick" style="font-size:11px">
        <li>Shots: ${[...new Set(s.beats.map((b) => b.shot.split(' ')[0]))].map(esc).join(' · ')}</li>
        <li>Moves: ${[...new Set(s.beats.map((b) => b.mv))].map((m) => ({ locked: 'locked', push: 'push in', pull: 'pull out', pan: 'pan', tilt: 'tilt', whip: 'record-scratch cut', hand: 'handheld', orbit: 'orbit' }[m] || m)).join(', ')}</li>
        <li>Keep captions inside the dashed safe box.</li>
        <li>Shoot each beat three times.</li>
      </ul>
    </div>` : '';
  const bandTop = 602, bandH = 152;
  const planBox = n > 5 ? `<div style="position:absolute;left:48px;top:${bandTop - 6}px;width:400px"><div class="lab" style="margin-bottom:4px">FLOOR PLAN · ${esc(s.block)}</div><div style="border:2.5px solid ${C.ink};border-radius:12px;overflow:hidden;background:#fff">${floorPlan({ w: 400, h: 150, ...s.plan, label: 'TOP-DOWN · SUGGESTED' })}</div></div>` : '';
  const x0 = n > 5 ? 48 + 400 + 24 : 48;
  const R = 1392 - x0;
  const wC = Math.round(R * 0.36), wT = Math.round(R * 0.26), wR = R - wC - wT - 24;
  const takeRows = s.beats.map((b, i) => `<div style="display:flex;align-items:center;gap:4px;font-size:10.5px;height:19px;white-space:nowrap"><span class="mono" style="width:14px;font-weight:500">${i + 1}</span>${[1, 2, 3].map(() => `<span style="display:inline-block;width:12px;height:12px;border:1.6px solid ${C.ink};border-radius:3px;background:#fff"></span>`).join('')}<span style="display:inline-block;width:14px;height:14px;border:1.6px solid ${C.ink};border-radius:7px;background:${C.Y};margin-left:4px"></span></div>`).join('');
  addPage(`
    <div class="badge" style="position:absolute;left:48px;top:30px;width:78px;height:62px;font-size:38px">${s.id}</div>
    <div style="position:absolute;left:146px;top:28px">
      <div class="kick">FACTORY SHOOT · SCRIPT ${String(si + 1).padStart(2, '0')} OF 10 · ${esc(s.kind)} · ${s.len}S</div>
      <div style="font-size:38px;font-weight:800;letter-spacing:-.01em;line-height:1.05;margin-top:2px">${esc(s.title)}</div>
    </div>
    <div style="position:absolute;right:48px;top:36px;display:flex;gap:8px;align-items:center"><span class="chip k">${esc(s.tag)}</span><span class="chip y">${esc(s.block)}</span><span class="chip">9:16 · ${s.len}s · EN subtitles</span></div>
    <div class="rail" style="position:absolute;left:48px;top:112px;width:1344px">${rail}</div>
    ${cols}${side}${planBox}
    <div class="card" style="position:absolute;left:${x0}px;top:${bandTop}px;width:${wC}px;height:${bandH}px;padding:10px 14px;font-size:11.5px;line-height:1.4;overflow:hidden">
      <div class="lab">CAST AND PROPS</div>
      <div style="margin-top:6px"><b>Cast:</b> ${esc(s.cast)}</div>
      <div style="margin-top:3px"><b>Props:</b> ${esc(s.props)}</div>
    </div>
    <div class="card" style="position:absolute;left:${x0 + wC + 12}px;top:${bandTop}px;width:${wT}px;height:${bandH}px;padding:10px 14px;overflow:hidden">
      <div class="lab">TAKE LOG</div><span style="font-size:9.5px;color:${C.grey};margin-left:6px">3 takes · yellow = keep</span>
      <div style="margin-top:4px;display:grid;grid-template-columns:${n > 4 ? '1fr 1fr' : '1fr'};gap:0 10px">${takeRows}</div>
    </div>
    <div class="dash" style="position:absolute;left:${x0 + wC + wT + 24}px;top:${bandTop}px;width:${wR}px;height:${bandH}px;overflow:hidden;font-size:11.5px">
      <span class="lab">HOUSE RULE</span>
      <div style="margin-top:6px">${esc(s.rule)}</div>
      <div style="margin-top:6px;color:${C.grey};font-size:10.5px">Timings are from the launch plan${s.id === 'S9' ? ', except where marked proposed' : ''}. Shot sizes and moves are suggestions.</div>
    </div>
    <div class="foot">wrapshap · shoot guide · ${s.id}</div>
  `);
}

// ---------------- 5. POST CARDS ----------------
const cardH = 380, cardW = 1392;
function postCard(p, top) {
  const n = p.frames.length;
  const is45 = p.frames[0].art().includes('viewBox="-6 -6 216 266"');
  const cw = n <= 6 ? 124 : n === 7 ? 114 : 106, cg = 8;
  const cols = p.frames.map((f, i) => `
    <div style="position:absolute;left:${16 + i * (cw + cg)}px;top:70px;width:${cw}px">
      ${inl(f.art())}
      <div class="cap" style="margin-top:4px;font-size:10px"><span class="t" style="font-size:9.5px">${esc(f.t)}</span><div>${esc(f.cap)}</div></div>
    </div>`).join('');
  return `
  <div class="card" style="position:absolute;left:24px;top:${top}px;width:${cardW}px;height:${cardH}px;overflow:hidden">
    <div class="badge" style="position:absolute;left:16px;top:12px;width:62px;height:46px;font-size:28px;border-radius:11px">${p.id}</div>
    <div style="position:absolute;left:92px;top:8px;width:790px"><div class="kick" style="font-size:10.5px">${esc(p.phase)}</div><div style="font-size:25px;font-weight:800;line-height:1.1;letter-spacing:-.01em">${esc(p.title)}</div></div>
    <div style="position:absolute;left:560px;top:14px;width:330px;display:flex;gap:6px;justify-content:flex-end;flex-wrap:wrap">${p.proposed ? `<span class="chip k" style="font-size:10px">PROPOSED BEATS</span>` : `<span class="chip y" style="font-size:10px">AS PER PLAN</span>`}</div>
    <div style="position:absolute;left:16px;top:52px;display:flex;gap:6px">${p.fmt.map((f) => `<span class="chip" style="font-size:10px;padding:1px 8px">${esc(f)}</span>`).join('')}</div>
    ${cols}
    ${p.extra ? (() => { const right = n <= 4; const fh = is45 ? cw * 266 / 216 : cw * 336 / 196; const left = right ? 16 + n * (cw + cg) + 8 : 16; const top = right ? 70 : Math.round(70 + fh + 50); const wd = right ? 912 - left : 896; const cols2 = right ? 1 : 2; return `<div style="position:absolute;left:${left}px;top:${top}px;width:${wd}px;background:#fff;border:2px solid ${C.ink};border-radius:10px;padding:8px 12px"><span class="lab" style="font-size:9.5px">${esc(p.extra.title)}</span><ul class="tick" style="margin-top:6px;columns:${cols2};column-gap:22px">${p.extra.items.map((t) => `<li style="font-size:10.5px;break-inside:avoid">${esc(t)}</li>`).join('')}</ul></div>`; })() : ''}
    <div style="position:absolute;left:928px;top:12px;width:448px;height:${cardH - 24}px;font-size:11px;line-height:1.38">
      <div class="blk"><div class="lab" style="font-size:9.5px">ON-SCREEN TEXT</div>${p.texts.map((t) => `<div class="mk" style="color:#fff;font-size:11.5px;margin-top:3px"><span style="color:${C.Y}">»</span> ${esc(t)}</div>`).join('')}</div>
      <div style="margin-top:8px"><span class="lab" style="font-size:9.5px">THE LOOK</span><div style="margin-top:3px">${esc(p.look)}</div></div>
      <div style="margin-top:8px"><span class="lab" style="font-size:9.5px">CAMERA AND SET${p.proposed ? ' (SUGGESTED)' : ''}</span><div style="margin-top:3px">${esc(p.cam)}</div></div>
      <div class="dash" style="margin-top:8px;font-size:10.5px;padding:6px 10px"><b>House rule:</b> ${esc(p.rule)}</div>
    </div>
  </div>`;
}
for (let i = 0; i < POSTS.length; i += 2) {
  const pair = POSTS.slice(i, i + 2);
  addPage(pair.map((p, k) => postCard(p, 8 + k * (cardH + 10))).join(''));
}

// ---------------- 6. CALENDAR ----------------
{
  const weeks = [['W-4', 'Groundwork · no posts', []], ['W-3', 'Phase 1', ['A1 · Mon', 'A2 · Fri']], ['W-2', 'Phase 1', ['A3 · Mon', 'A5 · Thu', 'A3 entries close']], ['W-1', 'Phase 2', ['B1 · Mon', 'B2 · Tue', 'B3 · Wed', 'B4 · Thu', 'B5 · Fri', 'B6 · Sat']], ['L', 'Phase 3 · days L → L+6', ['C1 · L', 'C4 · L+1', 'C2 · L+2', 'C3 · L+3', 'C5 · L+5']], ['L+1', 'Phase 4 · week 1', ['D1', 'D2 (then pinned)', 'D3', 'C3', 'C5']], ['L+2', 'Phase 4 · week 2', ['D1', 'D3', 'C3', 'C5']], ['L+3', 'Phase 4 · week 3', ['D1', 'D3', 'C3', 'C5']], ['L+4', 'Phase 4 · week 4', ['D1', 'D3', 'C3', 'C5', 'Review + plan month 2']]];
  const col = (i) => (i === 0 ? '#e9e6df' : i <= 2 ? C.Y : i === 3 ? '#fff' : i === 4 ? C.ink : '#fff');
  addPage(`
    <div style="position:absolute;left:48px;top:34px"><div class="kick">LAUNCH MAP · COUNTED BACK FROM OPENING DAY</div><div style="font-size:40px;font-weight:800;letter-spacing:-.01em;margin-top:2px">What gets shot for what, and when</div></div>
    ${weeks.map(([w, ph, items], i) => `
      <div class="card" style="position:absolute;left:${48 + i * 150}px;top:124px;width:140px;height:330px;padding:10px;background:${col(i)};color:${i === 4 ? C.Y : C.ink}">
        <div class="an" style="font-size:26px">${w}</div><div style="font-size:10.5px;font-weight:700;margin:2px 0 8px;opacity:.8;min-height:26px">${ph}</div>
        ${items.map((t) => `<div style="background:${i === 4 ? C.Y : '#fff'};color:${C.ink};border:2px solid ${C.ink};border-radius:8px;padding:4px 8px;margin-bottom:6px;font-size:12px;font-weight:700">${t}</div>`).join('')}
      </div>`).join('')}
    <div class="card big" style="position:absolute;left:48px;top:484px;width:640px;height:288px;padding:16px 18px">
      <div class="lab">WHERE THE SHOOT FEEDS THE POSTS (SUGGESTED)</div>
      <ul class="tick" style="margin-top:12px">
        <li><b>S4 Which Half?</b> rehearses B3: decide which half carries the film before either shoots.</li>
        <li><b>S8 Not Your Screen, Uncle</b> and <b>S7 “Glass Wala Do”</b> rehearse B4 and D2, with the same house rules.</li>
        <li><b>S1, S3 and S10</b> hold the cut footage that C2, C4 and C5 reuse as b-roll.</li>
        <li><b>B5 and B6</b> are not factory shoots: B5 needs noon sun outdoors, B6 needs a drop rig and a tested height.</li>
        <li>Weekly series (C3, C5, D1, D3) need one shoot day each week from L+1.</li>
      </ul>
    </div>
    <div class="card big" style="position:absolute;left:712px;top:484px;width:680px;height:288px;padding:16px 18px">
      <div class="lab">BEFORE PHASE 1 STARTS</div>
      <ul class="tick" style="margin-top:10px">
        <li>Swap the logo stars for the sparkle on every file and on the kiosk sign.</li>
        <li>Lock the opening date and the mall. No teaser goes out without a date, and no more than 3 weeks before.</li>
        <li>Profiles and bios are live. Batch shoot 1 is done in W-4.</li>
        <li>Spec sheet in hand: every number on screen is checked against it.</li>
      </ul>
    </div>
    <div class="foot">Source: launch plan pp. 7–8. In opening week “L+n” means n days after opening; from Phase 4 it means weeks.</div>
  `);
}

// ---------------- 7. QC + OPEN QUESTIONS ----------------
{
  addPage(`
    <div style="position:absolute;left:48px;top:34px"><div class="kick">BEFORE ANYTHING GOES OUT</div><div style="font-size:40px;font-weight:800;letter-spacing:-.01em;margin-top:2px">Quality check and open questions</div></div>
    <div class="card big" style="position:absolute;left:48px;top:122px;width:660px;height:650px;padding:16px 20px">
      <div class="lab">EVERY CLIP AND IMAGE</div>
      <ul class="tick" style="margin-top:12px">
        ${['Logo is the four-point sparkle version. Zoom in and check both “a”s.', 'No six-point star anywhere: logo, sign, sticker, doodle or AI-generated image.', 'Every number matches the spec sheet: 0.25–0.35 mm, 4H–5H, 99%+, 35°, 0.15–0.20 mm (never reversed).', 'No “scratch-proof”, “unbreakable” or “shatterproof”. Impact language is TUFF only.', 'Every timer on screen is a real timer, and the “under 60 seconds” line matches it.', 'The drop height on screen is the real height (B6).', 'Subtitles burned in on every dialogue clip, in English.', 'Consent forms on file for everyone who appears; asked again before posting.', 'Mall, floor, hours and date filled in. No “[MALL]” or “[KIOSK LOCATION]” left on any frame.', 'The last frame points to the kiosk.', 'AI-generated art (for example from Flow): read every word on it. Image models misspell and invent text.']
          .map((t) => `<li style="margin-bottom:9px">${esc(t)}</li>`).join('')}
      </ul>
    </div>
    <div class="card big" style="position:absolute;left:732px;top:122px;width:660px;height:360px;padding:16px 20px">
      <div class="lab">STILL OPEN (NEEDS THE TEAM)</div>
      <ul class="tick" style="margin-top:12px">
        <li><b>Mall, floor, opening date.</b> Needed for B1, C1, C2, C5, D1, D2 and every end card.</li>
        <li><b>What the kiosk looks like.</b> The frames show a generic kiosk. Send a photo and the art can be redrawn to match.</li>
        <li><b>Real timer results</b> for the “under 60 seconds” claim, and the real drop height for B6.</li>
        <li><b>Cast for Day 1:</b> shopkeeper, customer, three staffers, two uncles, a girl and a friend, one actor for four roles.</li>
        <li><b>S9 timings</b> after 0–2s are proposed; the plan lists the order only.</li>
      </ul>
    </div>
    <div class="card" style="position:absolute;left:732px;top:506px;width:660px;height:266px;padding:16px 20px;background:${C.Y}">
      <div class="lab" style="background:${C.ink};color:${C.Y}">WHAT THIS GUIDE IS NOT</div>
      <div style="font-size:12.5px;line-height:1.45;margin-top:10px">The frames are drawn in code, in the brand’s marker style, to show framing, blocking, timing and camera moves. They are not photos and they do not show the real kiosk. The Day-1 times and the post beats marked PROPOSED are suggestions to adjust on the day. Everything else, including dialogue, on-screen text, timings and house rules, comes straight from the launch plan.</div>
      <div style="position:absolute;right:20px;bottom:14px">${logoImg(46)}</div>
    </div>
    <div class="foot">wrapshap · shoot guide · QC</div>
  `);
}

const html = `<!doctype html><html><head><meta charset="utf-8"><title>Wrapshap Shoot Guide</title><style>${CSS}</style></head><body>${pages.join('\n')}</body></html>`;
fs.writeFileSync(path.join(out, 'guide.html'), html);
console.log('pages', pages.length, 'frames', totalFrames);
