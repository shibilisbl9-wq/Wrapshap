"""Photo-style mockups of the t-shirt collection: flat-lay shirts in soft studio light (Blender Cycles).

Each shirt is a 3D surface built from a height map: rounded edges, body volume, soft folds, a raised
rib collar, stitched hems, shoulder and armhole seams. The print files (the exact placed PDFs from the
collection) are mapped onto that surface, so the artwork follows the folds and takes the same light,
sheen and knit texture as the fabric. Nothing in the artwork is redrawn.

  python3 photo_mockup.py            -> mockup/photo-d<N>[-<view>].jpg and mockup/photo-collection.jpg
  python3 photo_mockup.py quick d2   -> fast low-res test render of one design
"""
import os, sys, time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
from scipy.spatial import cKDTree
from shapely.geometry import Polygon
import pymupdf as fitz
from collection_mockup import DESIGNS

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.abspath(os.path.join(HERE, '..', 'fonts'))
MAPS = os.path.join(HERE, 'photo', 'maps')
OUT = os.path.join(HERE, 'mockup')
K = 4                                         # texture px per mm
X0, X1, Y0, Y1 = -460, 460, -30, 790          # garment frame, mm: x from the centre line, y down from the shoulder line
TW, TH = (X1 - X0) * K, (Y1 - Y0) * K
SHIRT = {'black': '#141416', 'white': '#EFEFEC', 'cream': '#EBE3CF', 'orange': '#F39200'}
BACKDROP = '#C9C7C2'
NAMES = [d[1] for d in DESIGNS]


# ---- garment geometry (mm) ----------------------------------------------------------------------
def bez(p0, p1, p2, p3, n=48):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2, p3 = map(np.asarray, (p0, p1, p2, p3))
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3


BACK_NECK = bez((-95, 0), (-90, 26), (90, 26), (95, 0))
FRONT_NECK = bez((-95, 0), (-95, 118), (95, 118), (95, 0))
HEM = bez((294, 742), (150, 748), (-150, 748), (-294, 742))
R = [(95, 0), (262, 30), (430, 205), (340, 300), (290, 256), (294, 742)]   # neck, shoulder, sleeve tip, sleeve under, armpit, hem


def outline():
    right = R[:5] + [(292, 500)]
    left = [(-x, y) for x, y in right][::-1]
    pts = right + [tuple(p) for p in HEM] + left + [tuple(p) for p in BACK_NECK[1:-1]]
    poly = Polygon(pts).buffer(0)
    poly = poly.buffer(-5, join_style='round').buffer(5, join_style='round')     # soften outer corners
    poly = poly.buffer(14, join_style='round').buffer(-14, join_style='round')    # and the underarm
    P, _, _ = along(list(poly.exterior.coords), 1.0)
    dv = np.gradient(P, axis=0)
    n = np.stack([dv[:, 1], -dv[:, 0]], 1) / (np.hypot(*dv.T)[:, None] + 1e-9)
    wav = ndimage.gaussian_filter1d(np.random.default_rng(3).normal(size=len(P)), 45, mode='wrap')
    wav *= 2.2 / (np.abs(wav).max() + 1e-9)
    wav *= 1 - smoothstep(0, 1, np.clip((70 - P[:, 1]) / 40, 0, 1)) * (np.abs(P[:, 0]) < 140)
    return Polygon(P + n * wav[:, None]).buffer(0)


def rasterize(polys, scale=K, ss=2):
    """Antialiased mask of shapely polygons on the texture grid (scale px/mm)."""
    w, h = (X1 - X0) * scale * ss, (Y1 - Y0) * scale * ss
    im = Image.new('L', (w, h), 0)
    dr = ImageDraw.Draw(im)
    for p in polys:
        for g in getattr(p, 'geoms', [p]):
            dr.polygon([((x - X0) * scale * ss, (y - Y0) * scale * ss) for x, y in g.exterior.coords], fill=255)
            for hole in g.interiors:
                dr.polygon([((x - X0) * scale * ss, (y - Y0) * scale * ss) for x, y in hole.coords], fill=0)
    return np.asarray(im.resize((w // ss, h // ss), Image.LANCZOS), np.float32) / 255


def grid(scale):
    ys, xs = np.mgrid[0:(Y1 - Y0) * scale, 0:(X1 - X0) * scale].astype(np.float32)
    return X0 + (xs + 0.5) / scale, Y0 + (ys + 0.5) / scale


def along(pts, step=0.5):
    """Resample a polyline every `step` mm; returns points and their normalised position 0..1."""
    P = np.asarray(pts, float)
    s = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(P, axis=0).T))])
    ss = np.arange(0, s[-1], step)
    Q = np.stack([np.interp(ss, s, P[:, 0]), np.interp(ss, s, P[:, 1])], 1)
    return Q, ss / max(s[-1], 1e-6), ss


def dist_to(pts, X, Y, reach):
    """Distance (mm) from every grid point to a polyline, plus the polyline position (0..1) of the nearest point."""
    Q, t, _ = along(pts)
    d, i = cKDTree(Q).query(np.stack([X.ravel(), Y.ravel()], 1), distance_upper_bound=reach)
    d = d.reshape(X.shape)
    i = np.minimum(i, len(t) - 1).reshape(X.shape)
    return np.where(np.isfinite(d), d, reach), t[i]


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def ridged(shape, sigma, seed):
    """Crease-like field: sharp crests, soft troughs, zero mean."""
    r = 1 - np.abs(noise(shape, sigma, seed))
    return (r - r.mean()) / (r.std() + 1e-9)


def noise(shape, sigma, seed):
    n = ndimage.gaussian_filter(np.random.default_rng(seed).normal(size=shape).astype(np.float32), sigma)
    return n / (n.std() + 1e-9)


# folds: polyline (mm), amplitude (mm, + ridge / - valley), half width (mm). Kept soft over the print areas.
FOLDS = [
    # underarm drapes
    ([(-288, 262), (-230, 330), (-170, 400)], -3.2, 14), ([(292, 262), (236, 326), (182, 392)], -2.8, 13),
    ([(-300, 285), (-250, 380), (-215, 470)], 2.4, 20), ([(300, 290), (262, 370), (238, 450)], 2.0, 22),
    ([(-282, 300), (-268, 420), (-262, 560)], -1.4, 12), ([(286, 470), (276, 560), (272, 660)], -1.3, 12),
    # sleeves
    ([(-262, 40), (-330, 120), (-390, 200)], 2.6, 24), ([(262, 40), (336, 126), (392, 196)], 2.3, 26),
    ([(-305, 170), (-360, 250)], -1.8, 10), ([(318, 160), (372, 238)], -1.6, 10),
    ([(-296, 214), (-338, 262)], 1.4, 8), ([(300, 206), (346, 250)], 1.3, 8),
    ([(-352, 110), (-392, 150)], -1.2, 7), ([(356, 104), (400, 146)], -1.1, 7),
    # hem
    ([(-270, 650), (-120, 675), (40, 668)], 2.2, 26), ([(-200, 704), (0, 714), (180, 700)], -1.6, 18),
    ([(120, 610), (230, 640), (285, 690)], 1.8, 22),
    ([(-250, 742), (-238, 700)], -1.2, 7), ([(-150, 746), (-140, 712)], 1.0, 7), ([(212, 742), (224, 704)], -1.1, 7),
    # torso, outside the print areas
    ([(-240, 520), (-190, 600), (-120, 640)], 1.3, 30), ([(170, 470), (210, 560)], -1.0, 20),
    # collar
    ([(-150, 40), (-120, 120)], 0.9, 16), ([(150, 38), (126, 110)], 0.8, 16),
]

def build_maps(di, view, key):
    """Height map (1 mm grid) and texture maps (K px/mm) for design di (0-based), view 'front'/'back'."""
    shirt, name, views = DESIGNS[di]
    prints = dict((v[0], v[1]) for v in views)[view]
    body = outline()
    front = view == 'front'
    label = Polygon([(222, 736), (242, 736), (242, 752), (222, 752)]).buffer(1.2) if front else None
    garment = body.union(label) if label else body
    inner = Polygon(np.vstack([BACK_NECK, FRONT_NECK[::-1]])).buffer(0) if front else None

    # --- height (mm), 1 mm grid
    X, Y = grid(1)
    m1 = rasterize([garment], 1, 4)
    d = ndimage.distance_transform_edt(m1 > 0.5)
    h = 1.2 + 2.1 * (1 - np.exp(-d / 4)) + 7.0 * smoothstep(8, 180, d)
    edge = 0.35 + 0.65 * smoothstep(0, 30, d)
    for pts, amp, w in FOLDS:
        dd, t = dist_to(pts, X, Y, 4 * w)
        h += 3.0 * amp * edge * np.exp(-0.5 * (dd / w) ** 2) * np.sin(np.pi * np.clip(t, 0, 1)) ** 0.7
    h += 0.35 * noise(h.shape, 60, 1) + 0.12 * noise(h.shape, 8, 2)
    # fine creases: ridged noise, mostly running down the body, across it near the hem
    hem_w = smoothstep(560, 700, Y)
    h += edge * (0.75 * (1 - hem_w) * ridged(h.shape, (30, 9), 11) + 0.8 * hem_w * ridged(h.shape, (7, 26), 12)
                 + 0.4 * ridged(h.shape, (14, 14), 13))
    # collar
    db, _ = dist_to(BACK_NECK, X, Y, 60)
    if front:
        df, _ = dist_to(FRONT_NECK, X, Y, 60)
        mi = rasterize([inner], 1, 4)
        h -= 2.4 * mi * smoothstep(0, 6, df)                                   # inside of the back, one layer
        h += 0.9 * mi * np.clip(1 - db / 15, 0, 1) ** 0.5                      # back rib, seen from inside
        band = (1 - mi) * np.clip(1 - df / 18, 0, 1)
        h += 1.5 * np.sin(np.pi * np.clip(df / 18, 0, 1)) ** 0.6 * (band > 0)  # front rib band
    else:
        band = np.clip(1 - db / 18, 0, 1) * (m1 > 0.5)
        h += 1.4 * np.sin(np.pi * np.clip(db / 18, 0, 1)) ** 0.6 * (band > 0)
    # hems and seams
    dh, _ = dist_to(HEM, X, Y, 40)
    sleeve = [(R[2], R[3]), ((-R[2][0], R[2][1]), (-R[3][0], R[3][1]))]
    h += 0.5 * np.exp(-0.5 * ((dh - 12) / 6) ** 2) - 0.35 * np.exp(-0.5 * ((dh - 24) / 1.2) ** 2)
    for a, b in sleeve:
        ds, _ = dist_to([a, b], X, Y, 40)
        h += 0.5 * np.exp(-0.5 * ((ds - 12) / 6) ** 2) - 0.35 * np.exp(-0.5 * ((ds - 24) / 1.2) ** 2)
    seams = []
    for s in (1, -1):
        seams += [[(s * 95, 0), (s * 262, 30)], [(s * 262, 30), (s * 276, 140), (s * 290, 256)]]
    for pts in seams:
        dd, _ = dist_to(pts, X, Y, 12)
        h += 0.55 * np.exp(-0.5 * (dd / 1.6) ** 2)
    if label:
        ml = rasterize([label], 1, 4)
        h = h * (1 - ml) + (np.maximum(h, 3.2) + 0.6) * ml
    h = np.where(m1 > 0.02, np.maximum(h, 0.8), 0).astype(np.float32)

    # --- textures, K px/mm
    Xk, Yk = grid(K)
    mask = rasterize([garment], K, 2)
    base = np.array([int(SHIRT[shirt][i:i + 2], 16) / 255 for i in (1, 3, 5)], np.float32)
    alb = np.ones((TH, TW, 3), np.float32) * base
    heather = 1 + 0.006 * noise((TH, TW), 40, 3) + 0.015 * noise((TH, TW), 1.2, 4)
    alb *= heather[..., None]
    detail = 0.3 * noise((TH, TW), 1.6, 5) + 0.2 * noise((TH, TW), 0.7, 6)      # knit grain
    # rib stripes on collar bands (run across the band)
    bands = []
    if front:
        mik = rasterize([inner], K, 2)
        dfk, tf = dist_to(FRONT_NECK, Xk, Yk, 20)
        bands.append(((1 - mik) * (dfk < 18), tf, 280))
        alb *= (1 - 0.18 * mik * smoothstep(0, 30, dfk))[..., None]           # the inside sits in shadow of its own
    dbk, tb = dist_to(BACK_NECK, Xk, Yk, 20)
    bands.append(((dbk < (15 if front else 18)) * (mask > 0.5), tb, 230))
    for m, t, L in bands:
        detail += m * 0.9 * np.sin(2 * np.pi * t * L / 1.3)
    # stitches: double needle 1.5 mm from the band edges, dashes 2.4 mm every 3 mm
    thread = Image.new('L', (TW, TH), 0)
    dr = ImageDraw.Draw(thread)

    def stitch(pts, offset):
        Q, _, s = along(pts, 0.25)
        dv = np.gradient(Q, axis=0)
        n = np.stack([-dv[:, 1], dv[:, 0]], 1) / (np.hypot(*dv.T)[:, None] + 1e-9)
        Q = Q + n * offset
        on = (s % 3.0) < 2.4
        for a, b, o in zip(Q[:-1], Q[1:], on[:-1]):
            if o:
                dr.line([((a[0] - X0) * K, (a[1] - Y0) * K), ((b[0] - X0) * K, (b[1] - Y0) * K)], fill=255, width=2)
    for off in (22, 25.5):                                                     # hem (inward normal points up)
        stitch(HEM[::-1], off)
    for a, b in sleeve:
        for off in (22, 25.5):
            stitch([b, a] if a[0] > 0 else [a, b], off)
    neck = FRONT_NECK if front else BACK_NECK
    for off in (19, 22):
        stitch(neck[::-1], -off)
    for pts in seams:
        stitch(pts, 2.2 if pts[0][0] >= 0 else -2.2)
    th = np.asarray(thread, np.float32) / 255
    th = ndimage.gaussian_filter(th, 0.6)
    detail -= 1.6 * th
    tone = 1.35 if base.mean() < 0.3 else 0.86
    alb *= (1 + (tone - 1) * np.clip(th * 1.4, 0, 1))[..., None]

    # prints: exact placed artwork at K px/mm
    ink = np.zeros((TH, TW), np.float32)

    def place(name, x, y, anchor='c', clip=None):
        pg = fitz.open(os.path.join(HERE, 'placed', name + '.pdf'))[0]
        pix = pg.get_pixmap(matrix=fitz.Matrix(K * 25.4 / 72, K * 25.4 / 72), alpha=True, clip=clip)
        a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 4).astype(np.float32) / 255
        wmm = pix.width / K
        left = x - wmm / 2 if anchor == 'c' else x
        c0, r0 = int(round((left - X0) * K)), int(round((y - Y0) * K))
        r1, c1 = min(TH, r0 + pix.height), min(TW, c0 + pix.width)
        a = a[:r1 - r0, :c1 - c0]
        rgb, al = a[..., :3], a[..., 3:4]
        rgb = rgb * (1 - 0.05 * np.clip(noise(al.shape[:2], 0.7, 9), -2, 2))[..., None]     # ink takes the knit
        alb[r0:r1, c0:c1] = alb[r0:r1, c0:c1] * (1 - al) + rgb * al
        ink[r0:r1, c0:c1] = np.maximum(ink[r0:r1, c0:c1], al[..., 0])
    for n, x, y, anchor in prints:
        place(n, x, y, anchor)
    if front:
        if shirt == 'black':
            place('tee-black-neck', 0, 30)
        place('tee-label', 232, 736, clip=fitz.Rect(0, 16 * 72 / 25.4, 20 * 72 / 25.4, 32 * 72 / 25.4))
    detail *= (1 - 0.75 * ink)

    os.makedirs(MAPS, exist_ok=True)
    p = lambda s: os.path.join(MAPS, f'{key}-{s}')
    Image.fromarray((np.clip(alb, 0, 1) * 255 + 0.5).astype(np.uint8)).save(p('albedo.png'))
    Image.fromarray((mask * 255 + 0.5).astype(np.uint8)).save(p('mask.png'))
    Image.fromarray((ink * 255 + 0.5).astype(np.uint8)).save(p('ink.png'))
    dn = (detail - detail.min()) / (detail.max() - detail.min())
    Image.fromarray((dn * 65535).astype(np.uint16)).save(p('detail.png'))
    np.save(p('height.npy'), h)
    return dict(albedo=p('albedo.png'), mask=p('mask.png'), ink=p('ink.png'), detail=p('detail.png'), height=h)


# ---- Blender scene --------------------------------------------------------------------------------------
def srgb_to_lin(c):
    c = np.asarray(c, float)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def hexlin(hexv):
    return tuple(srgb_to_lin([int(hexv[i:i + 2], 16) / 255 for i in (1, 3, 5)])) + (1.0,)


def garment_mesh(bpy, maps, name, ox, step):
    """Height-field mesh over the garment, in metres; UVs map straight onto the texture maps."""
    h = maps['height'][::step, ::step]
    ny, nx = h.shape
    xs = (X0 + (np.arange(nx) * step + 0.5)) / 1000
    ys = (Y0 + (np.arange(ny) * step + 0.5)) / 1000
    keep_v = ndimage.binary_dilation(h > 0, iterations=2)
    idx = -np.ones((ny, nx), np.int64)
    idx[keep_v] = np.arange(keep_v.sum())
    XX, YY = np.meshgrid(xs, ys)
    verts = np.stack([XX[keep_v] + ox, -YY[keep_v], h[keep_v] / 1000], 1)
    a, b, c, d = idx[:-1, :-1], idx[:-1, 1:], idx[1:, 1:], idx[1:, :-1]
    ok = (a >= 0) & (b >= 0) & (c >= 0) & (d >= 0)
    faces = np.stack([a[ok], d[ok], c[ok], b[ok]], 1)
    me = bpy.data.meshes.new(name)
    me.vertices.add(len(verts))
    me.vertices.foreach_set('co', verts.astype(np.float32).ravel())
    me.loops.add(faces.size)
    me.loops.foreach_set('vertex_index', faces.astype(np.int32).ravel())
    me.polygons.add(len(faces))
    me.polygons.foreach_set('loop_start', (np.arange(len(faces)) * 4).astype(np.int32))
    me.polygons.foreach_set('use_smooth', np.ones(len(faces), bool))
    uv = me.uv_layers.new(name='UV')
    vx, vy = XX[keep_v], YY[keep_v]
    u = (vx * 1000 - X0) / (X1 - X0)
    v = 1 - (vy * 1000 - Y0) / (Y1 - Y0)
    uvv = np.stack([u, v], 1)[faces.ravel()]
    uv.data.foreach_set('uv', uvv.astype(np.float32).ravel())
    me.validate()
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.append(fabric(bpy, maps, name))
    return ob


def fabric(bpy, maps, name):
    mat = bpy.data.materials.new(name + '-fabric')
    mat.use_nodes = True
    nt = mat.node_tree
    N, L = nt.nodes, nt.links
    bsdf = N['Principled BSDF']

    def tex(path, colour):
        n = N.new('ShaderNodeTexImage')
        n.image = bpy.data.images.load(path)
        n.image.colorspace_settings.name = 'sRGB' if colour else 'Non-Color'
        n.interpolation = 'Cubic'
        return n
    alb, msk, ink, det = tex(maps['albedo'], True), tex(maps['mask'], False), tex(maps['ink'], False), tex(maps['detail'], False)
    L.new(alb.outputs['Color'], bsdf.inputs['Base Color'])
    L.new(msk.outputs['Color'], bsdf.inputs['Alpha'])

    def mix(a, b):
        m = N.new('ShaderNodeMix')
        m.data_type = 'FLOAT'
        L.new(ink.outputs['Color'], m.inputs['Factor'])
        m.inputs['A'].default_value, m.inputs['B'].default_value = a, b
        return m.outputs['Result']
    L.new(mix(0.93, 0.8), bsdf.inputs['Roughness'])
    L.new(mix(0.3, 0.04), bsdf.inputs['Sheen Weight'])
    bsdf.inputs['Sheen Roughness'].default_value = 0.35
    bsdf.inputs['Specular IOR Level'].default_value = 0.35
    bump = N.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.55
    bump.inputs['Distance'].default_value = 0.0004
    L.new(det.outputs['Color'], bump.inputs['Height'])
    L.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    return mat


def scene(bpy, garments, frame_w, frame_h, res_x, samples, step, shift=0.0):
    """garments: [(maps, x offset in m)]. Frame in metres, centred on the shirts, moved down by shift."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 6
    sc.view_settings.view_transform = 'Standard'
    sc.view_settings.look = 'None'
    sc.render.resolution_x, sc.render.resolution_y = res_x, round(res_x * frame_h / frame_w)
    sc.render.image_settings.file_format = 'PNG'
    world = bpy.data.worlds.new('w')
    sc.world = world
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.8, 0.8, 0.8, 1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.18
    cx = sum(o for _, o in garments) / len(garments)
    cy = -0.375 - shift
    # backdrop: grey paper
    bpy.ops.mesh.primitive_plane_add(size=1, location=(cx, cy, -0.0003))
    bd = bpy.context.object
    bd.scale = (frame_w * 3, frame_h * 3, 1)
    m = bpy.data.materials.new('paper')
    m.use_nodes = True
    p = m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = hexlin(BACKDROP)
    p.inputs['Roughness'].default_value = 0.95
    p.inputs['Specular IOR Level'].default_value = 0.2
    bd.data.materials.append(m)
    for i, (maps, ox) in enumerate(garments):
        garment_mesh(bpy, maps, f'shirt{i}', ox, step)
    # soft studio light: a strip softbox beyond the top of the frame, a weaker fill from below

    def area(name, loc, size, energy):
        l = bpy.data.lights.new(name, 'AREA')
        l.shape = 'RECTANGLE'
        l.size, l.size_y = size[0], size[1]
        l.energy = energy
        ob = bpy.data.objects.new(name, l)
        ob.location = loc
        sc.collection.objects.link(ob)
        d = np.array((loc[0], cy + shift, 0)) - np.array(loc)
        ob.rotation_euler = mathutils.Vector(d).to_track_quat('-Z', 'Y').to_euler()
    wide = frame_w + 0.6                     # strip lights as wide as the set: even light across a row of shirts

    def strip(L, d):                         # relative light a strip of length L delivers at distance d below its middle
        x = L / 2 / d
        return x / (1 + x * x) + np.arctan(x)
    ref = 1.62                               # the single-shirt set the light level was calibrated on
    area('key', (cx, cy + 1.5, 1.5), (wide, 0.9), KEY * wide * strip(ref, 2.12) / strip(wide, 2.12))
    area('fill', (cx, cy - 1.7, 1.5), (wide, 1.0), 0.2 * KEY * wide * strip(ref, 2.27) / strip(wide, 2.27))
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
    cam.data.lens = 85
    cam.data.sensor_width = 36
    cam.data.sensor_fit = 'HORIZONTAL'
    z = frame_w * 85 / 36
    cam.location = (cx, cy, z)
    sc.collection.objects.link(cam)
    sc.camera = cam
    return sc


def render(garments, out, frame_w, frame_h, res_x, samples, step=1, exposure=0.0, shift=0.0):
    global mathutils
    import bpy, mathutils
    sc = scene(bpy, garments, frame_w, frame_h, res_x, samples, step, shift)
    sc.view_settings.exposure = exposure
    sc.render.filepath = out
    t = time.time()
    bpy.ops.render.render(write_still=True)
    print('rendered', os.path.basename(out), sc.render.resolution_x, sc.render.resolution_y, f'{time.time() - t:.0f}s')


def board(png, out, fw, fh, shift, step_m):
    """Captions under each shirt, like the reference board."""
    im = Image.open(png).convert('RGB')
    W, H = im.size
    ppm = W / fw
    y_of = lambda y_mm: (y_mm / 1000 - (0.375 + shift - fh / 2)) * ppm
    dr = ImageDraw.Draw(im)
    f1 = ImageFont.truetype(os.path.join(FONTS, 'Geist-600.ttf'), round(0.036 * ppm))
    f2 = ImageFont.truetype(os.path.join(FONTS, 'Geist-500.ttf'), round(0.024 * ppm))
    f3 = ImageFont.truetype(os.path.join(FONTS, 'Geist-500.ttf'), round(0.018 * ppm))
    n = len(DESIGNS)
    for i, (_, name, _) in enumerate(DESIGNS):
        x = W / 2 + (i - (n - 1) / 2) * step_m * ppm
        dr.text((x, y_of(850)), f'DESIGN {i + 1}', font=f1, fill='#2A2926', anchor='mm')
        dr.text((x, y_of(905)), ' '.join(name.upper()), font=f2, fill='#55524C', anchor='mm')
    m = 0.06 * ppm
    dr.text((m, y_of(-95)), ' '.join('WRAPSHAP — T-SHIRT COLLECTION'), font=f3, fill='#6E6B64', anchor='lm')
    dr.text((W - m, y_of(-95)), ' '.join('SIZE L · PRINTS AT 100%'), font=f3, fill='#6E6B64', anchor='rm')
    im.save(out, quality=92, optimize=True)
    print('board', out, im.size)


SINGLES = [(0, 'back'), (0, 'front'), (1, 'back'), (2, 'front'), (3, 'back'), (4, 'front'), (5, 'back')]
EXPOSURE = 0.0
KEY = 33

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    args = sys.argv[1:]
    if args and args[0] == 'quick':
        di = int(args[1][1:]) - 1
        view = args[2] if len(args) > 2 else DESIGNS[di][2][0][0]
        maps = build_maps(di, view, f'd{di + 1}-{view}')
        render([(maps, 0)], os.path.join(OUT, f'quick-d{di + 1}-{view}.png'), 1.02, 0.98, 700, 24, 2, EXPOSURE)
        sys.exit()
    maps = {}
    for di, view in SINGLES:
        maps[di, view] = build_maps(di, view, f'd{di + 1}-{view}')
        print('maps', di + 1, view)
    for di, view in SINGLES:
        png = os.path.join(OUT, f'photo-d{di + 1}-{view}.png')
        render([(maps[di, view], 0)], png, 1.02, 0.98, 2400, 48, 1, EXPOSURE)
        Image.open(png).convert('RGB').save(png[:-4] + '.jpg', quality=92, optimize=True)
    # the collection in one shot: six shirts, one set, one light
    step_m, n = 1.0, len(DESIGNS)
    row = [(maps[di, DESIGNS[di][2][0][0]], (di - (n - 1) / 2) * step_m) for di in range(n)]
    fw, fh, shift = n * step_m + 0.2, 1.2, 0.1
    png = os.path.join(OUT, 'photo-collection.png')
    render(row, png, fw, fh, 7200, 40, 2, EXPOSURE, shift)
    board(png, os.path.join(OUT, 'photo-collection.jpg'), fw, fh, shift, step_m)
