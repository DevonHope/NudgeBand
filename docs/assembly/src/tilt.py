"""Writes the tilted case parts used by the 'close the band' and 'close the dock' pictures:
r/cover-tilt.stl (band wrist cover rev E hooked in at the antenna end, 25 deg open) and r/dtop-tilt.stl (dock top rev D
hooked in at the back-left, 50 deg open). Needs build123d. usage: python tilt.py
The band (rev E) and dock (rev D) scripts each load their own copy of rev A's case module, so they run in two processes."""
import os, subprocess, sys
H = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../hardware'))
if len(sys.argv) == 1:
    os.makedirs('r', exist_ok=True)
    for part in ('band', 'dock'):
        subprocess.run([sys.executable, __file__, part], check=True)
    sys.exit()
from build123d import export_stl  # noqa: E402
if sys.argv[1] == 'band':
    sys.path.insert(0, f'{H}/band/rev-e/case')
    import case_rev_e as band  # noqa: E402
    export_stl(band.A.to_step_frame(band.D.swung(band.make_cover(), 25)), 'r/cover-tilt.stl', tolerance=0.02, angular_tolerance=0.2)
else:
    sys.path.insert(0, f'{H}/dock/rev-d/case')
    import dock_rev_d as dock  # noqa: E402
    export_stl(dock.C.out_frame(dock.swung(dock.make_top(), 50)), 'r/dtop-tilt.stl', tolerance=0.02, angular_tolerance=0.2)
