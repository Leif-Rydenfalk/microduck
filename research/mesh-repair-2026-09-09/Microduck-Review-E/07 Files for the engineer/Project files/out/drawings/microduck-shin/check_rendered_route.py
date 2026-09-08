import sys
from pathlib import Path
root=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(root/'tools'))
from rendered_drawing import draw_rendered
draw_rendered('microduck-shin',outdir=Path(__file__).resolve().parent/'render-panel-next')
