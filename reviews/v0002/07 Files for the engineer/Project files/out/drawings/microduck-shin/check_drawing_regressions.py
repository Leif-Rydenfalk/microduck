"""Run the shin-discovered regressions and core checker self-tests in one kernel."""
import runpy
from pathlib import Path
from cecad import pdfsheet,sheetcheck
p=Path(__file__).resolve().parent
for script in ('check_generator_regressions.py','check_detail_regression.py','check_caption_regression.py','check_render_scale_regression.py'):
 print('\nREGRESSION',script,flush=True)
 runpy.run_path(str(p/script),run_name='__main__')
print('\nCORE PDF SELF TEST',flush=True)
pdfsheet.self_test()
print('\nCORE SHEETCHECK SELF TEST',flush=True)
sheetcheck.self_test()
