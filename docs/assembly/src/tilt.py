"""Writes the tilted case parts used by the 'close the band' and 'close the dock' pictures:
r/cover-tilt.stl (band wrist cover hooked in at the antenna end, 25 deg open) and r/dtop-tilt.stl (dock top hooked
in at the back-left, 50 deg open). Needs build123d. usage: python tilt.py"""
import os, sys
H = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../hardware'))
sys.path.insert(0, f'{H}/band/rev-d/case'); sys.path.insert(0, f'{H}/dock/rev-d/case')
sys.argv = sys.argv[:1]
import case_rev_d as band  # noqa: E402
import dock_rev_d as dock  # noqa: E402
from build123d import export_stl  # noqa: E402
os.makedirs('r', exist_ok=True)
export_stl(band.A.to_step_frame(band.swung(band.make_cover(), 25)), 'r/cover-tilt.stl', tolerance=0.02, angular_tolerance=0.2)
export_stl(dock.C.out_frame(dock.swung(dock.make_top(), 50)), 'r/dtop-tilt.stl', tolerance=0.02, angular_tolerance=0.2)
print('ok')
