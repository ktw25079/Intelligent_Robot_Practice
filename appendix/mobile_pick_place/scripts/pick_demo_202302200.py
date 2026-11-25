#!/usr/bin/env python3
"""Single-process mobile six-stage demonstration. No motion without --execute.
The mobile extension differs from the lecture's stationary-arm assignment.
"""
import argparse,json,math,os,signal,tempfile,time
from pathlib import Path
import numpy as np
from mission_geometry import Grid,tip,wrap,transform_pose

class Mission:
    def __init__(self,c):
        import rclpy
        from rclpy.action import ActionClient
        from rclpy.qos import qos_profile_sensor_data
        from geometry_msgs.msg import Twist
        from nav_msgs.msg import Odometry
        from sensor_msgs.msg import LaserScan,JointState
        from control_msgs.msg import DynamicJointState
        from control_msgs.action import FollowJointTrajectory,GripperCommand
        self.ros=rclpy;self.Twist=Twist;self.n=rclpy.create_node('pick_demo_202302200');self.c=c;self.s={};self.loaded=False;self.moving=False;self.active=None;self.pending=None;self.phase='preflight';self.completed=False
        self.pub=self.n.create_publisher(Twist,'/cmd_vel',10)
        for typ,topic,k in [(Odometry,'/odom','odom'),(LaserScan,'/scan','scan'),(JointState,'/joint_states','joint'),(DynamicJointState,'/dynamic_joint_states','power')]:
            self.n.create_subscription(typ,topic,lambda m,k=k:self.receive(k,m),qos_profile_sensor_data)
        self.arm=ActionClient(self.n,FollowJointTrajectory,'/arm_controller/follow_joint_trajectory');self.grip=ActionClient(self.n,GripperCommand,'/gripper_controller/gripper_cmd')
        self.grid=Grid(c['map']);self.ma=list(c['map_anchor']);self.oa=list(c['odom_anchor']);self.base_anchor=None;self.arm_hold=None;self.last_zero=0.;self.floor=None
    def event(self,event,**data):print(json.dumps({'time':time.time(),'phase':self.phase,'event':event,**data}),flush=True)
    def receive(self,k,m):
        stamp=m.header.stamp.sec+m.header.stamp.nanosec/1e9
        if abs(time.time()-stamp)<.5:self.s[k]=(m,time.monotonic())
    def joints(self):
        m=self.s['joint'][0];return dict(zip(m.name,m.position))
    def q(self):return [self.joints()[k] for k in self.c['paths']['joint_names']]
    def voltage(self):
        m=self.s['power'][0]
        for k,v in zip(m.joint_names,m.interface_values):
            if k=='battery':return dict(zip(v.interface_names,v.values))['voltage']
        raise RuntimeError('Battery feedback missing')
    def odom(self):
        p=self.s['odom'][0].pose.pose;q=p.orientation
        return [p.position.x,p.position.y,math.atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y*q.y+q.z*q.z))]
    def pose(self):return transform_pose(self.odom(),self.oa,self.ma)
    def check(self):
        if len(self.s)!=4 or any(time.monotonic()-v[1]>.8 for v in self.s.values()):raise RuntimeError('Stale sensor feedback')
        if self.voltage()<=11.:raise RuntimeError('Battery reached 11V stop threshold')
        if self.loaded and abs(self.joints()['gripper_left_joint']-self.contact)>.003:raise RuntimeError('Grip changed during loaded motion')
        if self.loaded and self.moving and self.floor is not None and float(tip(self.q())[2])-self.floor[0]<self.minimum_lift():raise RuntimeError('Load height dropped during transport')
        if self.moving and self.arm_hold is not None and max(abs(a-b) for a,b in zip(self.q(),self.arm_hold))>.06:raise RuntimeError('Arm moved during base motion')
        if not self.moving and self.base_anchor is not None:
            p=self.odom()
            if math.dist(p[:2],self.base_anchor[:2])>.015 or abs(wrap(p[2]-self.base_anchor[2]))>.05:raise RuntimeError('Base moved during arm operation')
    def tick(self):
        self.ros.spin_once(self.n,timeout_sec=.02);self.check()
        if not self.moving and time.monotonic()-self.last_zero>.1:self.pub.publish(self.Twist());self.last_zero=time.monotonic()
    def pause(self,seconds):
        end=time.monotonic()+seconds
        while time.monotonic()<end:self.tick()
    def stop(self):
        for _ in range(20):self.pub.publish(self.Twist());self.ros.spin_once(self.n,timeout_sec=.02)
    def settle(self):
        self.moving=False;self.base_anchor=None;end=time.monotonic()+5;stable=None
        while time.monotonic()<end:
            self.tick();v=self.s['odom'][0].twist.twist
            if abs(v.linear.x)<.004 and abs(v.angular.z)<.02:
                stable=stable or time.monotonic()
                if time.monotonic()-stable>.5:self.base_anchor=self.odom();return
            else:stable=None
        raise RuntimeError('Base did not settle')
    def points(self,mask_payload=True):
        s=self.s['scan'][0];pts=[]
        for i,r in enumerate(s.ranges):
            if not math.isfinite(r) or not s.range_min<r<s.range_max:continue
            a=wrap(s.angle_min+i*s.angle_increment)
            if mask_payload and self.loaded and -.25<a<.06 and .12<r<.19:continue
            pts.append((a,r,-.024+r*math.cos(a),r*math.sin(a)))
        if len(pts)<30:raise RuntimeError('Insufficient laser returns')
        return pts
    def localize(self):
        self.settle();pts=[[p[2],p[3]] for p in self.points() if .3<p[1]<3.5];fit=self.grid.match(pts,self.pose())
        # Refresh queued samples after the CPU-only map fit.
        for _ in range(40):self.ros.spin_once(self.n,timeout_sec=0.)
        self.check();self.ma=fit['pose'];self.oa=self.odom();self.event('localized',fit=fit)
    def navigate_once(self,goal,reverse=False):
        start=self.pose();required=.35 if self.loaded else .27
        clearance=self.grid.clearance(start,goal)
        if clearance<required:raise RuntimeError('Map route clearance insufficient: '+str(clearance))
        self.arm_hold=self.q();self.moving=True;self.base_anchor=None;origin=self.odom();budget=math.dist(start[:2],goal[:2])+0.35;deadline=time.monotonic()+100;speed=0.;last=time.monotonic();report=0.
        try:
            while time.monotonic()<deadline:
                self.tick();p=self.pose();d=math.dist(p[:2],goal[:2]);m=self.Twist();pts=self.points();near=min(x[1] for x in pts)
                if math.dist(self.odom()[:2],origin[:2])>budget:raise RuntimeError('Navigation travel limit exceeded')
                if near<.22:raise RuntimeError('Obstacle inside body boundary')
                if d>.03:
                    heading=wrap(math.atan2(goal[1]-p[1],goal[0]-p[0])+(math.pi if reverse else 0.)-p[2])
                    if abs(heading)>.04:m.angular.z=math.copysign(min(.20,max(.07,abs(heading)*.7)),heading)
                    if abs(heading)<.18:m.linear.x=(-1. if reverse else 1.)*min(.05 if self.loaded else .10,max(.018,d*.4))
                else:
                    heading=wrap(goal[2]-p[2])
                    if abs(heading)<.04:return
                    m.angular.z=math.copysign(min(.20,max(.07,abs(heading)*.7)),heading)
                if m.angular.z and near<(.35 if self.loaded else .30):raise RuntimeError('Turning clearance insufficient')
                # Swept forward corridor in base coordinates; no unmasked forward obstacle is ignored.
                length=.42 if self.loaded else .32;width=.25 if self.loaded else .23
                if m.linear.x>0 and any(0<x<length and abs(y)<width for a,r,x,y in pts):raise RuntimeError('Obstacle in forward stopping corridor')
                if m.linear.x<0:
                    rear=[r for a,r,x,y in pts if abs(a)>2.35]
                    if len(rear)<8 or min(rear)<.35:raise RuntimeError('Obstacle in rear stopping corridor')
                now=time.monotonic();dt=min(.1,now-last);last=now
                target=abs(m.linear.x);m.linear.x=math.copysign(min(target,abs(speed)+(.05 if self.loaded else .1)*dt),m.linear.x);speed=m.linear.x;self.pub.publish(m)
                if now-report>2:self.event('navigation',pose=p,distance=d,voltage=self.voltage());report=now
            raise RuntimeError('Navigation timeout')
        finally:self.stop();self.settle()
    def navigate(self,goal,reverse=False):
        for attempt in range(3):
            p=self.pose()
            # Inside the arrival radius, align heading without unnecessary translation.
            target=[*p[:2],goal[2]] if math.dist(p[:2],goal[:2])<=.05 else goal
            try:self.navigate_once(target,reverse=reverse)
            except RuntimeError as e:
                # A nearby side wall can enter the conservative forward corridor as
                # odometry drifts. Stop, rematch the scan, then replan; never ignore it.
                if str(e)!='Obstacle in forward stopping corridor' or math.dist(self.pose()[:2],goal[:2])>.25:raise
                self.event('near_goal_relocalization',attempt=attempt+1)
            self.localize();p=self.pose()
            if math.dist(p[:2],goal[:2])<=.05 and abs(wrap(p[2]-goal[2]))<=.10:self.event('navigation_complete',pose=p);return
            self.event('navigation_correction',attempt=attempt+1,pose=p)
        raise RuntimeError('Goal not reached after bounded localization corrections')
    def surface(self):
        pts=sorted(p for p in self.points(False) if abs(p[0])<.60 and .10<p[1]<.65);groups=[];group=[]
        for p in pts:
            if group and (p[0]-group[-1][0]>.045 or math.dist(p[2:],group[-1][2:])>.055):
                if len(group)>=3:groups.append(group)
                group=[]
            group.append(p)
        if len(group)>=3:groups.append(group)
        if not groups:raise RuntimeError('Pickup object not isolated')
        g=min(groups,key=lambda g:sum(p[1] for p in g)/len(g));width=math.dist(g[0][2:],g[-1][2:])
        if not .012<width<.10:raise RuntimeError('Pickup scan width inconsistent')
        return np.mean([[p[2]+.024,p[3]] for p in g],axis=0),min(p[1] for p in g)
    def align(self):
        self.arm_hold=self.q();self.base_anchor=None;self.moving=True;start=self.odom();end=time.monotonic()+55;stable=None
        try:
            while time.monotonic()<end:
                self.tick();xy,r=self.surface();dx,dy=xy-np.array(self.c['surface_reference']);p=self.odom();m=self.Twist()
                if math.dist(p[:2],start[:2])>.40:raise RuntimeError('Alignment travel limit')
                if r<.132 or dx<-.008:raise RuntimeError('Object too close')
                if abs(dx)<.005 and abs(dy)<.008:
                    stable=stable or time.monotonic()
                    if time.monotonic()-stable>.5:self.event('aligned',surface=xy.tolist());return
                else:
                    stable=None
                    if dx<.045:
                        if abs(dy)>.012:raise RuntimeError('Pickup lateral mismatch')
                        if dx>.004:m.linear.x=.015
                    else:
                        heading=math.atan2(dy,dx)
                        if abs(heading)>.03:m.angular.z=math.copysign(min(.08,max(.05,abs(heading)*.6)),heading)
                        if abs(heading)<.15:m.linear.x=.02
                if any(abs(a)>.6 and r<.18 for a,r,x,y in self.points(False)):raise RuntimeError('Side obstacle during alignment')
                self.pub.publish(m)
            raise RuntimeError('Alignment timeout')
        finally:self.stop();self.settle()
    def wait(self,f,timeout):
        end=time.monotonic()+timeout
        while not f.done() and time.monotonic()<end:self.tick()
        if not f.done():raise RuntimeError('Action timed out')
        return f.result()
    def action(self,client,goal,timeout):
        self.pending=client.send_goal_async(goal);self.active=self.wait(self.pending,8);self.pending=None
        if not self.active.accepted:raise RuntimeError('Action rejected')
        result=self.wait(self.active.get_result_async(),timeout);self.active=None;return result
    def minimum_lift(self):
        return .02 if self.c.get('observed_carry',{}).get('user_confirmed_clear_of_floor_and_suitable_for_transport') else .025
    def observed_endpoint_ok(self,name):
        if self.floor is None:return False
        q=self.q()
        if name=='carry':
            ref=self.c.get('observed_carry',{})
            if not ref.get('user_confirmed_clear_of_floor_and_suitable_for_transport') or not self.loaded:return False
            target=[ref['joints'][k] for k in self.c['paths']['joint_names']]
            return (max(abs(a-b) for a,b in zip(q,target))<=.02
                    and math.dist(tip(q),tip(target))<=.008
                    and abs(sum(q[1:])-sum(target[1:]))<=.04
                    and float(tip(q)[2])-self.floor[0]>=self.minimum_lift())
        if name=='place':
            target=self.c['paths']['stages']['place']['goal']
            return (max(abs(a-b) for a,b in zip(q,target))<=.06
                    and math.dist(tip(q)[:2],tip(target)[:2])<=.008
                    and abs(float(tip(q)[2])-self.floor[0])<=.008
                    and abs(sum(q[1:])-self.floor[1])<=.04)
        return False
    def arm_to(self,name):
        from control_msgs.action import FollowJointTrajectory
        from trajectory_msgs.msg import JointTrajectoryPoint
        from builtin_interfaces.msg import Duration
        stage=self.c['paths']['stages'][name];q=self.q()
        if max(abs(a-b) for a,b in zip(q,stage['start']))>.06:raise RuntimeError('Arm differs from validated start: '+name)
        g=FollowJointTrajectory.Goal();g.trajectory.joint_names=self.c['paths']['joint_names'];g.goal_time_tolerance=Duration(sec=5)
        p=JointTrajectoryPoint();p.positions=q;p.velocities=[0.]*4;g.trajectory.points=[p]
        for pt in stage['points']:
            p=JointTrajectoryPoint();p.positions=pt['positions'];p.velocities=pt['velocities'];t=pt['time']+1.;sec=int(t);p.time_from_start=Duration(sec=sec,nanosec=int((t-sec)*1e9));g.trajectory.points.append(p)
        self.event('arm_start',name=name);r=self.action(self.arm,g,stage['duration']+15)
        succeeded=r.status==4 and r.result.error_code==0
        endpoint_timeout=r.status==6 and r.result.error_code==-5
        if not succeeded and not endpoint_timeout:raise RuntimeError('Arm action failed: '+str(r))
        self.pause(.5)
        if not succeeded or max(abs(a-b) for a,b in zip(self.q(),stage['goal']))>.035:
            # Only a settled goal-tolerance failure may use a physically taught endpoint.
            for _ in range(5):
                if not self.observed_endpoint_ok(name):raise RuntimeError('Arm endpoint outside taught task bounds: '+name)
                self.pause(.1)
            self.event('observed_endpoint_accepted',name=name,controller_status=r.status,actual=self.q())
        self.event('arm_complete',name=name,actual=self.q(),tip=tip(self.q()).tolist())
    def gripper(self,close):
        from control_msgs.action import GripperCommand
        g=GripperCommand.Goal();g.command.position=self.c['paths']['gripper_close_command'] if close else .019;g.command.max_effort=-1.
        r=self.action(self.grip,g,15);self.pause(.5);position=self.joints()['gripper_left_joint']
        if close:
            if abs(position-self.c['paths']['gripper_taught_contact'])>.004 or not ((r.status==4 and r.result.reached_goal) or (r.status==6 and r.result.stalled)):raise RuntimeError('Grasp contact not detected')
            self.contact=position;self.loaded=True
        else:
            if r.status!=4 or position<.017:raise RuntimeError('Gripper failed to open')
            self.loaded=False
        self.event('gripper_complete',close=close,position=position,status=r.status)
    def reverse(self,distance=.10):
        self.arm_hold=self.q();self.moving=True;self.base_anchor=None;start=self.odom();deadline=time.monotonic()+15
        try:
            while time.monotonic()<deadline:
                self.tick();p=self.odom();delta=np.array(p[:2])-np.array(start[:2]);d=-delta@np.array([math.cos(start[2]),math.sin(start[2])])
                if abs(wrap(p[2]-start[2]))>.08:raise RuntimeError('Reverse heading drift')
                rear=[r for a,r,x,y in self.points() if abs(a)>2.35]
                if len(rear)<8 or min(rear)<.30:raise RuntimeError('Rear path obstructed')
                if d>=distance-.002:self.event('retreat_complete',distance=d);return
                m=self.Twist();m.linear.x=-.025;self.pub.publish(m)
            raise RuntimeError('Reverse timeout')
        finally:self.stop();self.settle()
    def run(self):
        deadline=time.monotonic()+45
        while len(self.s)<4 and time.monotonic()<deadline:self.ros.spin_once(self.n,timeout_sec=.1)
        self.check();self.settle()
        if self.voltage()<11.5:raise RuntimeError('Charge battery before starting full continuous mission (minimum 11.5V at start)')
        if max(abs(a-b) for a,b in zip(self.q(),[0.,-1.05,1.05,0.]))>.06:raise RuntimeError('Start requires bringup pose')
        if not self.arm.wait_for_server(timeout_sec=8) or not self.grip.wait_for_server(timeout_sec=8):raise RuntimeError('Controller action unavailable')
        if self.c.get('rebase_odom_after_confirmed_restart'):
            self.oa=self.odom();self.event('odom_rebased_after_confirmed_restart',odom=self.oa)
        self.localize();self.event('mission_start',voltage=self.voltage())
        if math.dist(self.pose()[:2],self.c['A'][:2])>.08:
            front=[r for a,r,x,y in self.points() if abs(a)<.6]
            if front and min(front)<.30:
                rear=[r for a,r,x,y in self.points() if abs(a)>2.35]
                if len(rear)<8 or min(rear)<.50:raise RuntimeError('Rear clearance insufficient for initial separation')
                self.phase='initial_separation';self.reverse(.20);self.localize()
            self.phase='return_to_A_before_trial';self.navigate(self.c['A'],reverse=True)
        self.phase='1_approach';self.navigate(self.c['staging']);self.align();self.localize()
        # No wheel commands after alignment until the load is lifted.
        if self.joints()['gripper_left_joint']<.018:self.gripper(False)
        self.arm_to('approach')
        self.phase='2_lower';self.arm_to('lower');self.floor=(float(tip(self.q())[2]),sum(self.q()[1:]));self.event('floor_reference',z=self.floor[0],pitch=self.floor[1])
        self.phase='3_grasp';self.gripper(True)
        self.phase='4_lift';self.arm_to('carry')
        height=float(tip(self.q())[2])-self.floor[0]
        if height<self.minimum_lift():raise RuntimeError('Insufficient lift height')
        self.event('lift_verified',tool_height_gain=height)
        self.phase='5_transfer';self.localize();self.navigate(self.c['B'])
        self.phase='6_place_retreat';self.arm_to('place')
        if abs(float(tip(self.q())[2])-self.floor[0])>.008 or abs(sum(self.q()[1:])-self.floor[1])>.04:raise RuntimeError('Placement differs from calibrated floor pose; release withheld')
        # The flat-floor height is taught and previously observed; this is not a force/contact sensor.
        self.loaded=False
        self.gripper(False);self.reverse();self.arm_to('home');self.completed=True;self.event('six_stage_complete',pose=self.pose(),voltage=self.voltage())
    def close(self):
        if self.pending is not None:
            end=time.monotonic()+3
            while not self.pending.done() and time.monotonic()<end:self.ros.spin_once(self.n,timeout_sec=.02)
            if self.pending.done():self.active=self.pending.result()
        if self.active is not None and self.active.accepted:
            f=self.active.cancel_goal_async();end=time.monotonic()+3
            while not f.done() and time.monotonic()<end:self.ros.spin_once(self.n,timeout_sec=.02)
        self.stop()
        if len(self.s)==4:
            scan=self.s['scan'][0];self.event('final_state',completed=self.completed,odom=self.odom(),map_pose=self.pose(),joints=self.joints(),voltage=self.voltage(),scan={'angle_min':scan.angle_min,'angle_increment':scan.angle_increment,'range_min':scan.range_min,'range_max':scan.range_max,'ranges':[v if math.isfinite(v) else None for v in scan.ranges]})
        self.n.destroy_node()

def main():
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--execute',action='store_true');args=p.parse_args();c=json.loads(Path(args.config).read_text())
    if not c.get('paths_validated') or not c.get('object_reset_confirmed'):raise RuntimeError('Validated paths and reset object required')
    if not args.execute:print('CONFIG CHECK ONLY: six-stage configuration loaded; no ROS commands sent');return
    peers=''.join('<locator><udpv4><address>127.0.0.1</address><port>'+str(8410+2*i)+'</port></udpv4></locator>' for i in range(60))
    profile=tempfile.NamedTemporaryFile(mode='w',suffix='.xml',delete=False);profile.write('<?xml version="1.0"?><profiles xmlns="http://www.eprosima.com/XMLSchemas/fastRTPS_Profiles"><participant profile_name="mission_peers" is_default_profile="true"><rtps><builtin><initialPeersList>'+peers+'</initialPeersList></builtin></rtps></participant></profiles>');profile.close();os.environ['FASTRTPS_DEFAULT_PROFILES_FILE']=profile.name
    import rclpy
    rclpy.init();mission=Mission(c)
    def interrupt(*_):raise KeyboardInterrupt('Interrupted')
    signal.signal(signal.SIGTERM,interrupt);signal.signal(signal.SIGINT,interrupt)
    try:mission.run()
    except BaseException as e:mission.event('mission_stopped',reason=str(e));raise
    finally:mission.close();rclpy.shutdown();os.unlink(profile.name)
if __name__=='__main__':main()
