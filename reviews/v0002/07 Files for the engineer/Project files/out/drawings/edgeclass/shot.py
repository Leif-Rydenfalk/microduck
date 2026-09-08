import sys, os, re
sys.path.insert(0, "/Users/leifrydenfalk/dev/ce-workshop/ce-cad")
from cecad.vision import screenshot_url
MAXW = int(os.environ.get("SHOT_W", "1300"))
MAXH = int(os.environ.get("SHOT_H", "1300"))
for svg in sys.argv[1:]:
    head = open(svg).read(400)
    w = float(re.search(r'width="([\d.]+)"', head).group(1))
    h = float(re.search(r'height="([\d.]+)"', head).group(1))
    sc = min(MAXW / w, MAXH / h)
    W, H = int(w * sc), int(h * sc)
    holder = os.path.splitext(svg)[0] + "-view.html"
    open(holder, "w").write('<!doctype html><meta charset="utf-8"><style>html,body{margin:0;padding:0;background:#fff}img{display:block;width:100vw;height:auto}</style><img src="%s">' % os.path.basename(svg))
    png = os.path.splitext(svg)[0] + ".png"
    screenshot_url("file://" + os.path.abspath(holder), png, width=W, height=H, verify=False)
    print(png, "%dx%d" % (W, H), os.path.getsize(png), flush=True)
