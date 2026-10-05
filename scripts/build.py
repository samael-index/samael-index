"""Genera los SVG del perfil en assets/.

Uso:  python scripts/build.py [ruta-avatar.png]
Si no se pasa avatar, descarga https://github.com/samael-index.png
"""
import io
import math
import random
import sys
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageEnhance, ImageOps

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

USER = "samael-index"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

# Paleta Matrix
BG = "#0d1117"
PANEL = "#010409"
BORDER = "#1b4332"
GREEN = "#00ff9c"
GREEN_DIM = "#00b36b"
TEXT = "#c9d1d9"
MUTED = "#6e7681"
CYAN = "#39d0d8"
YELLOW = "#e3b341"
PINK = "#ff6d8a"

random.seed(7)


def window(w, h, title, body):
    """Ventana de terminal con barra de título y tres puntos."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{MONO}">
<style>
  .blink {{ animation: blink 1.1s steps(1) infinite; }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
</style>
<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="12" fill="{BG}" stroke="{BORDER}" stroke-width="2"/>
<circle cx="22" cy="18" r="6" fill="#ff5f57"/><circle cx="42" cy="18" r="6" fill="#febc2e"/><circle cx="62" cy="18" r="6" fill="#28c840"/>
<text x="{w/2}" y="22" text-anchor="middle" font-size="12" fill="{MUTED}">{escape(title)}</text>
<line x1="2" y1="34" x2="{w-2}" y2="34" stroke="{BORDER}"/>
{body}
</svg>
"""


# ---------------------------------------------------------------- header.svg
def ascii_avatar(img, x0, y0, cols, rows, cw, lh):
    ramp = " .:-=+*#%@"
    rgb = img.convert("RGB").resize((cols, rows), Image.LANCZOS)
    lum = ImageOps.autocontrast(rgb.convert("L"), cutoff=2)
    lum = ImageEnhance.Contrast(lum).enhance(1.35)
    px, cpx = lum.load(), rgb.load()
    rng = random.Random(42)
    out = []
    xs = " ".join(f"{x0 + c * cw:.1f}" for c in range(cols))
    for r in range(rows):
        runs, cur_lvl, cur = [], None, ""
        for c in range(cols):
            # máscara circular, como el avatar de GitHub
            dx = (c + 0.5) / cols - 0.5
            dy = (r + 0.5) / rows - 0.5
            if dx * dx + dy * dy > 0.25:
                lvl, ch = 0, " "
            else:
                R, G, B = cpx[c, r]
                if G - max(R, B) > 60 or max(R, G, B) < 25:
                    # fondo Matrix: 0/1 tenues
                    lvl = 1 if G > 120 else 0
                    ch = rng.choice("01") if G > 60 else " "
                else:
                    # el gato y los audífonos: rampa completa
                    i = min(len(ramp) - 1, int(px[c, r] / 255 * len(ramp)))
                    lvl = max(2, min(4, i // 2))
                    ch = ramp[max(1, i)]
            if lvl != cur_lvl and cur:
                runs.append((cur_lvl, cur))
                cur = ""
            cur_lvl = lvl
            cur += ch
        runs.append((cur_lvl, cur))
        spans = "".join(
            f'<tspan class="a{l}">{escape(s).replace(" ", "&#160;")}</tspan>' for l, s in runs
        )
        out.append(f'<text x="{xs}" y="{y0 + r * lh:.1f}">{spans}</text>')
    return "\n".join(out)


def yaml_lines():
    K, V, C, P, S = "k", "v", "c", "p", "s"  # key, value, comment, punctuation, section
    return [
        [(S, "profile"), (P, ":")],
        [(K, "  user"), (P, ": "), (V, USER)],
        [(K, "  role"), (P, ": "), (V, "Developer Junior")],
        [(K, "  origin"), (P, ": "), (V, "Colombia")],
        [(K, "  focus"), (P, ": "), (V, "Frontend · IA · Automatizaciones")],
        [(K, "  also"), (P, ": "), (V, "Marketing digital · SEO")],
        [(K, "  status"), (P, ": "), ("g", "construyendo en público")],
        [(S, "stack"), (P, ":")],
        [(K, "  frontend"), (P, ": "), (V, "Next.js · React · TypeScript · Tailwind")],
        [(K, "  backend"), (P, ": "), (V, "Node.js · Prisma · PostgreSQL")],
        [(K, "  automation"), (P, ": "), ("n", "n8n"), (V, " · Claude / IA")],
        [(K, "  deploy"), (P, ": "), (V, "Vercel · Git · GitHub")],
        [(S, "projects"), (P, ":")],
        [(P, "  - "), (V, "velas-luze"), (C, "   # e-commerce en Next.js")],
        [(S, "now"), (P, ":")],
        [(K, "  learning"), (P, ": "), (V, "arquitectura de software")],
        [(C, "# wake up, samael... the matrix has you")],
    ]


def build_header(avatar):
    W, H = 960, 410
    # Panel izquierdo: retrato ASCII
    lx, ly, lw, lh_ = 16, 46, 360, 348
    cols, rows, cw, line = 56, 48, 5.4, 6.0
    ax = lx + (lw - cols * cw) / 2
    art = ascii_avatar(avatar, ax, ly + 36, cols, rows, cw, line)

    # Panel derecho: profile.yml
    rx, ry, rw, rh = 392, 46, 552, 348
    code, y = [], ry + 50
    for n, toks in enumerate(yaml_lines(), 1):
        spans = "".join(f'<tspan class="{t}">{escape(s)}</tspan>' for t, s in toks)
        code.append(
            f'<text x="{rx + 14}" y="{y}" class="ln" text-anchor="start">{n:>2}</text>'
            f'<text x="{rx + 44}" y="{y}" xml:space="preserve">{spans}</text>'
        )
        y += 16.4
    last = sum(len(s) for _, s in yaml_lines()[-1])
    cursor = f'<rect class="blink" x="{rx + 48 + last * 7.52:.1f}" y="{y - 16.4 - 11}" width="8" height="14" fill="{GREEN}"/>'

    body = f"""
<style>
  .a0 {{ fill: {GREEN}; opacity: .10; }} .a1 {{ fill: {GREEN}; opacity: .35; }}
  .a2 {{ fill: {GREEN}; opacity: .6; }}  .a3 {{ fill: {GREEN}; opacity: .85; }}
  .a4 {{ fill: #d8ffe9; }}
  .art text {{ font-size: 7.4px; }}
  .code text {{ font-size: 12.5px; }}
  .ln {{ fill: #30363d; }} .k {{ fill: {GREEN_DIM}; }} .s {{ fill: {GREEN}; font-weight: 700; }}
  .v {{ fill: {TEXT}; }} .p {{ fill: {MUTED}; }} .c {{ fill: {MUTED}; font-style: italic; }}
  .g {{ fill: {YELLOW}; }} .n {{ fill: {PINK}; }}
</style>
<rect x="{lx}" y="{ly}" width="{lw}" height="{lh_}" rx="8" fill="{PANEL}" stroke="{BORDER}"/>
<text x="{lx + 12}" y="{ly + 18}" font-size="10" fill="{GREEN}" letter-spacing="1">VISUAL.MAP</text>
<text x="{lx + lw - 12}" y="{ly + 18}" font-size="10" fill="{MUTED}" text-anchor="end">{cols}x{rows} · ascii</text>
<g class="art">{art}</g>
<text x="{lx + 12}" y="{ly + lh_ - 10}" font-size="9" fill="{MUTED}">src: avatar.png → luminance → glyphs</text>

<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="8" fill="{PANEL}" stroke="{BORDER}"/>
<text x="{rx + 14}" y="{ry + 20}" font-size="11" fill="{TEXT}">profile.yml <tspan fill="{MUTED}">[YAML]</tspan></text>
<rect x="{rx + rw - 128}" y="{ry + 8}" width="116" height="18" rx="9" fill="#0f2a1e"/>
<text x="{rx + rw - 70}" y="{ry + 21}" font-size="10" fill="{GREEN}" text-anchor="middle">@{USER}</text>
<line x1="{rx}" y1="{ry + 30}" x2="{rx + rw}" y2="{ry + 30}" stroke="{BORDER}"/>
<g class="code">{''.join(code)}</g>
{cursor}
<rect x="{rx + 1}" y="{ry + rh - 22}" width="{rw - 2}" height="21" fill="#0b1f16"/>
<rect x="{rx + 1}" y="{ry + rh - 22}" width="64" height="21" fill="{GREEN}"/>
<text x="{rx + 33}" y="{ry + rh - 8}" font-size="10" font-weight="700" fill="{PANEL}" text-anchor="middle">NORMAL</text>
<text x="{rx + 76}" y="{ry + rh - 8}" font-size="10" fill="{TEXT}">profile.yml</text>
<text x="{rx + rw / 2 + 30}" y="{ry + rh - 8}" font-size="10" fill="{MUTED}">[utf-8]</text>
<text x="{rx + rw - 12}" y="{ry + rh - 8}" font-size="10" fill="{MUTED}" text-anchor="end">yaml · {len(yaml_lines())}L · 100%</text>
"""
    (ASSETS / "header.svg").write_text(window(W, H, "vim ~/profile.yml", body), encoding="utf-8")


# ---------------------------------------------------------------- whoami.svg
def matrix_rain(x, y, w, h, n_cols=16):
    glyphs = "01<>/{}[]$#*+=:;%&ABCDEFXYZ"
    cw = w / n_cols
    cols = []
    for i in range(n_cols):
        length = random.randint(8, 16)
        dur = random.uniform(3.5, 8.0)
        begin = -random.uniform(0, dur)
        cx = x + cw * i + cw / 2
        chars = []
        for j in range(length):
            ch = escape(random.choice(glyphs))
            if j == length - 1:
                fill, op = "#eafff4", 1
            else:
                fill, op = GREEN, round(0.15 + 0.75 * j / length, 2)
            chars.append(
                f'<text x="{cx:.1f}" y="{j * 14}" fill="{fill}" opacity="{op}" text-anchor="middle">{ch}</text>'
            )
        span = length * 14
        cols.append(
            f'<g><animateTransform attributeName="transform" type="translate" '
            f'from="0 {y - span}" to="0 {y + h}" dur="{dur:.2f}s" begin="{begin:.2f}s" '
            f'repeatCount="indefinite"/>{"".join(chars)}</g>'
        )
    return "\n".join(cols)


def build_whoami():
    W, H = 960, 300
    lx, ly, lw, lh = 20, 50, 600, 230
    rx, ry, rw, rh = 636, 50, 304, 230

    def row(y, parts):
        bold = ' font-weight="700"'
        spans = "".join(f'<tspan fill="{c}"{bold if b else ""}>{escape(t)}</tspan>' for t, c, b in parts)
        return f'<text x="{lx + 18}" y="{y}" xml:space="preserve">{spans}</text>'

    lines = [
        row(ly + 30, [("❯ ", GREEN, True), ("whoami", GREEN, True)]),
        row(ly + 52, [(USER, TEXT, True), ("  —  ", MUTED, False), ("Developer Junior", YELLOW, False)]),
        row(ly + 80, [("context:   ", MUTED, False), ("Colombia · CO", CYAN, False)]),
        row(ly + 100, [("mission:   ", MUTED, False), ("unir código, marketing e IA", GREEN_DIM, False)]),
        row(ly + 118, [("           ", MUTED, False), ("para crear productos que venden", GREEN_DIM, False)]),
        row(ly + 148, [("❯ ", GREEN, True), ("ls expertise/", GREEN, True)]),
        row(ly + 170, [("frontend/     ", PINK, False), ("Next.js · React · TS · Tailwind", TEXT, False)]),
        row(ly + 188, [("automation/   ", PINK, False), ("n8n · IA · APIs", TEXT, False)]),
        row(ly + 206, [("marketing/    ", PINK, False), ("SEO · contenido · embudos", TEXT, False)]),
    ]

    body = f"""
<defs><clipPath id="rain"><rect x="{rx + 2}" y="{ry + 30}" width="{rw - 4}" height="{rh - 58}"/></clipPath></defs>
<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="8" fill="{PANEL}" stroke="{BORDER}"/>
<g font-size="14">{''.join(lines)}</g>

<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="8" fill="{PANEL}" stroke="{BORDER}"/>
<text x="{rx + 14}" y="{ry + 20}" font-size="12" fill="{GREEN}">matrix runtime</text>
<circle class="blink" cx="{rx + rw - 18}" cy="{ry + 16}" r="4" fill="{GREEN}"/>
<g clip-path="url(#rain)" font-size="12">{matrix_rain(rx + 4, ry + 30, rw - 8, rh - 58)}</g>
<text x="{rx + 14}" y="{ry + rh - 12}" font-size="11" fill="{MUTED}">status: <tspan fill="{GREEN}">aprendiendo siempre</tspan><tspan class="blink" fill="{GREEN}"> █</tspan></text>
"""
    title = f"{USER} · profile shell · online"
    (ASSETS / "whoami.svg").write_text(window(W, H, title, body), encoding="utf-8")


# ---------------------------------------------------------------- radar.svg
def radar(cx, cy, r, title, axes):
    n = len(axes)
    pts = lambda f: [
        (cx + r * f(i) * math.sin(2 * math.pi * i / n), cy - r * f(i) * math.cos(2 * math.pi * i / n))
        for i in range(n)
    ]
    poly = lambda p: " ".join(f"{x:.1f},{y:.1f}" for x, y in p)
    out = [f'<text x="{cx}" y="62" text-anchor="middle" font-size="13" font-weight="700" fill="{GREEN}">{escape(title)}</text>']
    for k in (0.25, 0.5, 0.75, 1):
        out.append(f'<polygon points="{poly(pts(lambda i: k))}" fill="none" stroke="#1f3b2d"/>')
    for x, y in pts(lambda i: 1):
        out.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#1f3b2d"/>')
    vals = pts(lambda i: axes[i][1] / 100)
    out.append(
        f'<polygon points="{poly(vals)}" fill="{GREEN}" fill-opacity=".18" stroke="{GREEN}" stroke-width="2">'
        f'<animate attributeName="fill-opacity" values=".1;.28;.1" dur="3s" repeatCount="indefinite"/></polygon>'
    )
    for x, y in vals:
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{GREEN}"/>')
    for i, (x, y) in enumerate(pts(lambda i: 1.22)):
        name, v = axes[i]
        anchor = "middle" if abs(x - cx) < 5 else ("start" if x > cx else "end")
        out.append(
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="11" fill="{TEXT}">{escape(name)}'
            f'<tspan x="{x:.1f}" dy="13" fill="{MUTED}" font-size="10">{v}</tspan></text>'
        )
    return "\n".join(out)


def build_radar():
    W, H = 960, 380
    skills = [("Frontend", 70), ("Automatización", 75), ("IA", 75), ("Marketing", 80), ("SEO", 65), ("Backend", 50)]
    stack = [("TypeScript", 65), ("React", 70), ("Next.js", 70), ("Tailwind", 80), ("n8n", 75), ("SQL", 50)]
    body = f"""
{radar(250, 222, 100, "skill_radar", skills)}
{radar(710, 222, 100, "stack_radar", stack)}
<text x="{W/2}" y="{H - 14}" text-anchor="middle" font-size="10" fill="{MUTED}">signals: skill_radar · stack_radar · status: <tspan fill="{GREEN}">healthy</tspan></text>
"""
    (ASSETS / "radar.svg").write_text(window(W, H, "$ samael --signals --all", body), encoding="utf-8")


# ---------------------------------------------------------------- tiles
N8N = "M21.4737 5.6842c-1.1772 0-2.1663.8051-2.4468 1.8947h-2.8955c-1.235 0-2.289.893-2.492 2.111l-.1038.623a1.263 1.263 0 0 1-1.246 1.0555H11.289c-.2805-1.0896-1.2696-1.8947-2.4468-1.8947s-2.1663.8051-2.4467 1.8947H4.973c-.2805-1.0896-1.2696-1.8947-2.4468-1.8947C1.1311 9.4737 0 10.6047 0 12s1.131 2.5263 2.5263 2.5263c1.1772 0 2.1663-.8051 2.4468-1.8947h1.4223c.2804 1.0896 1.2696 1.8947 2.4467 1.8947 1.1772 0 2.1663-.8051 2.4468-1.8947h1.0008a1.263 1.263 0 0 1 1.2459 1.0555l.1038.623c.203 1.218 1.257 2.111 2.492 2.111h.3692c.2804 1.0895 1.2696 1.8947 2.4468 1.8947 1.3952 0 2.5263-1.131 2.5263-2.5263s-1.131-2.5263-2.5263-2.5263c-1.1772 0-2.1664.805-2.4468 1.8947h-.3692a1.263 1.263 0 0 1-1.246-1.0555l-.1037-.623A2.52 2.52 0 0 0 13.9607 12a2.52 2.52 0 0 0 .821-1.4794l.1038-.623a1.263 1.263 0 0 1 1.2459-1.0555h2.8955c.2805 1.0896 1.2696 1.8947 2.4468 1.8947 1.3952 0 2.5263-1.131 2.5263-2.5263s-1.131-2.5263-2.5263-2.5263m0 1.2632a1.263 1.263 0 0 1 1.2631 1.2631 1.263 1.263 0 0 1-1.2631 1.2632 1.263 1.263 0 0 1-1.2632-1.2632 1.263 1.263 0 0 1 1.2632-1.2631M2.5263 10.7368A1.263 1.263 0 0 1 3.7895 12a1.263 1.263 0 0 1-1.2632 1.2632A1.263 1.263 0 0 1 1.2632 12a1.263 1.263 0 0 1 1.2631-1.2632m6.3158 0A1.263 1.263 0 0 1 10.1053 12a1.263 1.263 0 0 1-1.2632 1.2632A1.263 1.263 0 0 1 7.579 12a1.263 1.263 0 0 1 1.2632-1.2632m10.1053 3.7895a1.263 1.263 0 0 1 1.2631 1.2632 1.263 1.263 0 0 1-1.2631 1.2631 1.263 1.263 0 0 1-1.2632-1.2631 1.263 1.263 0 0 1 1.2632-1.2632"
CLAUDE = "m4.7144 15.9555 4.7174-2.6471.079-.2307-.079-.1275h-.2307l-.7893-.0486-2.6956-.0729-2.3375-.0971-2.2646-.1214-.5707-.1215-.5343-.7042.0546-.3522.4797-.3218.686.0608 1.5179.1032 2.2767.1578 1.6514.0972 2.4468.255h.3886l.0546-.1579-.1336-.0971-.1032-.0972L6.973 9.8356l-2.55-1.6879-1.3356-.9714-.7225-.4918-.3643-.4614-.1578-1.0078.6557-.7225.8803.0607.2246.0607.8925.686 1.9064 1.4754 2.4893 1.8336.3643.3035.1457-.1032.0182-.0728-.164-.2733-1.3539-2.4467-1.445-2.4893-.6435-1.032-.17-.6194c-.0607-.255-.1032-.4674-.1032-.7285L6.287.1335 6.6997 0l.9957.1336.419.3642.6192 1.4147 1.0018 2.2282 1.5543 3.0296.4553.8985.2429.8318.091.255h.1579v-.1457l.1275-1.706.2368-2.0947.2307-2.6957.0789-.7589.3764-.9107.7468-.4918.5828.2793.4797.686-.0668.4433-.2853 1.8517-.5586 2.9021-.3643 1.9429h.2125l.2429-.2429.9835-1.3053 1.6514-2.0643.7286-.8196.85-.9046.5464-.4311h1.0321l.759 1.1293-.34 1.1657-1.0625 1.3478-.8804 1.1414-1.2628 1.7-.7893 1.36.0729.1093.1882-.0183 2.8535-.607 1.5421-.2794 1.8396-.3157.8318.3886.091.3946-.3278.8075-1.967.4857-2.3072.4614-3.4364.8136-.0425.0304.0486.0607 1.5482.1457.6618.0364h1.621l3.0175.2247.7892.522.4736.6376-.079.4857-1.2142.6193-1.6393-.3886-3.825-.9107-1.3113-.3279h-.1822v.1093l1.0929 1.0686 2.0035 1.8092 2.5075 2.3314.1275.5768-.3218.4554-.34-.0486-2.2039-1.6575-.85-.7468-1.9246-1.621h-.1275v.17l.4432.6496 2.3436 3.5214.1214 1.0807-.17.3521-.6071.2125-.6679-.1214-1.3721-1.9246L14.38 17.959l-1.1414-1.9428-.1397.079-.674 7.2552-.3156.3703-.7286.2793-.6071-.4614-.3218-.7468.3218-1.4753.3886-1.9246.3157-1.53.2853-1.9004.17-.6314-.0121-.0425-.1397.0182-1.4328 1.9672-2.1796 2.9446-1.7243 1.8456-.4128.164-.7164-.3704.0667-.6618.4008-.5889 2.386-3.0357 1.4389-1.882.929-1.0868-.0062-.1579h-.0546l-6.3385 4.1164-1.1293.1457-.4857-.4554.0608-.7467.2307-.2429 1.9064-1.3114Z"


def tile(name, path, color):
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256"><title>{name}</title>'
        f'<rect width="256" height="256" rx="60" fill="#242938"/>'
        f'<g transform="translate(38 38) scale(7.5)"><path fill="{color}" d="{path}"/></g></svg>'
    )
    (ASSETS / f"{name.lower()}.svg").write_text(svg, encoding="utf-8")


def load_avatar():
    if len(sys.argv) > 1:
        return Image.open(sys.argv[1])
    with urllib.request.urlopen(f"https://github.com/{USER}.png?size=256") as r:
        return Image.open(io.BytesIO(r.read()))


if __name__ == "__main__":
    build_header(load_avatar())
    build_whoami()
    build_radar()
    tile("n8n", N8N, "#EA4B71")
    tile("Claude", CLAUDE, "#D97757")
    print("ok ->", ", ".join(p.name for p in sorted(ASSETS.glob("*.svg"))))
