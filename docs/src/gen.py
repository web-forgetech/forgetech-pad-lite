"""Generates the README diagrams (SVG) for Forgetech Pad Lite.
Run:  python docs/src/gen.py   then render PNGs with docs/src/render.js
"""
import os

OUT = os.path.join(os.path.dirname(__file__), "..")

STYLE = """<style>
text{font-family:-apple-system,"Segoe UI",Helvetica,Arial,sans-serif}
.t{font-size:14px;fill:#2C2C2A}.ts{font-size:12px;fill:#5F5E5A}.th{font-size:14px;font-weight:600;fill:#2C2C2A}
.title{font-size:16px;font-weight:600;fill:#2C2C2A}
.teal rect,.teal circle{fill:#E1F5EE;stroke:#0F6E56}.teal .th{fill:#085041}.teal .ts{fill:#0F6E56}
.purple rect,.purple circle{fill:#EEEDFE;stroke:#534AB7}.purple .th{fill:#3C3489}.purple .ts{fill:#534AB7}
.coral rect,.coral circle{fill:#FAECE7;stroke:#993C1D}.coral .th{fill:#712B13}.coral .ts{fill:#993C1D}
.gray rect{fill:#F1EFE8;stroke:#5F5E5A}.gray .th{fill:#2C2C2A}.gray .ts{fill:#5F5E5A}
.blue rect{fill:#E6F1FB;stroke:#185FA5}.blue .th{fill:#0C447C}.blue .ts{fill:#185FA5}
.amber rect{fill:#FAEEDA;stroke:#854F0B}.amber .th{fill:#633806}.amber .ts{fill:#854F0B}
</style>
<defs><marker id="ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
<path d="M2 1L8 5L2 9" fill="none" stroke="#5F5E5A" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker></defs>"""


def svg(name, w, h, title, body):
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
         f'<title>{title}</title>{STYLE}<rect width="{w}" height="{h}" fill="#FFFFFF"/>'
         f'<text class="title" x="{w/2}" y="28" text-anchor="middle">{title}</text>{body}</svg>')
    open(os.path.join(OUT, name + ".svg"), "w").write(s)


def box(cls, x, y, w, h, title, sub=None, sub2=None):
    cy = y + h / 2
    if sub2:
        return (f'<g class="{cls}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" stroke-width="0.8"/>'
                f'<text class="th" x="{x+w/2}" y="{cy-12}" text-anchor="middle" dominant-baseline="central">{title}</text>'
                f'<text class="ts" x="{x+w/2}" y="{cy+6}" text-anchor="middle" dominant-baseline="central">{sub}</text>'
                f'<text class="ts" x="{x+w/2}" y="{cy+22}" text-anchor="middle" dominant-baseline="central">{sub2}</text></g>')
    if sub:
        return (f'<g class="{cls}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" stroke-width="0.8"/>'
                f'<text class="th" x="{x+w/2}" y="{cy-9}" text-anchor="middle" dominant-baseline="central">{title}</text>'
                f'<text class="ts" x="{x+w/2}" y="{cy+10}" text-anchor="middle" dominant-baseline="central">{sub}</text></g>')
    return (f'<g class="{cls}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" stroke-width="0.8"/>'
            f'<text class="th" x="{x+w/2}" y="{cy}" text-anchor="middle" dominant-baseline="central">{title}</text></g>')


def arrow(x1, y1, x2, y2):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#5F5E5A" stroke-width="1.5" marker-end="url(#ar)"/>'


# ---------------------------------------------------------------- 1. system overview
b = ""
xs = [20, 190, 360, 530]
b += box("coral", xs[0], 60, 140, 72, "Forgetech Pad", "ESP32-C3", "Xbox Series X mode")
b += box("blue", xs[1], 60, 140, 72, "Mac", "pair here", "(Bluetooth settings)")
b += box("gray", xs[2], 60, 140, 72, "Parallels", "shares controller", "with Windows")
b += box("teal", xs[3], 60, 140, 72, "Windows game", "sees a Virtual", "Xbox Controller")
for i in range(3):
    b += arrow(xs[i] + 142, 96, xs[i + 1] - 4, 96)
b += '<text class="ts" x="175" y="150" text-anchor="middle">Bluetooth LE</text>'
b += arrow(260, 134, 260, 182)
b += box("blue", 190, 186, 140, 56, "macOS games", "use it directly")
b += ('<text class="ts" x="340" y="276" text-anchor="middle">The Mac sees an "Xbox Wireless Controller". Parallels 18+ passes every controller macOS supports</text>'
      '<text class="ts" x="340" y="294" text-anchor="middle">to Windows 10/11 as a "Virtual Xbox Controller", so the same pad works on both sides.</text>')
svg("system", 690, 316, "How the controller reaches macOS and Windows", b)

# ---------------------------------------------------------------- 2. controller layout
b = '<rect x="60" y="50" width="560" height="250" rx="70" fill="#F1EFE8" stroke="#444441" stroke-width="1.2"/>'
b += '<text class="th" x="340" y="82" text-anchor="middle">Forgetech Pad Lite</text>'
# direction cluster
for (cx, cy, lab, gp) in [(190, 125, "Up", "GPIO0"), (190, 235, "Down", "GPIO1"), (135, 180, "Left", "GPIO3"), (245, 180, "Right", "GPIO4")]:
    b += f'<g class="teal"><circle cx="{cx}" cy="{cy}" r="25" stroke-width="0.8"/><text class="th" x="{cx}" y="{cy-5}" text-anchor="middle" dominant-baseline="central">{lab}</text><text class="ts" x="{cx}" y="{cy+11}" text-anchor="middle" dominant-baseline="central">{gp}</text></g>'
b += '<text class="ts" x="190" y="184" text-anchor="middle">left stick</text>'
# action buttons
b += '<g class="purple"><circle cx="560" cy="150" r="28" stroke-width="0.8"/><text class="th" x="560" y="145" text-anchor="middle" dominant-baseline="central">B</text><text class="ts" x="560" y="162" text-anchor="middle" dominant-baseline="central">GPIO6</text></g>'
b += '<g class="purple"><circle cx="495" cy="205" r="28" stroke-width="0.8"/><text class="th" x="495" y="200" text-anchor="middle" dominant-baseline="central">A</text><text class="ts" x="495" y="217" text-anchor="middle" dominant-baseline="central">GPIO5</text></g>'
# turbo + LED
b += '<g class="coral"><rect x="300" y="205" width="80" height="34" rx="17" stroke-width="0.8"/><text class="th" x="340" y="217" text-anchor="middle" dominant-baseline="central">Turbo</text><text class="ts" x="340" y="231" text-anchor="middle" dominant-baseline="central">GPIO7</text></g>'
b += '<circle cx="340" cy="130" r="9" fill="#97C459" stroke="#3B6D11" stroke-width="0.8"/>'
b += '<text class="ts" x="340" y="160" text-anchor="middle">Status LED (GPIO8)</text>'
b += ('<text class="ts" x="340" y="330" text-anchor="middle">Direction buttons push the Xbox left stick fully (two at once = diagonal). A and B are Xbox A and B.</text>'
      '<text class="ts" x="340" y="348" text-anchor="middle">Turbo turns auto-fire on A on/off. All buttons connect between their GPIO and GND.</text>')
svg("layout", 680, 368, "Controller layout (top view)", b)

# ---------------------------------------------------------------- 3. auto-fire timing
X0, X1 = 150, 650
ev = {"on": 220, "hold": 400, "rel": 490, "off": 590}
b = ""
rows = [("Turbo button", 70), ("Status LED", 130), ("Your finger on A", 190), ("A sent to the game", 250)]
for lab, y in rows:
    b += f'<text class="th" x="20" y="{y+4}">{lab}</text>'
    b += f'<line x1="{X0}" y1="{y+20}" x2="{X1}" y2="{y+20}" stroke="#D3D1C7" stroke-width="0.8"/>'
for k, x in ev.items():
    b += f'<line x1="{x}" y1="52" x2="{x}" y2="290" stroke="#888780" stroke-width="0.8" stroke-dasharray="4 3"/>'
labels = {"on": "Turbo ON", "hold": "Hold A", "rel": "Release A", "off": "Turbo OFF"}
for k, x in ev.items():
    b += f'<text class="ts" x="{x}" y="48" text-anchor="middle">{labels[k]}</text>'
HI, LO = -12, 18  # offsets from row y
def wave(y, pts):
    d = "M" + " L".join(f"{px} {y+py}" for px, py in pts)
    return f'<path d="{d}" fill="none" stroke="#534AB7" stroke-width="2" stroke-linejoin="round"/>'
# turbo button: two short presses
y = 70
b += f'<path d="M{X0} {y+LO} H{ev["on"]} V{y+HI} H{ev["on"]+14} V{y+LO} H{ev["off"]} V{y+HI} H{ev["off"]+14} V{y+LO} H{X1}" fill="none" stroke="#D85A30" stroke-width="2"/>'
# LED bars
y = 130
b += f'<rect x="{X0}" y="{y-6}" width="{ev["on"]-X0}" height="18" fill="#97C459"/>'
b += f'<rect x="{ev["on"]}" y="{y-6}" width="{ev["off"]-ev["on"]}" height="18" fill="#EF9F27"/>'
b += f'<rect x="{ev["off"]}" y="{y-6}" width="{X1-ev["off"]}" height="18" fill="#97C459"/>'
b += f'<text class="ts" x="{(X0+ev["on"])/2}" y="{y+7}" text-anchor="middle">green</text>'
b += f'<text class="ts" x="{(ev["on"]+ev["off"])/2}" y="{y+7}" text-anchor="middle">orange (auto-fire ON)</text>'
# finger on A
y = 190
b += f'<path d="M{X0} {y+LO} H{ev["hold"]} V{y+HI} H{ev["rel"]} V{y+LO} H{X1}" fill="none" stroke="#1D9E75" stroke-width="2"/>'
# A sent: pulses between on..hold and rel..off, steady during hold
y = 250
pts = [(X0, LO), (ev["on"], LO)]
x = ev["on"]
step = 10
def pulses(x_start, x_end):
    p, x = [], x_start
    while x + 2 * step <= x_end:
        p += [(x, HI), (x + step, HI), (x + step, LO), (x + 2 * step, LO)]
        x += 2 * step
    p += [(x_end, LO)]
    return p
pts += [(ev["on"], LO)] + pulses(ev["on"], ev["hold"])
pts += [(ev["hold"], LO), (ev["hold"], HI), (ev["rel"], HI), (ev["rel"], LO)]
pts += pulses(ev["rel"], ev["off"]) + [(X1, LO)]
d = f"M{pts[0][0]} {y+pts[0][1]}" + "".join(f" L{px} {y+py}" for px, py in pts[1:])
b += f'<path d="{d}" fill="none" stroke="#534AB7" stroke-width="2" stroke-linejoin="round"/>'
b += (f'<text class="ts" x="{(ev["on"]+ev["hold"])/2}" y="{y+40}" text-anchor="middle">fires by itself, 10/s</text>'
      f'<text class="ts" x="{(ev["hold"]+ev["rel"])/2}" y="{y+40}" text-anchor="middle">steady hold</text>'
      f'<text class="ts" x="{(ev["rel"]+ev["off"])/2}" y="{y+40}" text-anchor="middle">fires again</text>')
svg("autofire", 680, 310, "Auto-fire behaviour on button A", b)

# ---------------------------------------------------------------- 4. firmware flow
b = ""
W, X = 300, 190
steps = [
    ("gray", "setup()", "pull-ups on, start BLE as Xbox Series X"),
    ("teal", "Read buttons", "debounced, 20 ms"),
    ("coral", "Turbo pressed?", "toggle auto-fire on/off"),
    ("blue", "Host connected?", "no: blink LED blue, go back"),
    ("purple", "Work out A, B, stick", "apply auto-fire rule to A"),
    ("amber", "Anything changed?", "yes: send one BLE report"),
]
y = 50
ys = []
for cls, t, s in steps:
    b += box(cls, X, y, W, 50, t, s)
    ys.append(y)
    y += 70
for i in range(len(steps) - 1):
    b += arrow(X + W / 2, ys[i] + 50, X + W / 2, ys[i + 1] - 4)
# loop back
yl = ys[-1] + 25
b += f'<path d="M{X+W} {yl} H{X+W+50} V{ys[1]+25} H{X+W+6}" fill="none" stroke="#5F5E5A" stroke-width="1.5" marker-end="url(#ar)"/>'
b += f'<text class="ts" x="{X+W+58}" y="{(yl+ys[1]+25)/2}">every 5 ms</text>'
svg("firmware-flow", 680, ys[-1] + 80, "What the firmware does (main loop)", b)
print("ok")
