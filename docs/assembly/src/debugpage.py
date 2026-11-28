"""Debugging page for the assembly guide: dock contact pinout + bring-up measurements.
guide.py adds it as the last page (needs img/dock-pinout.png: cp ../dock-pinout.png img/).
Run alone to render just this page:  python3 debugpage.py OUT.html PAGE_NO"""
import sys

ROWS = [
    ("1", "Dock alone: spring pin P4 (VIN) to P3 (GND)", "about 5 V", "0 V: USB cable or the dock's fuse / band switch."),
    ("2", "Band VIN: C201 pad to TP707 (GND)", "about 5 V", "0 V while step 1 is fine: the dock pins aren't reaching the band's pads. Reseat; check the carrier pin tails."),
    ("3", "TP705 (PMID) to TP707", "about 5 V on the dock, cell voltage off it", "0 V with VIN fine: the charger (U201) isn't starting. Check its solder."),
    ("4", "R203 pad (2.0 V rail) to TP707", "1.97 to 2.03 V", "0 V with PMID fine: the 2.0 V regulator (U203)."),
    ("5", "TP706 (VBAT) to TP707", "3.0 to 4.2 V, rising slowly on the dock", "0 V: cell wires (TP201 +, TP202 −) or the cell's protection is asleep."),
    ("6", "TP701 (nRESET) to TP707", "about 2.0 V", "Low: the chip is held in reset."),
]


def body(img_src):
    rows = "".join(f"<tr><td class='n'>{n}</td><td>{w}</td><td><b>{e}</b></td><td>{f}</td></tr>" for n, w, e, f in ROWS)
    return f"""<h1>Debugging: dock contacts and test points</h1>
<div class="dbg"><div class="dbgimg"><img src="{img_src}"></div><div class="dbgtxt">
<p>The dock touches four gold pads on the wrist side: <b>1 SWDCLK, 2 SWDIO, 3 GND, 4 VIN</b>. The dock's spring pins
<b>P1 to P4</b> sit right under pads 1 to 4. The band has no firmware until you flash it, so its LED stays dark at
first; that is normal.</p>
<p>Fit the <b>dev shell</b> (open roof, <code>hardware/band/rev-e/case</code>) instead of the real shell, set the band in a
powered dock and measure in this order. Black probe on <b>TP707 (GND)</b>.</p>
<table class="dbgt"><tr><th></th><th>Measure</th><th>Expect</th><th>If not</th></tr>{rows}</table>
<div class="box tip"><span class="ic">i</span><div><b>Off the dock</b> the charger can sit in ship mode with everything off.
Tap TP203 (/MR) to TP707 with tweezers to wake it; TP705 then reads the cell voltage.</div></div>
<div class="box check"><span class="ic">✓</span><div><b>All six fine?</b> Then SWD should answer:
<code>probe-rs info --protocol swd</code>. No reply with good rails means pad 1 or 2 isn't touching its spring pin.</div></div>
<div class="box warn"><span class="ic">!</span><div>Never bridge VIN and GND with the probe tips or tweezers.</div></div>
</div></div>"""


CSS = """.dbg{display:flex;gap:6mm;height:168mm}.dbgimg{width:112mm;display:flex;align-items:center}
.dbgimg img{max-width:100%;max-height:168mm}.dbgtxt{flex:1;font-size:9.5pt}.dbgtxt p{margin:0 0 2mm}
.dbgt{border-collapse:collapse;width:100%;font-size:8.8pt;margin:1mm 0 1mm}.dbgt th{text-align:left;background:#eef1f5;padding:1mm 1.5mm}
.dbgt td{border-top:.3mm solid #dde2ea;padding:1.1mm 1.5mm;vertical-align:top}.dbgt td.n{font-weight:900;color:var(--sec)}"""

if __name__ == "__main__":
    import os
    out, pn = sys.argv[1], sys.argv[2]
    here = os.path.dirname(os.path.abspath(__file__))
    css = open(os.path.join(here, "guide.css")).read() + CSS
    img = "file://" + os.path.abspath(os.path.join(here, "..", "dock-pinout.png"))
    page = f"""<section class="page" style="--sec:#e63946">
<div class="secbar"><span class="secl">F</span><span class="secn">Finish</span></div>
{body(img)}
<div class="foot"><span>NudgeBand · band rev C board · case rev E · dock rev D</span><span class="pn">{pn}</span></div></section>"""
    open(out, "w").write(f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{page}</body></html>')
