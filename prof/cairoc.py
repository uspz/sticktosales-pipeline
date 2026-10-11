"""Wrapper minimo do cairo (libcairo.so.2) via ctypes: desenho vetorial com anti-aliasing."""
import ctypes as C
import numpy as np

_lib = C.CDLL('libcairo.so.2')
D = C.c_double; I = C.c_int; P = C.c_void_p; S = C.c_char_p


class TextExtents(C.Structure):
    _fields_ = [('x_bearing', D), ('y_bearing', D), ('width', D), ('height', D),
                ('x_advance', D), ('y_advance', D)]


def _f(name, res, *args):
    fn = getattr(_lib, name)
    fn.restype = res
    fn.argtypes = list(args)
    return fn


_create_for_data = _f('cairo_image_surface_create_for_data', P, P, I, I, I, I)
_create = _f('cairo_create', P, P)
_destroy = _f('cairo_destroy', None, P)
_surf_destroy = _f('cairo_surface_destroy', None, P)
_flush = _f('cairo_surface_flush', None, P)
_rgba = _f('cairo_set_source_rgba', None, P, D, D, D, D)
_lw = _f('cairo_set_line_width', None, P, D)
_cap = _f('cairo_set_line_cap', None, P, I)
_join = _f('cairo_set_line_join', None, P, I)
_move = _f('cairo_move_to', None, P, D, D)
_line = _f('cairo_line_to', None, P, D, D)
_curve = _f('cairo_curve_to', None, P, D, D, D, D, D, D)
_arc = _f('cairo_arc', None, P, D, D, D, D, D)
_close = _f('cairo_close_path', None, P)
_newp = _f('cairo_new_path', None, P)
_newsub = _f('cairo_new_sub_path', None, P)
_stroke = _f('cairo_stroke', None, P)
_stroke_p = _f('cairo_stroke_preserve', None, P)
_fill = _f('cairo_fill', None, P)
_fill_p = _f('cairo_fill_preserve', None, P)
_paint = _f('cairo_paint', None, P)
_paint_a = _f('cairo_paint_with_alpha', None, P, D)
_save = _f('cairo_save', None, P)
_restore = _f('cairo_restore', None, P)
_translate = _f('cairo_translate', None, P, D, D)
_scale = _f('cairo_scale', None, P, D, D)
_rotate = _f('cairo_rotate', None, P, D)
_rect = _f('cairo_rectangle', None, P, D, D, D, D)
_clip = _f('cairo_clip', None, P)
_reset_clip = _f('cairo_reset_clip', None, P)
_font = _f('cairo_select_font_face', None, P, S, I, I)
_fsize = _f('cairo_set_font_size', None, P, D)
_show = _f('cairo_show_text', None, P, S)
_tpath = _f('cairo_text_path', None, P, S)
_text_ext = _f('cairo_text_extents', None, P, S, C.POINTER(TextExtents))
_push = _f('cairo_push_group', None, P)
_pop_src = _f('cairo_pop_group_to_source', None, P)
_lin = _f('cairo_pattern_create_linear', P, D, D, D, D)
_rad = _f('cairo_pattern_create_radial', P, D, D, D, D, D, D)
_stop = _f('cairo_pattern_add_color_stop_rgba', None, P, D, D, D, D, D)
_set_src = _f('cairo_set_source', None, P, P)
_pat_destroy = _f('cairo_pattern_destroy', None, P)
_dash = _f('cairo_set_dash', None, P, C.POINTER(D), I, D)

FORMAT_RGB24 = 1
CAP_ROUND = 1
JOIN_ROUND = 1


def hexrgb(h):
    h = h.lstrip('#')
    if len(h) == 3: h = ''.join(ch * 2 for ch in h)
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


class Canvas:
    """Superficie RGB24 sobre um array numpy (H, W, 4) em ordem B,G,R,X."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.buf = np.zeros((h, w, 4), np.uint8)
        self.surf = _create_for_data(self.buf.ctypes.data, FORMAT_RGB24, w, h, w * 4)
        self.cr = _create(self.surf)
        _cap(self.cr, CAP_ROUND)
        _join(self.cr, JOIN_ROUND)

    # ---- estado ----
    def save(self): _save(self.cr)
    def restore(self): _restore(self.cr)
    def translate(self, x, y): _translate(self.cr, x, y)
    def scale(self, sx, sy=None): _scale(self.cr, sx, sx if sy is None else sy)
    def rotate(self, a): _rotate(self.cr, a)

    def color(self, c, a=1.0):
        if isinstance(c, str): c = hexrgb(c)
        _rgba(self.cr, c[0], c[1], c[2], a)

    def lw(self, w): _lw(self.cr, w)

    def dash(self, pattern=None, offset=0.0):
        if not pattern:
            _dash(self.cr, None, 0, 0.0)
        else:
            arr = (D * len(pattern))(*pattern)
            _dash(self.cr, arr, len(pattern), offset)

    # ---- caminhos ----
    def new_path(self): _newp(self.cr)
    def move(self, x, y): _move(self.cr, x, y)
    def line(self, x, y): _line(self.cr, x, y)
    def curve(self, x1, y1, x2, y2, x3, y3): _curve(self.cr, x1, y1, x2, y2, x3, y3)
    def close(self): _close(self.cr)
    def arc(self, x, y, r, a1=0.0, a2=6.283185307179586):
        _newsub(self.cr); _arc(self.cr, x, y, r, a1, a2)
    def rect(self, x, y, w, h): _rect(self.cr, x, y, w, h)

    def rrect(self, x, y, w, h, r):
        r = min(r, w / 2, h / 2)
        _newsub(self.cr)
        _arc(self.cr, x + w - r, y + r, r, -1.5707963, 0)
        _arc(self.cr, x + w - r, y + h - r, r, 0, 1.5707963)
        _arc(self.cr, x + r, y + h - r, r, 1.5707963, 3.14159265)
        _arc(self.cr, x + r, y + r, r, 3.14159265, 4.71238898)
        _close(self.cr)

    def stroke(self, preserve=False): (_stroke_p if preserve else _stroke)(self.cr)
    def fill(self, preserve=False): (_fill_p if preserve else _fill)(self.cr)
    def paint(self, alpha=None):
        if alpha is None: _paint(self.cr)
        else: _paint_a(self.cr, alpha)
    def clip(self): _clip(self.cr)
    def reset_clip(self): _reset_clip(self.cr)

    def polyline(self, pts):
        if not pts: return
        self.move(*pts[0])
        for p in pts[1:]: self.line(*p)

    def smooth(self, pts, tension=0.5):
        """Curva Catmull-Rom passando por todos os pontos (convertida em Bezier)."""
        n = len(pts)
        if n < 2: return
        self.move(*pts[0])
        if n == 2:
            self.line(*pts[1]); return
        for i in range(n - 1):
            p0 = pts[i - 1] if i > 0 else pts[i]
            p1 = pts[i]; p2 = pts[i + 1]
            p3 = pts[i + 2] if i + 2 < n else pts[i + 1]
            k = tension / 3.0 * 2
            c1 = (p1[0] + (p2[0] - p0[0]) * k / 2, p1[1] + (p2[1] - p0[1]) * k / 2)
            c2 = (p2[0] - (p3[0] - p1[0]) * k / 2, p2[1] - (p3[1] - p1[1]) * k / 2)
            self.curve(c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])

    # ---- gradientes ----
    def linear(self, x0, y0, x1, y1, stops):
        pat = _lin(x0, y0, x1, y1)
        for off, c, a in stops:
            c = hexrgb(c) if isinstance(c, str) else c
            _stop(pat, off, c[0], c[1], c[2], a)
        _set_src(self.cr, pat); _pat_destroy(pat)

    def radial(self, cx, cy, r0, r1, stops):
        pat = _rad(cx, cy, r0, cx, cy, r1)
        for off, c, a in stops:
            c = hexrgb(c) if isinstance(c, str) else c
            _stop(pat, off, c[0], c[1], c[2], a)
        _set_src(self.cr, pat); _pat_destroy(pat)

    # ---- grupos (transparencia de um conjunto) ----
    def push(self): _push(self.cr)
    def pop_paint(self, alpha):
        _pop_src(self.cr); _paint_a(self.cr, alpha)

    # ---- texto ----
    def font(self, family, size, bold=True):
        _font(self.cr, family.encode(), 0, 1 if bold else 0)
        _fsize(self.cr, size)

    def extents(self, txt):
        e = TextExtents()
        _text_ext(self.cr, txt.encode('utf-8'), C.byref(e))
        return e

    def text(self, x, y, txt):
        self.move(x, y); _show(self.cr, txt.encode('utf-8'))

    def text_path(self, x, y, txt):
        self.move(x, y); _tpath(self.cr, txt.encode('utf-8'))

    # ---- saida ----
    def clear(self, c):
        self.save(); self.color(c); self.paint(); self.restore()

    def rgb(self):
        _flush(self.surf)
        return self.buf[:, :, 2::-1].copy()

    def bgr0_bytes(self):
        _flush(self.surf)
        return self.buf.tobytes()

    def close_canvas(self):
        _destroy(self.cr); _surf_destroy(self.surf)
