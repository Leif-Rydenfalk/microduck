import sys
sys.path.insert(0, '/Users/leifrydenfalk/dev/ce-workshop/ce-cad')
from cecad import meshslice, meshfeatures
REF = '/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck/reference/pollen-microduck-rl/assets/'
OUT = '/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck/out/measure/foot/'
T = meshslice.load(REF+'foot_left.stl', 1000)
meshslice.render(T, OUT+'foot_left_z.png', 'z', [-29.0,-27.5,-26,-23,-20,-18.3,-17.5,-16,-14,-12.8])
meshslice.render(T, OUT+'foot_left_x.png', 'x', [32,36,40,45,50,55,60,64,68])
meshslice.render(T, OUT+'foot_left_y.png', 'y', [-11,-6,0,6,15,24,30,36,41])
S = meshslice.load(REF+'sole_left.stl', 1000)
meshslice.render(S, OUT+'sole_left_z.png', 'z', [-31,-30,-28,-26,-24,-22,-20.5,-19.5,-18.5])
meshslice.render(S, OUT+'sole_left_x.png', 'x', [31,35,40,45,50,55,60,65,69])
meshslice.render(S, OUT+'sole_left_y.png', 'y', [-11,-6,0,8,15,22,30,36,41])
r = meshfeatures.cylinders(REF+'foot_left.stl', scale=1000)
print('FOOT holes:'); [print(h) for h in r['holes']]
print('FOOT bosses:'); [print(h) for h in r['bosses']]
r = meshfeatures.cylinders(REF+'sole_left.stl', scale=1000)
print('SOLE holes:'); [print(h) for h in r['holes']]
print('SOLE bosses:'); [print(h) for h in r['bosses']]
