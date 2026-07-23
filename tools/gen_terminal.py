#!/usr/bin/env python3
"""Generator for veloxy profile terminal.svg — edit constants, rerun.

Transparent, theme-adaptive (prefers-color-scheme). One-time replay:
  0.4s-1.1s  type "neofetch"
  1.4s       neofetch output appears (cube + info)
  1.7s       second prompt appears
  2.0s-4.0s  type "http get https://sourcebox.be"
  4.3s       final prompt appears, cursor blinks forever
"""
import json, os

SP = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(f'{SP}/glyphs.json'))

CW = 8.4; X0 = 24; INFO_X = 270; LH = 21

# theme-independent (colored caps + their dark icons)
INK = '#171221'
PINKC, PURC, GRNC, CYAC = '#ff5fd7', '#a78bff', '#5fff87', '#5fe7e7'

# class -> (light, dark) fills; dark = Ada ghostty palette
THEME = {
    'fg':   ('#1f2328', '#e6edf3'),   # Primer fg
    'mut':  ('#656d76', '#7d8590'),   # Primer muted
    'pink': ('#d61f9c', '#ff5fd7'),
    'pur':  ('#7c53f4', '#a78bff'),
    'pur2': ('#6f3ff5', '#875fff'),
    'grn':  ('#0f9d45', '#5fff87'),
    'orn':  ('#d97706', '#ffaf5f'),
    'cya':  ('#0e9494', '#5fe7e7'),
    'yel':  ('#b58a00', '#ffe787'),
    'pill': ('#f6f8fa', '#21262d'),   # Primer canvas subtle
}

CUBE = 'M78.549 28.899L54 14.725a8 8 0 0 0-8 0L21.451 28.899a8 8 0 0 0-4 6.928v28.348a8.003 8.003 0 0 0 4 6.929L46 85.275a8.001 8.001 0 0 0 8 0l24.549-14.172c2.475-1.43 4-4.07 4-6.929V35.827a8.002 8.002 0 0 0-4-6.928zM50 21.653l20.549 11.865-20.547 11.863-20.551-11.863L50 21.653zM25.451 64.175V40.446L46 52.31v23.728L25.451 64.175zM54 76.037V52.311l20.549-11.863v23.728L54 76.037z'

def esc(s): return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def style_block():
    light = '\n'.join(f'    .{k}{{fill:{v[0]}}}' for k, v in THEME.items())
    dark = '\n'.join(f'      .{k}{{fill:{v[1]}}}' for k, v in THEME.items())
    return (f'  <style>\n{light}\n'
            f'    .conn{{stroke:{THEME["mut"][0]}}}\n'
            f'    @media (prefers-color-scheme: dark) {{\n{dark}\n'
            f'      .conn{{stroke:{THEME["mut"][1]}}}\n'
            f'    }}\n  </style>')

def glyph_icon(key, cap_x, cap_cy, target, color):
    g = G[key]
    x0,y0,x1,y1 = g['bounds']
    w, h = x1-x0, y1-y0
    s = target / max(w, h)
    tx = cap_x + 13 - (x0 + w/2)*s
    ty = cap_cy + (y0 + h/2)*s
    return (f'<g transform="translate({tx:.2f} {ty:.2f}) scale({s:.5f} -{s:.5f})">'
            f'<path fill="{color}" d="{g["path"]}"/></g>')

def info_line(y, label, value):
    tl = len(label)*CW
    return (f'    <text x="{INFO_X}" y="{y}"><tspan class="pink" font-weight="bold" '
            f'textLength="{tl:.1f}" lengthAdjust="spacingAndGlyphs">{esc(label)}</tspan>'
            f'<tspan x="{INFO_X + 11*CW:.1f}" class="fg">{esc(value)}</tspan></text>')

def appear(begin):
    return f'<set attributeName="opacity" to="1" begin="{begin}s" fill="freeze"/>'

def typing_clip(cid, x, yc, nchars, begin, dur):
    widths = ';'.join(f'{i*CW:.1f}' for i in range(nchars+1))
    kts = ';'.join(f'{i/nchars:.4f}' for i in range(nchars+1))
    return (f'    <clipPath id="{cid}"><rect x="{x}" y="{yc-14}" height="19" width="0">'
            f'<animate attributeName="width" values="{widths}" keyTimes="{kts}" '
            f'calcMode="discrete" begin="{begin}s" dur="{dur}s" fill="freeze"/></rect></clipPath>')

PSTART = X0 + 16
PH = 18; CAPW = 26; PF = 12; PCW = 7.2

def seg(x, y, cap_color, icon_key, icon_size, label_svg, label_chars):
    lw = label_chars*PCW
    total = CAPW + 8 + lw + 9
    ry = y - 13
    cap_cy = ry + PH/2
    out = []
    out.append(f'    <rect x="{x+13}" y="{ry}" width="{total-13:.0f}" height="{PH}" rx="9" class="pill"/>')
    out.append(f'    <rect x="{x}" y="{ry}" width="{CAPW}" height="{PH}" rx="9" fill="{cap_color}"/>')
    out.append('    ' + glyph_icon(icon_key, x, cap_cy, icon_size, INK))
    out.append(f'    <text x="{x+CAPW+8}" y="{y}" font-size="{PF}">{label_svg}</text>')
    return '\n'.join(out), x + total + 8

def pills_block(yp, yc, cmd_svg, cursor=False, clip=None):
    parts = []
    x = PSTART
    s, x = seg(x, yp, PURC, 'folder', 11, '<tspan class="fg">veloxy</tspan>', 6); parts.append(s)
    git_label = '<tspan class="fg">main</tspan><tspan class="orn"> !2+1</tspan>'
    s, x = seg(x, yp, PINKC, 'branch', 12, git_label, 9); parts.append(s)
    s, x = seg(x, yp, GRNC, 'php', 13, '<tspan class="fg">8.4</tspan>', 3); parts.append(s)
    # agent status: running / completed / blocked / idle
    agents = ('<tspan class="grn">▸2</tspan><tspan class="fg"> ✓4</tspan>'
              '<tspan class="orn"> !1</tspan><tspan class="mut"> ~1</tspan>')
    s, x = seg(x, yp, CYAC, 'robot', 13, agents, 11); parts.append(s)
    # connector: pill left edge -> down -> hooks into arrow mid-height
    parts.append(f'    <path d="M{PSTART-3} {yp-4} h-4 a6 6 0 0 0 -6 6 v{yc-yp-13} a6 6 0 0 0 6 6 h4" '
                 f'class="conn" stroke-width="1.3" fill="none"/>')
    parts.append(f'    <text x="{X0+11}" y="{yc}" class="pur2" font-weight="bold">❯</text>')
    clip_attr = f' clip-path="url(#{clip})"' if clip else ''
    parts.append(f'    <text x="{X0+27}" y="{yc}"{clip_attr}>{cmd_svg}</text>')
    if cursor:
        parts.append(f'    <rect x="{X0+27}" y="{yc-12}" width="2.5" height="15" class="orn">'
                     f'<animate attributeName="opacity" values="1;1;0;0" dur="1.2s" repeatCount="indefinite"/></rect>')
    return '\n'.join(parts)

# content spans y 45..411 after chrome removal
L = []
L.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 45 700 366" font-family="SFMono-Regular, Menlo, Consolas, \'Liberation Mono\', monospace" font-size="14">')
L.append(style_block())
L.append('  <g xml:space="preserve" class="fg">')

L.append(typing_clip('type1', X0+27, 92, len('neofetch'), 0.4, 0.7))
L.append(typing_clip('type2', X0+27, 348, len('http get https://sourcebox.be'), 2.0, 2.0))

# block 1: prompt visible from start, command types at 0.4s
L.append(pills_block(66, 92, '<tspan class="cya">neofetch</tspan>', clip='type1'))

# neofetch output: appears at 1.4s (cube floats forever after)
L.append(f'  <g opacity="0">{appear(1.4)}')
s = 2.4; w = 65.1*s; hh = 72.7*s
tx = 24 + (226 - w)/2 - 17.45*s; ty = 112 + (190 - hh)/2 - 14.725*s
L.append(f'  <g class="pur" transform="translate({tx:.1f} {ty:.1f}) scale({s})"><g>'
         f'<animateTransform attributeName="transform" type="translate" values="0 0; 0 -1.5; 0 0" '
         f'dur="5s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" '
         f'keySplines="0.42 0 0.58 1;0.42 0 0.58 1"/>'
         f'<path d="{CUBE}"/></g></g>')
L.append(f'    <text x="{INFO_X}" y="121"><tspan class="pink" font-weight="bold">veloxy@github</tspan></text>')
L.append(f'    <text x="{INFO_X}" y="142" textLength="{13*CW:.1f}" lengthAdjust="spacingAndGlyphs" class="pink">─────────────</text>')
rows = [("OS:","macOS"),("Uptime:","15+ years on GitHub"),("Shell:","nushell"),
        ("Editor:","PhpStorm"),("Terminal:","Ghostty"),
        ("Languages:","PHP · JS/TS · a long tail of others"),
        ("Locale:","nl_BE.UTF-8 · en_US.UTF-8")]
for i,(lab,val) in enumerate(rows):
    L.append(info_line(163 + i*LH, lab, val))
L.append('  </g>')

# block 2: appears at 1.7s, command types at 2.0s
L.append(f'  <g opacity="0">{appear(1.7)}')
L.append(pills_block(322, 348, '<tspan class="cya">http get</tspan><tspan class="yel"> https://sourcebox.be</tspan>', clip='type2'))
L.append('  </g>')

# block 3: appears at 4.3s, cursor blinks forever
L.append(f'  <g opacity="0">{appear(4.3)}')
L.append(pills_block(376, 400, '', cursor=True))
L.append('  </g>')

L.append('  </g>')
L.append('</svg>')

open(os.path.join(SP, '..', 'terminal.svg'),'w').write('\n'.join(L)+'\n')
print('written terminal.svg')
