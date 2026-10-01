// Drawing kit for the Wrapshap shoot guide. All art is SVG, drawn in code.
// RULE: never draw a six-point star. Sparkles are four-point only.

export const C = {
  Y: '#FFD500', Y2: '#FFE45C', ink: '#121212', paper: '#F3F1ED', card: '#FFFDF7',
  amber: '#F39200', grey: '#6b6a65', line: '#d8d4ca', factory: '#D9D6CE',
  skin: ['#C98B5E', '#E2AE82', '#A8683F', '#D49A6A'],
  pink: '#F06FA8', green: '#2FA55A', purple: '#7E57C2', white: '#ffffff',
};

const f = (n) => Math.round(n * 100) / 100;

export const sparkle = (cx, cy, r, fill = C.ink, stroke = 'none') =>
  `<path d="M${f(cx)},${f(cy - r)} Q${f(cx)},${f(cy)} ${f(cx + r)},${f(cy)} Q${f(cx)},${f(cy)} ${f(cx)},${f(cy + r)} Q${f(cx)},${f(cy)} ${f(cx - r)},${f(cy)} Q${f(cx)},${f(cy)} ${f(cx)},${f(cy - r)}Z" fill="${fill}" stroke="${stroke}" stroke-width="1"/>`;

export const crown = (x, y, s = 1, col = C.ink) =>
  `<g transform="translate(${x},${y}) scale(${s})"><path d="M0,16 L3,3 L9,11 L14,0 L19,11 L25,3 L28,16 Z" fill="none" stroke="${col}" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"/><path d="M1,20 L27,20" stroke="${col}" stroke-width="2.4" stroke-linecap="round"/></g>`;

export const smiley = (x, y, r = 10, col = C.ink, fill = 'none') =>
  `<g transform="translate(${x},${y})"><circle r="${r}" fill="${fill}" stroke="${col}" stroke-width="2"/><circle cx="${-r * 0.35}" cy="${-r * 0.2}" r="${r * 0.1}" fill="${col}"/><circle cx="${r * 0.35}" cy="${-r * 0.2}" r="${r * 0.1}" fill="${col}"/><path d="M${-r * 0.5},${r * 0.2} Q0,${r * 0.75} ${r * 0.5},${r * 0.2}" fill="none" stroke="${col}" stroke-width="2" stroke-linecap="round"/></g>`;

export function sticker(x, y, txt, { rot = -4, bg = C.ink, fg = C.Y, size = 13, pad = 6 } = {}) {
  const w0 = txt.length * size * 0.5 + pad * 2;
  if (w0 > 162) size = Math.max(7, size * 162 / w0);
  const w = txt.length * size * 0.5 + pad * 2;
  const h = size + pad * 1.4;
  return `<g transform="translate(${x},${y}) rotate(${rot})"><rect x="${-w / 2}" y="${-h / 2}" width="${f(w)}" height="${f(h)}" rx="3" fill="${bg}"/><text x="0" y="${f(size * 0.36)}" text-anchor="middle" font-family="Anton" font-size="${size}" letter-spacing="0.4" fill="${fg}">${esc(txt)}</text></g>`;
}

export function note(x, y, txt, { size = 12, rot = 0, fill = C.ink, anchor = 'middle' } = {}) {
  const w0 = txt.length * size * 0.62;
  if (w0 > 164) size = Math.max(7, size * 164 / w0);
  return `<text transform="translate(${x},${y}) rotate(${rot})" text-anchor="${anchor}" font-family="Permanent Marker" font-size="${size}" fill="${fill}">${esc(txt)}</text>`;
}

export function esc(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

export function arrow(pts, { col = C.ink, w = 2.4, head = 6 } = {}) {
  if (typeof pts[0] === 'number') pts = pts.reduce((a, v, i) => (i % 2 ? (a[a.length - 1].push(v), a) : (a.push([v]), a)), []);
  const d = pts.map((p, i) => `${i ? 'L' : 'M'}${f(p[0])},${f(p[1])}`).join(' ');
  const [x1, y1] = pts[pts.length - 2];
  const [x2, y2] = pts[pts.length - 1];
  const a = Math.atan2(y2 - y1, x2 - x1);
  const hx = (k) => f(x2 - head * Math.cos(a + k));
  const hy = (k) => f(y2 - head * Math.sin(a + k));
  return `<g fill="none" stroke="${col}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"><path d="${d}"/><path d="M${hx(0.5)},${hy(0.5)} L${f(x2)},${f(y2)} L${hx(-0.5)},${hy(-0.5)}"/></g>`;
}

export function curveArrow(x1, y1, cx, cy, x2, y2, o = {}) {
  const col = o.col || C.ink, w = o.w || 2.4, head = o.head || 6;
  const a = Math.atan2(y2 - cy, x2 - cx);
  const hx = (k) => f(x2 - head * Math.cos(a + k));
  const hy = (k) => f(y2 - head * Math.sin(a + k));
  return `<g fill="none" stroke="${col}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"><path d="M${x1},${y1} Q${cx},${cy} ${x2},${y2}"/><path d="M${hx(0.5)},${hy(0.5)} L${x2},${y2} L${hx(-0.5)},${hy(-0.5)}"/></g>`;
}

export const circleMark = (x, y, r, col = C.ink) =>
  `<ellipse cx="${x}" cy="${y}" rx="${r}" ry="${r * 0.85}" transform="rotate(-12 ${x} ${y})" fill="none" stroke="${col}" stroke-width="2" stroke-dasharray="none" stroke-linecap="round"/>`;

// ---------- phone ----------
export function phone(x, y, w, h, o = {}) {
  const { rot = 0, film = 'none', screen = 'dark', cam = true, body = '#1b1b1c', glare = false, prints = false, lens = true } = o;
  const r = Math.min(w, h) * 0.14;
  const inset = Math.max(2.5, w * 0.05);
  let scr;
  if (screen === 'glossy') scr = `<rect x="${inset}" y="${inset}" width="${w - inset * 2}" height="${h - inset * 2}" rx="${r * 0.7}" fill="#23262c"/><path d="M${inset},${h * 0.18} L${w * 0.7},${inset} L${w - inset},${inset} L${inset},${h * 0.62}Z" fill="#fff" opacity="0.55"/>`;
  else if (screen === 'matte') scr = `<rect x="${inset}" y="${inset}" width="${w - inset * 2}" height="${h - inset * 2}" rx="${r * 0.7}" fill="#2b2d31"/>`;
  else if (screen === 'lit') scr = `<rect x="${inset}" y="${inset}" width="${w - inset * 2}" height="${h - inset * 2}" rx="${r * 0.7}" fill="#f5f6f8"/>`;
  else if (screen === 'yellow') scr = `<rect x="${inset}" y="${inset}" width="${w - inset * 2}" height="${h - inset * 2}" rx="${r * 0.7}" fill="${C.Y}"/>`;
  else scr = `<rect x="${inset}" y="${inset}" width="${w - inset * 2}" height="${h - inset * 2}" rx="${r * 0.7}" fill="#2a2a2e"/>`;
  let fx = '';
  if (film === 'flush') fx = `<rect x="${inset + 1}" y="${inset + 1}" width="${w - inset * 2 - 2}" height="${h - inset * 2 - 2}" rx="${r * 0.6}" fill="none" stroke="#9fe3ff" stroke-width="1.4" opacity="0.9"/>`;
  if (film === 'crooked') fx = `<g transform="rotate(5 ${w / 2} ${h / 2})"><rect x="${inset + 3}" y="${inset + 4}" width="${w - inset * 2 - 6}" height="${h - inset * 2 - 8}" rx="2" fill="#fff" opacity="0.22" stroke="#fff" stroke-width="1.4" opacity="0.8"/><path d="M${w - inset - 3},${inset + 4} l-9,0 l9,9Z" fill="#fff" opacity="0.8"/></g>`;
  if (film === 'half') fx = `<rect x="${inset}" y="${inset}" width="${(w - inset * 2) / 2}" height="${h - inset * 2}" rx="2" fill="#9fe3ff" opacity="0.28"/><line x1="${w / 2}" y1="${inset}" x2="${w / 2}" y2="${h - inset}" stroke="#fff" stroke-width="1.2" stroke-dasharray="3 3"/>`;
  if (film === 'peel') fx = `<path d="M${inset},${h - inset} L${w - inset},${h - inset} L${w - inset},${h * 0.55} Q${w * 0.55},${h * 0.62} ${inset},${h - inset}Z" fill="#fff" opacity="0.5" stroke="#fff"/>`;
  const camEl = cam ? `<g><rect x="${inset + 3}" y="${inset + 3}" width="${w * 0.36}" height="${w * 0.36}" rx="${w * 0.09}" fill="#0b0b0c" stroke="#555" stroke-width="0.8"/><circle cx="${inset + 3 + w * 0.12}" cy="${inset + 3 + w * 0.12}" r="${w * 0.07}" fill="#2d3a55" stroke="#888" stroke-width="0.8"/><circle cx="${inset + 3 + w * 0.25}" cy="${inset + 3 + w * 0.25}" r="${w * 0.07}" fill="#2d3a55" stroke="#888" stroke-width="0.8"/></g>` : '';
  const pr = prints ? `<g stroke="#fff" stroke-width="0.8" opacity="0.5" fill="none"><ellipse cx="${w * 0.4}" cy="${h * 0.6}" rx="${w * 0.16}" ry="${w * 0.1}"/><ellipse cx="${w * 0.4}" cy="${h * 0.6}" rx="${w * 0.1}" ry="${w * 0.06}"/><ellipse cx="${w * 0.62}" cy="${h * 0.74}" rx="${w * 0.13}" ry="${w * 0.08}"/></g>` : '';
  return `<g transform="translate(${x},${y}) rotate(${rot} ${w / 2} ${h / 2})"><rect width="${w}" height="${h}" rx="${r}" fill="${body}" stroke="${C.ink}" stroke-width="2"/>${scr}${fx}${pr}${camEl}</g>`;
}

// ---------- hand ----------
export function hand(x, y, s = 1, o = {}) {
  const { rot = 0, skin = C.skin[1], flip = false, fist = false } = o;
  const sx = flip ? -s : s;
  const fingers = fist ? '' : [-16, -6, 4, 14].map((fx, i) => `<rect x="${fx}" y="${-26 + Math.abs(i - 1.5) * 3}" width="9" height="${30 - Math.abs(i - 1.5) * 3}" rx="4.5" fill="${skin}" stroke="${C.ink}" stroke-width="2"/>`).join('');
  return `<g transform="translate(${x},${y}) rotate(${rot}) scale(${sx},${s})"><rect x="-20" y="-2" width="42" height="40" rx="14" fill="${skin}" stroke="${C.ink}" stroke-width="2"/>${fingers}<ellipse cx="-22" cy="14" rx="7" ry="12" transform="rotate(20 -22 14)" fill="${skin}" stroke="${C.ink}" stroke-width="2"/><rect x="-18" y="36" width="38" height="26" fill="${skin}" stroke="${C.ink}" stroke-width="2"/></g>`;
}

// ---------- person (bust) ----------
export function person(x, y, s = 1, o = {}) {
  const { skin = C.skin[1], hair = '#1a1a1a', shirt = C.Y, glasses = false, hat = null, mood = 'smile', mustache = false, kurta = false, longHair = false, shadeCol = '#111', bottom = 330 } = o;
  const r = 18 * s;
  const sh = `<path d="M${x - 34 * s},${bottom} L${x - 30 * s},${y + r + 12 * s} Q${x},${y + r - 2 * s} ${x + 30 * s},${y + r + 12 * s} L${x + 34 * s},${bottom}Z" fill="${shirt}" stroke="${C.ink}" stroke-width="2"/>`;
  const neck = `<rect x="${x - 6 * s}" y="${y + r - 4 * s}" width="${12 * s}" height="${12 * s}" fill="${skin}" stroke="${C.ink}" stroke-width="2"/>`;
  const kurtaEl = kurta ? `<path d="M${x},${y + r + 10 * s} L${x},${bottom}" stroke="${C.ink}" stroke-width="2"/><circle cx="${x}" cy="${y + r + 22 * s}" r="${1.8 * s}" fill="${C.ink}"/><circle cx="${x}" cy="${y + r + 36 * s}" r="${1.8 * s}" fill="${C.ink}"/>` : '';
  const hairBack = longHair ? `<path d="M${x - r - 2 * s},${y} Q${x - r - 6 * s},${y + r * 2.4} ${x - r + 2 * s},${y + r * 2.4} L${x + r - 2 * s},${y + r * 2.4} Q${x + r + 6 * s},${y + r * 2.4} ${x + r + 2 * s},${y}Z" fill="${hair}" stroke="${C.ink}" stroke-width="2"/>` : '';
  const head = `<circle cx="${x}" cy="${y}" r="${r}" fill="${skin}" stroke="${C.ink}" stroke-width="2"/>`;
  const hairTop = hat ? '' : `<path d="M${x - r},${y - 2 * s} Q${x - r},${y - r - 4 * s} ${x},${y - r - 3 * s} Q${x + r},${y - r - 4 * s} ${x + r},${y - 2 * s} Q${x + r * 0.4},${y - r * 0.6} ${x - r * 0.3},${y - r * 0.55} Q${x - r * 0.8},${y - r * 0.45} ${x - r},${y - 2 * s}Z" fill="${hair}" stroke="${C.ink}" stroke-width="2"/>`;
  const hatEl = hat ? `<path d="M${x - r - 2 * s},${y - 4 * s} Q${x - r},${y - r - 10 * s} ${x},${y - r - 9 * s} Q${x + r},${y - r - 10 * s} ${x + r + 2 * s},${y - 4 * s}Z" fill="${hat}" stroke="${C.ink}" stroke-width="2"/><rect x="${x - r - 4 * s}" y="${y - 6 * s}" width="${2 * r + 8 * s}" height="${5 * s}" rx="${2 * s}" fill="${hat}" stroke="${C.ink}" stroke-width="2"/>` : '';
  const eyeY = y + 1 * s;
  let eyes;
  if (glasses) eyes = `<rect x="${x - 14 * s}" y="${eyeY - 5 * s}" width="${11 * s}" height="${8 * s}" rx="${3 * s}" fill="${shadeCol}"/><rect x="${x + 3 * s}" y="${eyeY - 5 * s}" width="${11 * s}" height="${8 * s}" rx="${3 * s}" fill="${shadeCol}"/><line x1="${x - 3 * s}" y1="${eyeY - 2 * s}" x2="${x + 3 * s}" y2="${eyeY - 2 * s}" stroke="${shadeCol}" stroke-width="2"/>`;
  else eyes = `<circle cx="${x - 7 * s}" cy="${eyeY}" r="${1.9 * s}" fill="${C.ink}"/><circle cx="${x + 7 * s}" cy="${eyeY}" r="${1.9 * s}" fill="${C.ink}"/>`;
  const my = y + 10 * s;
  const mouths = {
    smile: `<path d="M${x - 7 * s},${my} Q${x},${my + 7 * s} ${x + 7 * s},${my}" fill="none" stroke="${C.ink}" stroke-width="2" stroke-linecap="round"/>`,
    flat: `<line x1="${x - 6 * s}" y1="${my + 2 * s}" x2="${x + 6 * s}" y2="${my + 2 * s}" stroke="${C.ink}" stroke-width="2" stroke-linecap="round"/>`,
    shock: `<ellipse cx="${x}" cy="${my + 3 * s}" rx="${4 * s}" ry="${5 * s}" fill="${C.ink}"/>`,
    smug: `<path d="M${x - 6 * s},${my + 2 * s} Q${x + 2 * s},${my + 5 * s} ${x + 8 * s},${my - 1 * s}" fill="none" stroke="${C.ink}" stroke-width="2" stroke-linecap="round"/>`,
    worry: `<path d="M${x - 6 * s},${my + 5 * s} Q${x},${my - 1 * s} ${x + 6 * s},${my + 5 * s}" fill="none" stroke="${C.ink}" stroke-width="2" stroke-linecap="round"/>`,
    open: `<path d="M${x - 8 * s},${my - 1 * s} Q${x},${my + 12 * s} ${x + 8 * s},${my - 1 * s}Z" fill="${C.ink}"/>`,
  };
  const must = mustache ? `<path d="M${x - 9 * s},${my - 3 * s} Q${x - 4 * s},${my - 7 * s} ${x},${my - 3 * s} Q${x + 4 * s},${my - 7 * s} ${x + 9 * s},${my - 3 * s} Q${x + 4 * s},${my - 1 * s} ${x},${my - 2 * s} Q${x - 4 * s},${my - 1 * s} ${x - 9 * s},${my - 3 * s}Z" fill="${C.ink}"/>` : '';
  return `<g>${hairBack}${sh}${kurtaEl}${neck}${head}${hairTop}${hatEl}${eyes}${mouths[mood] || mouths.smile}${must}</g>`;
}

// ---------- kiosk ----------
export function kiosk(x, y, w, h, o = {}) {
  const { glow = true, screenLines = true } = o;
  const sign = h * 0.17;
  return `<g transform="translate(${x},${y})">
    <rect width="${w}" height="${h}" rx="${w * 0.06}" fill="#2a2a2d" stroke="${C.ink}" stroke-width="2.4"/>
    <rect x="3" y="3" width="${w - 6}" height="${sign}" rx="3" fill="${C.Y}" stroke="${C.ink}" stroke-width="2"/>
    ${sparkle(w * 0.2, 3 + sign / 2, sign * 0.3, C.ink)}
    <rect x="${w * 0.34}" y="${3 + sign * 0.35}" width="${w * 0.52}" height="${sign * 0.3}" rx="2" fill="${C.ink}"/>
    <rect x="${w * 0.1}" y="${sign + 12}" width="${w * 0.8}" height="${h * 0.26}" rx="4" fill="#dfe6ee" stroke="${C.ink}" stroke-width="2"/>
    ${screenLines ? [0, 1, 2, 3].map((i) => `<rect x="${w * 0.16}" y="${sign + 17 + i * h * 0.055}" width="${w * (0.44 + (i % 2) * 0.16)}" height="${h * 0.025}" rx="1.5" fill="#8a96a6"/>`).join('') : ''}
    <rect x="${w * 0.1}" y="${sign + 20 + h * 0.26}" width="${w * 0.8}" height="${h * 0.22}" rx="4" fill="#111418" stroke="${C.ink}" stroke-width="2"/>
    <line x1="${w * 0.16}" y1="${sign + 20 + h * 0.37}" x2="${w * 0.84}" y2="${sign + 20 + h * 0.37}" stroke="#ff5a4d" stroke-width="1.6" stroke-dasharray="4 3"/>
    <rect x="${w * 0.28}" y="${h * 0.84}" width="${w * 0.44}" height="${h * 0.035}" rx="2" fill="#050505" stroke="#555" stroke-width="1"/>
    ${glow ? `<rect x="3" y="${h - 9}" width="${w - 6}" height="5" rx="2.5" fill="${C.amber}"/><rect x="0" y="${h - 12}" width="${w}" height="11" rx="5" fill="${C.amber}" opacity="0.25"/>` : ''}
  </g>`;
}

export function timer(x, y, txt = '00:00', { size = 13, rot = 0, bg = C.ink, fg = C.Y } = {}) {
  const w = txt.length * size * 0.62 + 16;
  return `<g transform="translate(${x},${y}) rotate(${rot})"><rect x="${-w / 2}" y="${-size * 0.95}" width="${f(w)}" height="${size * 1.9}" rx="${size * 0.6}" fill="${bg}"/><circle cx="${-w / 2 + 9}" cy="0" r="3" fill="#ff4d4d"/><text x="${f(6)}" y="${size * 0.36}" text-anchor="middle" font-family="DM Mono" font-size="${size}" fill="${fg}">${esc(txt)}</text></g>`;
}

export const bubble = (x, y, r = 6) =>
  `<g><circle cx="${x}" cy="${y}" r="${r}" fill="#fff" opacity="0.35" stroke="#fff" stroke-width="1.4"/><circle cx="${x - r * 0.35}" cy="${y - r * 0.35}" r="${r * 0.22}" fill="#fff"/></g>`;

export const dust = (x, y, n = 6, spread = 14) =>
  Array.from({ length: n }, (_, i) => `<circle cx="${f(x + Math.sin(i * 2.3) * spread)}" cy="${f(y + Math.cos(i * 3.1) * spread * 0.6)}" r="${1 + (i % 3) * 0.5}" fill="#8a7f6a"/>`).join('');

export const filmSheet = (x, y, w, h, o = {}) =>
  `<g transform="translate(${x},${y}) rotate(${o.rot || 0})"><rect width="${w}" height="${h}" rx="3" fill="#bfeaff" opacity="0.55" stroke="${C.ink}" stroke-width="1.8"/><path d="M0,${h} L${w},${h} L${w},${h * 0.7} Q${w * 0.5},${h * 0.85} 0,${h}Z" fill="#fff" opacity="0.6"/></g>`;

export const blade = (x, y, len = 40, rot = 0) =>
  `<g transform="translate(${x},${y}) rotate(${rot})"><path d="M0,0 L${len},-4 L${len},4Z" fill="#c9ced6" stroke="${C.ink}" stroke-width="1.8"/><rect x="${-len * 0.45}" y="-5" width="${len * 0.45}" height="10" rx="3" fill="${C.ink}"/></g>`;

export const clothPad = (x, y, w = 40, h = 26, col = '#e8e2d2') =>
  `<g transform="translate(${x},${y})"><rect width="${w}" height="${h}" rx="5" fill="${col}" stroke="${C.ink}" stroke-width="2"/><path d="M6,${h * 0.35} Q${w / 2},${h * 0.1} ${w - 6},${h * 0.35} M6,${h * 0.7} Q${w / 2},${h * 0.45} ${w - 6},${h * 0.7}" fill="none" stroke="${C.ink}" stroke-width="1" opacity="0.4"/></g>`;

export const sun = (x, y, r = 14) =>
  `<g><circle cx="${x}" cy="${y}" r="${r}" fill="${C.Y}" stroke="${C.ink}" stroke-width="2"/>${Array.from({ length: 10 }, (_, i) => { const a = (i / 10) * Math.PI * 2; return `<line x1="${f(x + Math.cos(a) * (r + 4))}" y1="${f(y + Math.sin(a) * (r + 4))}" x2="${f(x + Math.cos(a) * (r + 10))}" y2="${f(y + Math.sin(a) * (r + 10))}" stroke="${C.ink}" stroke-width="2" stroke-linecap="round"/>`; }).join('')}</g>`;

export const flash = (W, H) => `<rect width="${W}" height="${H}" fill="#fff" opacity="0.75"/>`;

// ---------- camera-move icon ----------
const MOVE_LABELS = { locked: 'LOCKED', push: 'PUSH IN', pull: 'PULL OUT', orbit: 'ORBIT', tilt: 'TILT', hand: 'HANDHELD', gimbal: 'GIMBAL ARC', overhead: 'OVERHEAD', pan: 'PAN', whip: 'RECORD-SCRATCH CUT' };
export const moveWidth = (kind) => 64 + (MOVE_LABELS[kind] || kind).length * 6.1;
export function move(kind, x, y) {
  const lab = { locked: 'LOCKED', push: 'PUSH IN', pull: 'PULL OUT', orbit: 'ORBIT', tilt: 'TILT', hand: 'HANDHELD', gimbal: 'GIMBAL ARC', overhead: 'OVERHEAD', pan: 'PAN', whip: 'RECORD-SCRATCH CUT' }[kind] || kind;
  const cam = `<rect x="0" y="-7" width="16" height="12" rx="2.5" fill="${C.ink}"/><path d="M16,-4 L23,-8 L23,6 L16,2Z" fill="${C.ink}"/>`;
  let ar = '';
  if (kind === 'push') ar = `<path d="M28,-6 L36,0 L28,6 M36,-6 L44,0 L36,6" fill="none" stroke="${C.ink}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>`;
  if (kind === 'pull') ar = `<path d="M44,-6 L36,0 L44,6 M36,-6 L28,0 L36,6" fill="none" stroke="${C.ink}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>`;
  if (kind === 'orbit' || kind === 'gimbal') ar = `<path d="M28,6 Q36,-10 46,2" fill="none" stroke="${C.ink}" stroke-width="2.2" stroke-linecap="round"/><path d="M42,-2 L46,2 L40,4" fill="none" stroke="${C.ink}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>`;
  if (kind === 'tilt') ar = `<path d="M34,8 L34,-8 M30,-4 L34,-8 L38,-4" fill="none" stroke="${C.ink}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>`;
  if (kind === 'pan') ar = `<path d="M28,0 L46,0 M42,-4 L46,0 L42,4" fill="none" stroke="${C.ink}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>`;
  if (kind === 'locked') ar = `<rect x="30" y="-3" width="11" height="9" rx="2" fill="${C.ink}"/><path d="M32.5,-3 v-3 a3,3 0 0 1 6,0 v3" fill="none" stroke="${C.ink}" stroke-width="2"/>`;
  if (kind === 'hand') ar = `<path d="M28,2 l3,-4 l3,5 l3,-5 l3,4 l3,-3" fill="none" stroke="${C.ink}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>`;
  if (kind === 'overhead') ar = `<circle cx="36" cy="0" r="6" fill="none" stroke="${C.ink}" stroke-width="2"/><circle cx="36" cy="0" r="1.8" fill="${C.ink}"/>`;
  if (kind === 'whip') ar = `<path d="M28,-6 L44,-6 M28,0 L40,0 M28,6 L36,6" stroke="${C.ink}" stroke-width="2.2" stroke-linecap="round"/>`;
  return `<g transform="translate(${x},${y})">${cam}${ar}<text x="50" y="4" font-family="DM Mono" font-size="9" fill="${C.ink}">${lab}</text></g>`;
}

// ---------- frame wrapper ----------
const ASPECT = { '9:16': [180, 320], '4:5': [200, 250], '16:9': [320, 180], '1:1': [220, 220] };
export function aspectSize(a) { return ASPECT[a] || ASPECT['9:16']; }

export function frame({ aspect = '9:16', bg = '#fff', body = '', shot = '', num = '', dark = false, guide = true, mv = null, ghost = true } = {}) {
  const [W, H] = aspectSize(aspect);
  const id = 'c' + Math.random().toString(36).slice(2, 8);
  const bgEl = typeof bg === 'string' && bg.startsWith('factory')
    ? `<rect width="${W}" height="${H}" fill="${C.factory}"/><rect x="0" y="0" width="${W}" height="${H * 0.1}" fill="#eef1f4"/><rect x="${W * 0.1}" y="6" width="${W * 0.34}" height="5" rx="2.5" fill="#fff"/><rect x="${W * 0.56}" y="6" width="${W * 0.34}" height="5" rx="2.5" fill="#fff"/>`
    : `<rect width="${W}" height="${H}" fill="${bg}"/>`;
  const gd = guide && aspect === '9:16' ? `<rect x="6" y="${H * 0.1}" width="${W - 12}" height="${H * 0.72}" fill="none" stroke="${dark ? '#fff' : C.ink}" stroke-width="0.8" stroke-dasharray="3 4" opacity="0.22"/>` : '';
  const shotChip = shot ? `<g><rect x="6" y="6" width="${shot.length * 6.2 + 10}" height="15" rx="3" fill="${C.ink}"/><text x="11" y="17" font-family="DM Mono" font-size="9.5" font-weight="500" fill="${C.Y}">${esc(shot)}</text></g>` : '';
  const numChip = num ? `<g><circle cx="${W - 14}" cy="14" r="10" fill="${C.Y}" stroke="${C.ink}" stroke-width="1.8"/><text x="${W - 14}" y="18" text-anchor="middle" font-family="Anton" font-size="12" fill="${C.ink}">${esc(num)}</text></g>` : '';
  let mvEl = '';
  if (mv) { const pw = moveWidth(mv); mvEl = `<g><rect x="${W - pw - 4}" y="27" width="${pw}" height="17" rx="8.5" fill="#fff" opacity="0.94" stroke="${C.ink}" stroke-width="1.2"/>${move(mv, W - pw + 4, 36)}</g>`; }
  return `<svg viewBox="-6 -6 ${W + 16} ${H + 16}" xmlns="http://www.w3.org/2000/svg" class="frame">
  <defs><clipPath id="${id}"><rect width="${W}" height="${H}" rx="10"/></clipPath></defs>
  ${ghost ? `<rect x="5" y="5" width="${W}" height="${H}" rx="10" fill="${C.Y}" opacity="0.9"/>` : ''}
  <g clip-path="url(#${id})">${bgEl}${body}${gd}</g>
  <rect width="${W}" height="${H}" rx="10" fill="none" stroke="${C.ink}" stroke-width="3"/>
  ${shotChip}${numChip}${mvEl}
</svg>`;
}

// ---------- floor plan (top-down) ----------
export function floorPlan({ w = 400, h = 150, kind = 'machine', cams = [], actors = [], lights = [], items = [], label = '' }) {
  let room = `<rect x="2" y="2" width="${w - 4}" height="${h - 4}" rx="6" fill="#fbfaf6" stroke="${C.ink}" stroke-width="2"/>`;
  room += `<g stroke="${C.line}" stroke-width="1">${Array.from({ length: Math.floor(w / 20) }, (_, i) => `<line x1="${i * 20 + 10}" y1="4" x2="${i * 20 + 10}" y2="${h - 4}"/>`).join('')}${Array.from({ length: Math.floor(h / 20) }, (_, i) => `<line x1="4" y1="${i * 20 + 10}" x2="${w - 4}" y2="${i * 20 + 10}"/>`).join('')}</g>`;
  if (kind === 'machine') room += `<rect x="${w / 2 - 34}" y="6" width="68" height="22" rx="3" fill="#2a2a2d" stroke="${C.ink}" stroke-width="2"/><rect x="${w / 2 - 30}" y="9" width="60" height="5" rx="2" fill="${C.Y}"/><text x="${w / 2}" y="24" text-anchor="middle" font-family="DM Mono" font-size="8" fill="#fff">KIOSK</text><rect x="${w / 2 - 50}" y="34" width="100" height="12" rx="3" fill="#e8e2d2" stroke="${C.ink}" stroke-width="1.6"/><text x="${w / 2}" y="43" text-anchor="middle" font-family="DM Mono" font-size="7" fill="${C.ink}">COUNTER</text>`;
  if (kind === 'table') room += `<rect x="${w / 2 - 60}" y="${h / 2 - 22}" width="120" height="44" rx="4" fill="#e8e2d2" stroke="${C.ink}" stroke-width="2"/><text x="${w / 2}" y="${h / 2 + 3}" text-anchor="middle" font-family="DM Mono" font-size="8" fill="${C.ink}">TABLE</text>`;
  if (kind === 'window') room += `<rect x="${w / 2 - 50}" y="2" width="100" height="8" fill="#bfeaff" stroke="${C.ink}" stroke-width="2"/><text x="${w / 2}" y="22" text-anchor="middle" font-family="DM Mono" font-size="8" fill="${C.ink}">WINDOW</text><rect x="${w / 2 - 54}" y="${h - 36}" width="108" height="10" rx="3" fill="#e8e2d2" stroke="${C.ink}" stroke-width="1.6"/><text x="${w / 2}" y="${h - 28}" text-anchor="middle" font-family="DM Mono" font-size="7" fill="${C.ink}">BENCH</text>`;
  const camEl = cams.map((c) => {
    const a = c.ang ?? 0;
    return `<g transform="translate(${c.x},${c.y}) rotate(${a})"><path d="M0,0 L-30,-46 L30,-46Z" fill="${C.Y}" opacity="0.45"/><path d="M0,0 L-30,-46 M0,0 L30,-46" stroke="${C.ink}" stroke-width="1" stroke-dasharray="3 3"/><rect x="-8" y="-5" width="16" height="11" rx="2.5" fill="${C.ink}"/><rect x="-4" y="-9" width="8" height="5" rx="1" fill="${C.ink}"/><text x="0" y="19" text-anchor="middle" transform="rotate(${-a} 0 19)" font-family="DM Mono" font-size="8" font-weight="500" fill="${C.ink}">${esc(c.label || 'A')}</text></g>`;
  }).join('');
  const actEl = actors.map((a) => `<g><circle cx="${a.x}" cy="${a.y}" r="8" fill="${a.col || C.skin[1]}" stroke="${C.ink}" stroke-width="1.8"/><text x="${a.x}" y="${a.y + 19}" text-anchor="middle" font-family="DM Sans" font-weight="700" font-size="8.5" fill="${C.ink}">${esc(a.label)}</text></g>`).join('');
  const ltEl = lights.map((l) => `<g transform="translate(${l.x},${l.y})"><circle r="7" fill="#fff" stroke="${C.ink}" stroke-width="1.8"/>${Array.from({ length: 8 }, (_, i) => { const t = (i / 8) * Math.PI * 2; return `<line x1="${f(Math.cos(t) * 9)}" y1="${f(Math.sin(t) * 9)}" x2="${f(Math.cos(t) * 12)}" y2="${f(Math.sin(t) * 12)}" stroke="${C.ink}" stroke-width="1.4"/>`; }).join('')}<text y="23" text-anchor="middle" font-family="DM Mono" font-size="7.5" fill="${C.ink}">${esc(l.label || 'KEY')}</text></g>`).join('');
  const itEl = items.map((i) => `<g><rect x="${i.x}" y="${i.y}" width="${i.w || 22}" height="${i.h || 14}" rx="3" fill="${i.fill || '#fff'}" stroke="${C.ink}" stroke-width="1.6"/><text x="${i.x + (i.w || 22) / 2}" y="${i.y + (i.h || 14) / 2 + 3}" text-anchor="middle" font-family="DM Mono" font-size="7" fill="${C.ink}">${esc(i.label)}</text></g>`).join('');
  return `<svg viewBox="0 0 ${w} ${h}" xmlns="http://www.w3.org/2000/svg" class="plan">${room}${itEl}${ltEl}${camEl}${actEl}${label ? `<text x="10" y="${h - 8}" text-anchor="start" font-family="DM Mono" font-size="7.5" fill="${C.grey}">${esc(label)}</text>` : ''}</svg>`;
}
