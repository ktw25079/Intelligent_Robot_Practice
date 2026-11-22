#!/usr/bin/env python3
"""Return to A, approach the reset pickup object, stop before gripper closure."""
import time,math
from pick_demo_202302200 import Mission,main

def run_pregrasp_only(self):
    deadline=time.monotonic()+45
    while len(self.s)<4 and time.monotonic()<deadline:self.ros.spin_once(self.n,timeout_sec=.1)
    self.check();self.settle()
    if max(abs(a-b) for a,b in zip(self.q(),[0.,-1.05,1.05,0.]))>.06:raise RuntimeError('Hardware must finish bringup pose before return')
    if not self.arm.wait_for_server(timeout_sec=8) or not self.grip.wait_for_server(timeout_sec=8):raise RuntimeError('Controller action unavailable')
    if self.c.get('rebase_odom_after_confirmed_restart'):self.oa=self.odom()
    self.localize()
    if self.joints()['gripper_left_joint']<.018:self.gripper(False)
    if math.dist(self.pose()[:2],self.c['A'][:2])>.08:
        front=[r for a,r,x,y in self.points() if abs(a)<.6]
        if front and min(front)<.30:
            rear=[r for a,r,x,y in self.points() if abs(a)>2.35]
            if len(rear)<8 or min(rear)<.50:raise RuntimeError('Rear clearance insufficient for initial separation')
            self.phase='initial_separation';self.reverse(.20)
        self.phase='return_A';self.localize();self.navigate(self.c['A'],reverse=True)
    self.phase='pickup_approach';self.navigate(self.c['staging']);self.align();self.localize()
    self.phase='pregrasp_arm';self.arm_to('approach');self.arm_to('lower')
    if self.joints()['gripper_left_joint']<.017:raise RuntimeError('Gripper not open at pregrasp')
    self.completed=True;self.event('pregrasp_complete',pose=self.pose(),joints=self.joints(),voltage=self.voltage())

if __name__=='__main__':
    Mission.run=run_pregrasp_only
    main()
