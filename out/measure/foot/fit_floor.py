import numpy as np
# sole OUTER bottom along x at y=15 (probe_sole2 C grid, y=15 col)
data_x = [(32,-29.545),(35,-30.997),(38,-31.137),(44,-30.608),(50,-30.091),(56,-29.576),(62,-29.044),(66,-28.367),(69,-26.236)]
# central plane fit x 38..62
X = np.array([p[0] for p in data_x if 38<=p[0]<=62]); Z = np.array([p[1] for p in data_x if 38<=p[0]<=62])
A = np.c_[X, np.ones(len(X))]
m,c = np.linalg.lstsq(A,Z,rcond=None)[0]
print('plane: z = %.5f*x + %.4f  (z(38)=%.3f z(62)=%.3f)'%(m,c,m*38+c,m*62+c))
res = Z-(m*X+c); print('plane residuals', np.round(res,3))
# heel arc: fit circle in x-z through heel points + tangency to plane
heel = np.array([(32,-29.545),(35,-30.997),(38,-31.137)]+[(30.322,-27.5),(30.980,-28.5),(31.947,-29.5),(32.614,-30.0),(29.722,-26.0),(29.606,-25.5),(29.526,-25.0)])
Ah = np.c_[heel[:,0],heel[:,1],np.ones(len(heel))]
bh = (heel**2).sum(1)
s = np.linalg.lstsq(Ah,bh,rcond=None)[0]
cx,cz = s[0]/2, s[1]/2; r = np.sqrt(s[2]+cx*cx+cz*cz)
d = np.abs(np.sqrt((heel[:,0]-cx)**2+(heel[:,1]-cz)**2)-r)
print('heel arc: centre (%.3f,%.3f) R %.3f resid max %.3f'%(cx,cz,r,d.max()))
# toe arc: points from E profile (+x outer wall lower) + toe floor
toe = np.array([(66,-28.367),(69,-26.236),(70.211,-24.0),(70.028,-24.5),(69.804,-25.0),(69.524,-25.5),(69.185,-26.0),(68.773,-26.5),(68.272,-27.0),(67.642,-27.5)])
At = np.c_[toe[:,0],toe[:,1],np.ones(len(toe))]
bt = (toe**2).sum(1)
s = np.linalg.lstsq(At,bt,rcond=None)[0]
cx2,cz2 = s[0]/2, s[1]/2; r2 = np.sqrt(s[2]+cx2*cx2+cz2*cz2)
d = np.abs(np.sqrt((toe[:,0]-cx2)**2+(toe[:,1]-cz2)**2)-r2)
print('toe arc: centre (%.3f,%.3f) R %.3f resid max %.3f'%(cx2,cz2,r2,d.max()))
# y fillet: rises at x50 relative to plane z(50)
rises = [(-9,1.686),(-5,0.052),(35,0.050),(39,1.685)]
# fillet tangent to floor: rise(d) = R - sqrt(R^2-(R-d)^2), d = dist from OUTER wall y=-12/42... try solve R from (d,h)

import math
def solve_R(d,h):
    # h = R - sqrt(R^2-(R-d)^2) -> (R-h)^2 = R^2-(R-d)^2 -> R^2 -2Rh +h^2 = 2Rd - d^2 -> R = (h^2+d^2)/(2(h+d-? )) solve properly:
    # R^2 - 2Rh + h^2 = R^2 - (R-d)^2 => -2Rh + h^2 = -(R^2 -2Rd + d^2 - R^2)?? do algebra numerically
    best=None
    for R in np.arange(2.0,20.0,0.01):
        if d>R: continue
        hh = R - math.sqrt(R*R-(R-d)*(R-d))
        if best is None or abs(hh-h)<best[1]: best=(R,abs(hh-h))
    return best
for dwall in (-12,):
    for y,h in rises[:2]:
        d = y - dwall
        print('front y=%s d=%.2f h=%.3f -> R'%(y,d,h), solve_R(d,h))
for y,h in rises[2:]:
    d = 42 - y
    print('back y=%s d=%.2f h=%.3f -> R'%(y,d,h), solve_R(d,h))
# foot rib bottoms (= sole inner floor = outer+2): verify plane+2
foot = [(38,-29.139),(44,-28.612),(50,-28.091),(56,-27.571),(62,-27.044)]
for x,z in foot:
    print('foot rib bottom x%d: %.3f vs plane+2 %.3f'%(x,z,m*x+c+2))
