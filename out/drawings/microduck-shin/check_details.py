import FreeCAD
from cecad import triad
from cecad.autosheet import detail_regions
p=triad.load(FreeCAD.newDocument('detail_probe'),'part:microduck-shin')
print(detail_regions(p,'right',max_n=3))
