import json, html, os
IMG=os.path.abspath('img'); A=json.load(open('img/anchors.json'))
def im(n): return f'file://{IMG}/{n}.png'
E=html.escape
SECTIONS={'A':('Print','#f4a261'),'B':('Dock','#3d5a80'),'C':('Band cover','#1f9bd7'),'D':('Band board','#2a9d6a'),'E':('Close the band','#8e5bd3'),'F':('Finish','#e63946'),'0':('Start here','#555')}
pages=[]; stepno=[0]
def page(sec,body,cls=''):
    name,col=SECTIONS[sec]
    pages.append(f'''<section class="page {cls}" style="--sec:{col}">
<div class="secbar"><span class="secl">{'' if sec=='0' else sec}</span><span class="secn">{name}</span></div>
{body}
<div class="foot"><span>NudgeBand · band rev C board · case rev E · dock rev D</span><span class="pn">{len(pages)+1}</span></div></section>''')
def parts(lst,title='You need'):
    if not lst: return ''
    it=''.join(f'<div class="pi"><img src="{im(n)}"><b>{q}</b><small>{E(l)}</small></div>' for n,q,l in lst)
    return f'<div class="parts"><div class="pt">{title}</div><div class="pgrid">{it}</div></div>'
def labels(n,lab):
    out=''
    for k,txt,col in lab:
        x,y=A[n][k]; out+=f'<div class="lab" style="left:{x*100:.1f}%;top:{y*100:.1f}%;--c:{col}"><span>{E(txt)}</span></div>'
    return out
def box(kind,txt):
    icon={'warn':'!','tip':'i','check':'✓','stop':'✋'}[kind]
    return f'<div class="box {kind}"><span class="ic">{icon}</span><div>{txt}</div></div>'
def step(title,img,text,p=None,lab=(),boxes=(),imgcls='',extra=''):
    stepno[0]+=1; n=stepno[0]
    li=''.join(f'<li>{t}</li>' for t in text)
    imgs=img if isinstance(img,list) else [img]
    ih=''.join(f'<div class="shot {imgcls}"><img src="{im(i)}">{labels(i,lab) if i in A and lab else ""}</div>' for i in imgs)
    bx=''.join(box(k,t) for k,t in boxes)
    return f'''<div class="step"><div class="sh"><div class="num">{n}</div><div class="st">{title}</div></div>
<div class="sbody"><div class="sleft">{parts(p)}<ol>{li}</ol>{bx}{extra}</div><div class="sright">{ih}</div></div></div>'''
def two(a,b): return f'<div class="two">{a}{b}</div>'
def one(a): return f'<div class="one">{a}</div>'

# ---------------- cover
pages.append(f'''<section class="page cover">
<div class="cv-top"><div class="brand">NudgeBand</div><div class="cv-sub">Build instructions for the gentle-wake wristband</div></div>
<img class="hero" src="{im('hero')}">
<img class="hero2" src="{im('explode')}">
<div class="chips"><span>Band board rev C</span><span>Case rev E</span><span>Dock rev D</span><span>1 band + 1 dock</span><span>Soldering: medium</span><span>≈ 2 h + printing</span></div>
<div class="cv-foot">Open-source hardware · github.com/DevonHope/NudgeBand · Personal and experimental use only: the radio is not FCC/IC/CE certified.</div>
</section>''')

# ---------------- legend + safety + tools
leg=[('#d62828','Red wire / lead','goes to a + pad'),('#222','Black wire / lead','goes to a – pad'),('#e63946','Red magnet half','North pole (N)'),('#1d70b8','Blue magnet half','South pole (S)'),
     ('#e8b923','Gold','bare contact: keep clean'),('#e39a2b','Orange sheet','kapton tape'),('#ffb703','Yellow bead','gel epoxy'),('#f2f2f2','White strip','thin double-sided tape'),
     ('#f4efe4','Cream part','printed shell / dock top (light filament)'),('#5bc0eb','Light blue part','printed wrist cover'),('#3d5a80','Navy part','printed dock tray')]
lg=''.join(f'<div class="lg"><span class="sw" style="background:{c}"></span><b>{E(a)}</b><small>{E(b)}</small></div>' for c,a,b in leg)
tools=['Fine-tip soldering iron + thin solder','Flux, isopropyl alcohol (IPA), cotton swabs','Tweezers, flush cutters, wire strippers','Multimeter (volts + continuity beep)',
       'Hotplate or hot-air station (for the pins)','Small file or 400-grit sandpaper','3D printer (PETG)','Magnifier or loupe','A spare magnet (for marking poles, optional)','Computer with USB-C (for the dock)']
page('0',f'''<h1>Before you start</h1>
<div class="cols3"><div><h2>Colour key</h2><div class="legend">{lg}</div>
<div class="lg"><span class="arrowsw">➜</span><b>Red arrow</b><small>move the part this way</small></div></div>
<div><h2>Tools</h2><ul class="tools">{''.join(f"<li>{t}</li>" for t in tools)}</ul>
<h2>How to read the steps</h2><p>Each step shows <b>what you need</b> in the blue box, then the picture. Do the steps in order: later steps use the dock to check the earlier ones.
The order is: <b>A</b> print · <b>B</b> dock · <b>C</b> band cover · <b>D</b> band board · <b>E</b> close · <b>F</b> strap and first charge.</p></div>
<div>{box('stop','<b>LiPo safety.</b> Never let the two battery wires touch. Cut and solder <b>one wire at a time</b>. Don’t hold the iron on the cell itself, don’t bend, dent or puncture it, and never charge a swollen or damaged cell. Charge only on the dock.')}
{box('warn','<b>Polarity matters for the battery.</b> Red goes to <b>+</b> (TP201), black to <b>–</b> (TP202). Reversed, it can damage the board.')}
{box('tip','Print the <b>shell</b> and the <b>dock top</b> in a <b>light colour</b>: their LEDs shine through a 0.4 mm skin, not a hole.')}
{box('tip','A new band has <b>no firmware</b>. Its LED stays dark until you flash it through the dock (see step F).')}</div></div>''')

# ---------------- inventory
band_parts=[('p_board','1x','Band PCB rev C (JLC assembled)'),('p_cell','1x','60 mAh LiPo, protected, 17.25 × 10 × 5.05 mm (cut off the JST plug)'),('p_lra','1x','VG0832012 coin motor (LRA)'),
            ('p_carrier','1x','Contact carrier PCB (from the 6-up panel)'),('p_pin','4x','Mill-Max 0906-2-15-20-75-14-11-0 spring pin'),('p_mag4','2x','Ø4 × 1.5 mm N42 disc magnet (same as the dock)'),
            ('p_screw','1x','M2 × 6 countersunk screw (DIN 7991, A2)'),('p_insert','1x','M2 brass heat-set insert, 3 mm long'),('p_shell','1x','Printed shell'),('p_cover','1x','Printed wrist cover')]
dock_parts=[('p_dpcb','1x','Dock PCB rev C (flashed with debugprobe)'),('p_dpin','4x','Mill-Max 0906-4-15-20-75-14-11-0 spring pin'),('p_mag4','2x','Ø4 × 1.5 mm N42 disc magnet'),
            ('p_feet','4x','Ø8 mm self-adhesive rubber foot'),('p_dtop','1x','Printed dock top'),('p_dtray','1x','Printed dock tray')]
cons=[('p_kapton','1','Kapton tape, 10–13 mm wide'),('p_foam','1','Thin double-sided tape, 0.15 mm max (3M 467MP or 9448A). No foam')]
def inv(lst): return ''.join(f'<div class="inv"><img src="{im(n)}"><div><b>{q}</b> {E(l)}</div></div>' for n,q,l in lst)
page('0',f'''<h1>Parts list</h1><div class="invwrap"><div><h2>Band</h2><div class="invg">{inv(band_parts)}</div></div>
<div><h2>Dock</h2><div class="invg">{inv(dock_parts)}</div><h2>Also</h2><div class="invg">{inv(cons)}</div>
<ul class="small"><li>Gel (thick) 2-part epoxy: a few drops. Not a thin, runny one.</li><li>CA (super) glue: four drops, for the dock and band magnets.</li>
<li>Solder paste (or very little wire solder) for the spring pins.</li><li>16 mm strap, sewn from the patterns in <code>hardware/strap/</code>.</li></ul>
<p class="small">Where to buy pins, magnets and the carrier panel: <code>hardware/band/rev-a/contact-carrier/BUY-LIST.md</code>. Magnets: Indigo Instruments (Mouser has none). Cell: X2 Robotics 60 mAh protected.</p></div></div>''')

# ---------------- print list
def pp(n,name,mat,col,orient,notes):
    return f'<div class="pp"><img src="{im(n)}"><div class="ppt"><b>{name}</b><div class="tag" style="background:{col};color:{'#1d2433' if col=='#d9cdb3' else '#fff'}">{mat}</div><div><b>On the bed:</b> {orient}</div><div>{notes}</div></div></div>'
page('A',f'''<h1>A · Print list</h1><div class="ppgrid">
{pp('print_shell','Band shell','PETG · light colour','#d9cdb3','outer (top) face down — as shown, upside down','No supports. The first 0.4 mm over the LED is the window.')}
{pp('print_cover','Band wrist cover','PETG · any colour','#5bc0eb','wrist face down','No pause: the 2 magnets are glued in after printing (step 2). No supports.')}
{pp('print_dtop','Dock top','PETG or PLA · light colour','#d9cdb3','flat underside down','No supports; the USB-C pocket bridges about 8 mm.')}
{pp('print_dtray','Dock tray','PETG or PLA · any colour','#3d5a80','floor down','No supports.')}</div>
<table class="settings"><tr><th>Setting</th><th>Band shell + cover</th><th>Dock top + tray</th></tr>
<tr><td>Material</td><td>PETG (or ASA). Not PLA: it creeps at skin temperature</td><td>PETG or PLA</td></tr>
<tr><td>Nozzle / layer height</td><td>0.4 mm / 0.12–0.16 mm</td><td>0.4 mm / 0.16–0.2 mm</td></tr>
<tr><td>Walls / infill</td><td>4 perimeters / 100 %</td><td>3–4 perimeters / 30 % or more</td></tr>
<tr><td>Supports / brim</td><td>none / none</td><td>none / none</td></tr>
<tr><td>Files</td><td><code>hardware/band/rev-e/case/</code> …shell.stl, …cover.stl (and …dev-shell.stl for bring-up)</td><td><code>hardware/dock/rev-d/case/</code> …top.stl, …tray.stl</td></tr></table>''')

# ---------------- A steps
page('A',two(
 step('Print the shell',['print_shell'],['Load <b>wakeband-case-rev-e-shell.stl</b>.','Lay it <b>outer face down</b> (the open side faces up).','Print in white, natural or another light PETG.','Let it cool, then peel it off. Don’t sand the top: the LED skin is only 0.4 mm.'],
      p=[('p_shell','1x','shell')],boxes=[('tip','If the LED skin looks see-through or holed, that’s normal for thin PETG. Leave it as printed.')]),
 step('Print the cover, add the magnets',['s_magnets'],
      ['Print <b>wakeband-case-rev-e-cover.stl</b> wrist face down. No pause: the two round magnet pockets are open on the inside.',
       '<b>Stack the two magnets</b> so they snap together, then pull them apart.',
       'Put a small drop of CA glue in each pocket and press the magnets in with the <b>faces that were touching facing DOWN</b>. That puts opposite poles down, so the band only fits the dock one way.',
       'They sit <b>flush</b> with the pocket rims (the cell rests on them). Wipe off any glue that squeezes out.'],
      p=[('p_cover','1x','cover'),('p_mag4','2x','Ø4×1.5 magnet')],lab=[('m1','A','#e63946'),('m2','B','#e63946')],
      boxes=[('warn','Steel tweezers will grab the magnets. Use plastic tweezers or a toothpick, and keep the spare magnet away from the bed.')])))

# ---------------- B dock
page('B',two(
 step('Pins into the dock PCB',['d_pins'],['Skip this page if your dock is already assembled.','Push the 4 <b>0906-4</b> spring pins into the 4 holes at the end of the dock PCB, flange flat on the board.','Solder each from underneath with a little solder. The GND pin takes a few seconds longer.','Flash the dock now (once): plug in USB-C, copy <b>debugprobe.uf2</b> onto the RPI-RP2 drive. The USB LED lights.'],
      p=[('p_dpcb','1x','dock PCB'),('p_dpin','4x','0906-4 pin')],boxes=[('tip','Flash before fitting the top: the case has no BOOTSEL hole.')]),
 step('PCB into the tray',['d_tray'],['Lower the PCB into the tray, USB-C end first into its opening.','It sits against the two rear stops so a USB plug can’t push it back.'],p=[('p_dtray','1x','tray')])))
page('B',two(
 step('Magnets into the dock top',['d_magnets'],['Turn the top plate over.','Find which way each magnet goes <b>using your printed band cover</b>: put a Ø4 magnet on the band cover’s wrist face over magnet A (A is nearer the end without the screw hole; in the dock, A is the pocket nearer the USB-C socket). It snaps on. The face that touches the cover goes <b>into the pocket first</b>.','Repeat for B with the second magnet.','Press each into its pocket with a small drop of CA glue.','Before the glue sets, try the cover in the recess: it must pull in one way round and push away when turned end for end.'],
      p=[('p_dtop','1x','dock top'),('p_mag4','2x','Ø4×1.5 magnet')],lab=[('m1','A','#e63946'),('m2','B','#e63946')],
      boxes=[('warn','Don’t let glue reach the recess face or the pin slots.')]),
 step('Close the dock',['d_top'],['Hold the top plate <b>steeply tilted</b> (about 50°), its left end down by the back-left corner.','Hook it over the little <b>hook</b> on the tray’s back-left corner.','Swing the right end down, guiding the 4 spring pins up through their holes, and press until the <b>clip</b> at the back-right corner snaps.','Don’t glue the top: it comes off for re-flashing.'],
      lab=[('hook','hook','#8e5bd3')],boxes=[('tip','To re-flash: pull the right end of the top up firmly to unsnap the clip, then unhook the left end at about 50°.')])))
page('B',one(
 step('Feet',['d_feet'],['Turn the dock over.','Stick a rubber foot inside each of the 4 rings.','The two small holes in the back wall show the status LEDs.'],
      p=[('p_feet','4x','rubber foot')])))

# ---------------- C cover
page('C',two(
 step('Heat-set insert',['s_insert'],['Turn the shell inside up.','Set the brass insert on the round boss at the end.','Press it in with the iron at about <b>230 °C</b>, slowly and straight, until it is <b>flush</b> with the end of the boss.','Let it cool before touching.'],
      p=[('p_insert','1x','M2 insert')],boxes=[('tip','A spare M2 screw in the insert keeps it straight while you press.')]),
 step('Free a contact carrier',['p_carrier'],['Cut (don’t snap) one carrier out of the panel at its two tabs.','File or sand the tab stubs flush so it drops into its pocket.','Clean with IPA.'],p=[('p_carrier','1x','carrier panel')],
      boxes=[('tip','The carrier is the same both ways round: either end can go either way.')],imgcls='small')))
page('C',two(
 step('Pins into the carrier',['s_pins'],['Put a <b>small dab of solder paste</b> on each of the 4 top pads.','Rest the carrier on a scrap of perfboard (holes under the pins) so the tails hang free.','Drop the 4 <b>0906-2</b> pins in, <b>tail first</b>, flanges flat on the paste.'],
      p=[('p_carrier','1x','carrier'),('p_pin','4x','0906-2 pin')],lab=[('paste','paste','#6c757d'),('tail','tail = contact','#e8a400')]),
 step('Reflow and check',['s_reflow'],['Heat on a hotplate (or hot air from above) until the paste flows. Let it cool without moving it.','Clean with IPA.','Under a loupe: every <b>tail end is bare</b> (no solder, no flux).','Meter: the two outer pins and the two inner pins must <b>not</b> beep to each other.'],
      boxes=[('warn','The tails are what the dock’s pins touch. Solder or flux on a tail = no charging.'),('tip','Only an iron? Solder each flange from the top with very little solder, tails pointing up.')])))
page('C',two(
 step('Carrier into the cover',['s_carrier'],['Stand the cover on a flat table, wrist face down (not on the dock).','Lay the carrier in its slot beside the round motor seat, pins up, tails down into the 4 little windows.','It should drop in and sit flat. If it doesn’t, sand the carrier’s ends a bit more.'],
      p=[('p_cover','1x','cover with magnets')]),
 step('Seal with gel epoxy',['s_epoxy'],['Run a small bead of <b>gel</b> epoxy round the inside edge of the carrier and over the 4 solder joints.','Keep it off the moving tops (plungers) of the pins.','Let it cure fully.'],
      boxes=[('warn','Use a thick gel epoxy. A runny one wicks under the carrier and coats the contact tails.')])))
page('C',one(
 step('Check the contacts on the dock',['s_cover_dock'],['Set the cover (no board yet) in the dock. The magnets pull it in one way round.','With a meter, check each of the dock’s 4 pins beeps to the pin above it in the carrier.','Slide the cover about 0.3 mm each way: every contact should still beep.','If one drops out, the dock recess is a bit loose: see the 2026-11-08 review notes and reprint the dock top tighter.'],
      boxes=[('check','4 of 4 beep, also when you wiggle the cover = good.')])))

# ---------------- D board
page('D',two(
 step('Sand the tab nubs',['p_board'],['The board comes from a panel. Sand the small tab nubs flush on the long edges (top edge near the dock end, bottom edge in two places) so it drops into the case.','Don’t sand into the board itself.','Clean off the dust with IPA.'],p=[('p_board','1x','band PCB')]),
 step('Turn it over',['t_board_back'],['The <b>back</b> of the board has no parts. It faces your wrist.','Only 9 gold spots are exposed on it: 4 round dock contacts, 2 square battery pads, 2 oval motor pads and the small JP201 jumper.','The next page shows exactly which is which.'])))
page('D','<h1>Know your pads: back of the board</h1><div class="padfull"><img src="'+im('band-rev-c-back-pads')+'"></div>')
page('D',two(
 step('Solder the battery',['s_battery'],['Board <b>back side up</b>. Lay the cell where it will live (big end towards the antenna end, its wire end by the dock contacts).',
       'Tin TP201 and TP202 with a little solder.','Cut off the JST plug <b>one wire at a time</b>. Trim each wire so it just reaches its pad with a little slack, strip 1.5 mm, tin it.',
       '<b>Red → TP201 (+)</b>, the big square pad. <b>Black → TP202 (–)</b>, the square pad in the opposite corner. Lay each wire flat and touch with the iron.'],
      p=[('p_cell','1x','60 mAh cell')],lab=[('p','+  red','#d62828'),('n','–  black','#222')],
      boxes=[('stop','Never cut both battery wires at once, and never let them touch.')]),
 step('Solder the motor',['s_motor'],['The motor sits next to the cell, by the dock contacts, with its leads towards the two oval pads.','Tin TP501 and TP502. Trim the motor leads to length and tin the ends.',
       'Red lead → <b>TP501</b>, other lead → <b>TP502</b>. (The motor is driven back and forth, so swapping them does no harm.)','Leave the motor free for now: it gets stuck to the cover later.'],
      p=[('p_lra','1x','VG0832012 motor')],lab=[('p','TP501 + TP502','#7b2cbf')],
      boxes=[('tip','The motor leads are thin enamelled wire: tin them with a hot iron and plenty of flux so the enamel burns off.')])))
page('D',two(
 step('Check, then kapton',['s_kapton'],['Meter on DC volts: TP201 (+) to TP202 (–) should read <b>3.0–4.2 V</b>.','Fold the cell and motor aside. Cover the back of the board with one layer of kapton from the antenna end up to just short of the 4 round dock contacts. It covers the solder joints too.','Fold the cell and motor back onto the kapton.'],
      p=[('p_kapton','1','strip of kapton')],lab=[('k','kapton','#c77700'),('dock','keep bare','#0077b6')],
      boxes=[('warn','The 4 round dock contacts must stay <b>bare</b>: the spring pins press on them.'),('tip','Reads 0 V? Some protected cells ship “asleep”. It wakes the first time the band sits on the dock.')]),
 step('Board into the shell',['s_board_shell'],['Put the shell on the table <b>inside up</b> (outer face down).','Lower the board in <b>parts side first</b>, so the back with the cell and motor faces up.','It drops into its pocket; the antenna end goes to the end without the screw boss.'])))

# ---------------- E close
page('E',two(
 step('Cell and motor in place',['s_stack'],['Lay the cell flat on the kapton, centred in the shell (17.25 × 10 × 5.05 mm cell).','Stand the motor on the kapton next to it, by the dock contacts, round face up.','Tuck the wires so nothing sits on the 4 dock contacts.'],
      boxes=[('check','Nothing sticks up above the shell’s rim except the cell and motor.')]),
 step('Tape (no foam) and motor tape',['s_foam'],['Stick one strip of <b>thin</b> double-sided tape (0.15 mm max) across the two magnets in the cover’s battery bay. <b>No foam</b>: the case has 0.45 mm of room over the cell and foam stops it closing.','Peel the liner off the motor’s sticky face (or add a piece of double-sided tape) so it sticks to the round seat in the cover when you close it.'],
      p=[('p_foam','1x','thin tape')],lab=[('ped','motor seat','#555')])))
page('E',two(
 step('Close the band',['s_close'],['Hold the cover <b>wrist face up</b> above the shell, <b>tilted</b>, the end without the screw hole lowest.','Tuck that end in first: the <b>hook lip</b> along the cover’s end goes in under the shell’s end wall.','Swing the screw end down. The hook pulls itself in; nothing slides. The spring pins land on the board’s dock contacts at the end of the swing.','Press gently until the gap closes all round. Don’t force it: check for a pinched wire.'],
      lab=[('hook','hook','#8e5bd3')],boxes=[('tip','To open it later: take the screw out and lift the screw end. The cover unhooks once it is tilted about 40°.')]),
 step('Screw it shut',['s_screw'],['Fit the <b>M2 × 6 countersunk screw</b> through the hole by the strap loop into the insert.','Tighten until snug. The head ends just below the surface.'],
      p=[('p_screw','1x','M2×6 screw')],boxes=[('warn','Snug, not tight: the case is plastic.')])))

# ---------------- F finish
page('F',two(
 step('Add the strap',['strap'],['Thread your sewn 16 mm strap through both loops (patterns in <code>hardware/strap/</code>).','The strap must not pass under the case: the wrist contacts and the motor sit on your skin.']),
 step('First charge and firmware',['d_band'],['Set the band in the dock, wrist side down. The magnets pull it in one way only.','Plug the dock into USB-C. The band starts charging at 30 mA (about 2 h from flat).','Flash the firmware through the dock’s debug probe (see <code>firmware/README.md</code>). After that the band’s LED shows charging through the shell.'],
      boxes=[('check','Tilt and tap the dock: the band must stay seated.')])))
page('F',f'''<h1>Done!</h1><div class="done"><img src="{im('s_done_top')}"><img src="{im('s_done_wrist')}"><img src="{im('s_xray')}"></div>
<div class="cols3 small"><div><h2>Doesn’t charge</h2><ul><li>Check the band sits flat in the dock (one way round).</li><li>Meter each dock pin to the tail above it (step 14).</li><li>Solder or flux on a tail? Clean with IPA.</li></ul></div>
<div><h2>Band seems dead</h2><ul><li>Measure the cell before closing: 3.0–4.2 V at TP201/TP202.</li><li>A sleeping protected cell wakes on the dock.</li><li>No firmware yet = no LED and no buzz.</li></ul></div>
<div><h2>Doesn’t fit</h2><ul><li>Sand the board’s tab nubs.</li><li>Pinched wire under the cover: open and re-route.</li><li>Band too tight in the dock: set <code>REC_CLR</code> to 0.2 and reprint the dock top.</li><li>Hook won’t go in: set <code>CLR</code> to 0.2 in <code>rev-d/case/case_rev_d.py</code>, rebuild rev E and reprint the shell.</li><li>Won’t close: no foam under the cell, tape 0.15 mm max, wires not under the cell.</li></ul></div></div>''')

# ---------------- debugging (dock pinout + bring-up measurements, src/debugpage.py)
import debugpage
page('F',debugpage.body(im('dock-pinout')))

CSS=open('guide.css').read()+debugpage.CSS
open('guide.html','w').write(f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{"".join(pages)}</body></html>')
print(len(pages),'pages',stepno[0],'steps')
