from pathlib import Path
from cecad.vision import screenshot_url
p=Path(__file__).resolve().parent
screenshot_url((p/'iteration-2026-09-08.html').as_uri(), str(p/'iteration-2026-09-08.png'), width=1400, height=1200, verify=False)
