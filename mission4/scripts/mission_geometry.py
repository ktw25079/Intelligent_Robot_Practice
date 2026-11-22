"""Pure geometry used by the single-process mobile pick-and-place runner."""
import math
import numpy as np

def wrap(a):
    return math.atan2(math.sin(a), math.cos(a))

def tip(q):
    yaw,a,j3,j4=q;b=a+j3;c=b+j4
    r=.024*math.cos(a)+.128*math.sin(a)+.124*math.cos(b)+.126*math.cos(c)
    return np.array([-.08+r*math.cos(yaw),r*math.sin(yaw),.1775-.024*math.sin(a)+.128*math.cos(a)-.124*math.sin(b)-.126*math.sin(c)])

def transform_pose(p, odom_anchor, map_anchor):
    a=map_anchor[2]-odom_anchor[2];dx=p[0]-odom_anchor[0];dy=p[1]-odom_anchor[1]
    return [map_anchor[0]+dx*math.cos(a)-dy*math.sin(a),map_anchor[1]+dx*math.sin(a)+dy*math.cos(a),wrap(p[2]+a)]

class Grid:
    def __init__(self,data):
        self.res=data['resolution'];self.origin=data['origin'];self.wall=np.array(data['wall_distance']);self.free=np.array(data['free_distance'])
    def sample(self,xy,field):
        x=(xy[:,0]-self.origin[0])/self.res;y=self.wall.shape[0]-1-(xy[:,1]-self.origin[1])/self.res
        # Bilinear sampling, including conservative out-of-map values.
        ix=np.floor(x).astype(int);iy=np.floor(y).astype(int)
        ok=(ix>=0)&(iy>=0)&(ix+1<field.shape[1])&(iy+1<field.shape[0])
        out=np.full(len(x),1. if field is self.wall else 0.)
        xx=x[ok]-ix[ok];yy=y[ok]-iy[ok];i=ix[ok];j=iy[ok]
        out[ok]=(1-xx)*(1-yy)*field[j,i]+xx*(1-yy)*field[j,i+1]+(1-xx)*yy*field[j+1,i]+xx*yy*field[j+1,i+1]
        return out
    def clearance(self,start,end):
        xy=np.array([start[:2],end[:2]])
        points=xy[0]+np.linspace(0,1,max(20,int(np.linalg.norm(xy[1]-xy[0])/.02)))[:,None]*(xy[1]-xy[0])
        return float(np.min(self.sample(points,self.free)))
    def match(self,points,seed):
        points=np.asarray(points)
        if len(points)<80:raise RuntimeError('Too few wall returns for localization')
        best=None
        for da in np.arange(-.3,.301,.02):
            a=seed[2]+da;c=math.cos(a);s=math.sin(a)
            rotated=points@np.array([[c,s],[-s,c]])
            for dx in np.arange(-.15,.151,.025):
                for dy in np.arange(-.15,.151,.025):
                    p=[seed[0]+dx,seed[1]+dy,a];e=self.sample(rotated+np.array(p[:2]),self.wall);score=float(np.mean(np.minimum(e,.15)))
                    if best is None or score<best['score']:best={'pose':p,'score':score,'match':float(np.mean(e<.10)),'delta':[dx,dy,da]}
        if best['match']<.92 or best['score']>.025:raise RuntimeError('Map/laser agreement inadequate: '+str(best))
        if abs(best['delta'][0])>.149 or abs(best['delta'][1])>.149 or abs(best['delta'][2])>.299:raise RuntimeError('Localization correction reached search boundary')
        best['pose'][2]=wrap(best['pose'][2]);return best
