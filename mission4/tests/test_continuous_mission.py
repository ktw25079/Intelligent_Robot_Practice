import sys,json,math,unittest
from pathlib import Path
from types import SimpleNamespace
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from mission_geometry import Grid,tip,transform_pose
from pick_demo_202302200 import Mission
C=json.loads((ROOT/'mission_config/continuous_mission.json').read_text())

class FakeMission(Mission):
    def __init__(self,fail=None,place_error=False):
        self.c=C;self.s=dict.fromkeys(['scan','odom','joint','power']);self.loaded=False;self.completed=False;self.calls=[];self.phase='preflight';self.floor=None;self.fail=fail;self.place_error=place_error;self.current=[0.,-1.05,1.05,0.];self.arm=self.grip=SimpleNamespace(wait_for_server=lambda **k:True)
    def check(self):pass
    def settle(self):pass
    def voltage(self):return 12.
    def q(self):return self.current
    def joints(self):return {'gripper_left_joint':.019}
    def localize(self):pass
    def pose(self):return C['A']
    def odom(self):return [0.,0.,0.]
    def event(self,*a,**k):pass
    def navigate(self,goal,reverse=False):self.calls.append('navigate')
    def align(self):self.calls.append('align')
    def arm_to(self,name):
        self.calls.append(name)
        if name==self.fail:raise RuntimeError('injected controller failure')
        self.current=C['paths']['stages'][name]['goal'][:]
        if name=='place' and self.place_error:self.current=C['paths']['stages']['carry']['goal'][:]
    def gripper(self,close):self.calls.append('close' if close else 'open');self.loaded=close
    def reverse(self):self.calls.append('reverse')

class Tests(unittest.TestCase):
    def test_near_goal_obstacle_relocalizes_then_aligns_without_forward_motion(self):
        m=FakeMission();poses=iter([[0.,.16,0.],[0.,.045,0.],[0.,.045,1.]])
        m.position=[0.,.20,0.];m.pose=lambda:m.position
        m.localize=lambda:setattr(m,'position',next(poses))
        targets=[]
        def step(goal,reverse=False):
            targets.append(list(goal))
            if len(targets)<3:raise RuntimeError('Obstacle in forward stopping corridor')
        m.navigate_once=step
        Mission.navigate(m,[0.,0.,1.])
        self.assertEqual(targets[-1],[0.,.045,1.])
    def test_sensor_failure_is_not_navigation_retry(self):
        m=FakeMission();m.pose=lambda:[0.,0.,0.]
        def fail(*args,**kwargs):raise RuntimeError('Stale sensor feedback')
        m.navigate_once=fail
        with self.assertRaisesRegex(RuntimeError,'Stale sensor'):Mission.navigate(m,[.1,0.,0.])
    def test_observed_carry_requires_confirmed_pose_and_height(self):
        import copy
        m=FakeMission();m.c=copy.deepcopy(C)
        ref=json.loads((ROOT/'taught_poses/carry_user_confirmed_run06.json').read_text())
        m.c['observed_carry']=ref;m.loaded=True;m.floor=(.2129270146366741,.17640779060684864)
        m.current=[ref['joints'][k] for k in C['paths']['joint_names']]
        self.assertTrue(m.observed_endpoint_ok('carry'))
        m.loaded=False;self.assertFalse(m.observed_endpoint_ok('carry'));m.loaded=True
        m.floor=(float(tip(m.current)[2])-.01,m.floor[1])
        self.assertFalse(m.observed_endpoint_ok('carry'))
    def test_placement_acceptance_rejects_raised_object(self):
        m=FakeMission();m.floor=(float(tip(C['paths']['stages']['place']['goal'])[2]),sum(C['paths']['stages']['place']['goal'][1:]))
        m.current=C['paths']['stages']['place']['goal'][:]
        self.assertTrue(m.observed_endpoint_ok('place'))
        m.current=C['paths']['stages']['carry']['goal'][:]
        self.assertFalse(m.observed_endpoint_ok('place'))
    def test_pregrasp_request_never_closes_or_lifts(self):
        from return_a_then_pregrasp import run_pregrasp_only
        m=FakeMission();run_pregrasp_only(m)
        self.assertTrue(m.completed)
        self.assertEqual(m.calls,['navigate','align','approach','lower'])
        self.assertFalse(m.loaded)

    def test_run_continues_without_external_resume(self):
        m=FakeMission();m.run();self.assertTrue(m.completed)
        self.assertEqual(m.calls,['navigate','align','approach','lower','close','carry','navigate','place','open','reverse','home'])
    def test_lift_failure_never_transports_or_releases(self):
        m=FakeMission(fail='carry')
        with self.assertRaises(RuntimeError):m.run()
        self.assertEqual(m.calls.count('navigate'),1);self.assertNotIn('open',m.calls);self.assertFalse(m.completed)
    def test_wrong_place_height_keeps_gripper_closed(self):
        m=FakeMission(place_error=True)
        with self.assertRaisesRegex(RuntimeError,'Placement differs'):m.run()
        self.assertNotIn('open',m.calls);self.assertNotIn('reverse',m.calls)
    def test_path_continuity_and_limits(self):
        limits=[(-2.827,2.827),(-1.790,1.570),(-.942,1.382),(-1.790,2.042)]
        for name,s in C['paths']['stages'].items():
            a=np.array([p['positions'] for p in s['points']]);times=np.array([p['time'] for p in s['points']]);self.assertTrue(np.all(np.diff(times)>0));self.assertLess(float(np.max(np.abs(np.diff(a,axis=0)/np.diff(times)[:,None]))),.071)
            for k,(lo,hi) in enumerate(limits):self.assertTrue(np.all((a[:,k]>=lo)&(a[:,k]<=hi)))
        self.assertGreater(tip(C['paths']['stages']['carry']['goal'])[2]-tip(C['paths']['stages']['lower']['goal'])[2],.04)
    def test_map_relocalization_on_recorded_scan(self):
        d=json.loads((ROOT/'tests/fixtures/a_localization_snapshot.json').read_text());anchor=json.loads((ROOT/'mission_config/current_a_verified.json').read_text());seed=[anchor['map_anchor'][k] for k in ('x','y','yaw')];s=d['scan'];pts=[]
        for i,r in enumerate(s['ranges']):
            if r is not None and .3<r<3.5:
                a=s['angle_min']+i*s['angle_increment'];pts.append([-.024+r*math.cos(a),r*math.sin(a)])
        grid=Grid(C['map']);fit=grid.match(pts,seed);self.assertGreater(fit['match'],.95);self.assertLess(math.dist(fit['pose'][:2],seed[:2]),.04)
        self.assertGreaterEqual(grid.clearance(seed,C['staging']),.27)
    def test_transform_anchor_round_trip(self):
        self.assertTrue(np.allclose(transform_pose(C['odom_anchor'],C['odom_anchor'],C['map_anchor']),C['map_anchor']))
if __name__=='__main__':unittest.main()
