#!/usr/bin/env python3
"""Lecture11 Mission4: stationary six-stage pick/place, upward retreat and home.
Default performs live planning checks only; --execute runs the sequence.
Use the taught 5x5x10cm box and align its faces with the gripper."""
import argparse
import json
import math
from pathlib import Path
import signal
import sys
import time

JOINTS = ['joint1', 'joint2', 'joint3', 'joint4']
WHEELS = ['wheel_left_joint', 'wheel_right_joint']
POSES = ['home', 'approach', 'lower', 'lift', 'transfer', 'place', 'retreat']
LIMITS = [(-.9*math.pi,.9*math.pi),(-.57*math.pi,.5*math.pi),
          (-.3*math.pi,.44*math.pi),(-.57*math.pi,.65*math.pi)]
SEQUENCE = [('arm','home'),('gripper','open'),('arm','approach'),
            ('arm','lower'),('gripper','close'),('arm','lift'),
            ('arm','transfer'),('arm','place'),('gripper','open'),
            ('arm','retreat'),('arm','home')]


def number(value):
    return isinstance(value, (int,float)) and not isinstance(value,bool) and math.isfinite(value)


def pose_errors(name, q):
    if not isinstance(q,list) or len(q)!=4:
        return [f'{name}: joint1~4 실물 관절값 4개가 필요합니다.']
    return [f'{name}/joint{i+1}: 유한한 URDF 범위 내 값이 필요합니다.'
            for i,(v,(lo,hi)) in enumerate(zip(q,LIMITS))
            if not number(v) or not lo<=v<=hi]


def validate(c):
    errors=[]
    if c.get('schema')!=1: errors.append('schema must be 1')
    for name in POSES: errors.extend(pose_errors(name,c.get('poses',{}).get(name)))
    for name in ['open','close']:
        v=c.get('gripper',{}).get(name)
        if not number(v) or not -.010<=v<=.019: errors.append(f'gripper.{name}: 교시한 지령값 필요 (-0.010~0.019m)')
    g=c.get('gripper',{})
    if number(g.get('open')) and number(g.get('close')) and g['open']<=g['close']:
        errors.append('gripper.open must exceed close')
    for key,lo,hi in [('move_seconds',2,60),('max_joint_speed',.01,.15),('settle_seconds',.3,5)]:
        v=c.get(key)
        if not number(v) or not lo<=v<=hi: errors.append(f'{key}: {lo}~{hi} 필요')
    return errors


def save_config(path,c):
    path=Path(path)
    if path.exists():
        backup=path.with_name(path.name+'.backup-'+str(time.time_ns()))
        backup.write_bytes(path.read_bytes())
    tmp=path.with_name(path.name+'.tmp')
    tmp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
    tmp.replace(path)


class Runner:
    def __init__(self, log_path=None):
        import rclpy
        from rclpy.action import ActionClient
        from rclpy.qos import qos_profile_sensor_data
        from sensor_msgs.msg import JointState
        from control_msgs.action import FollowJointTrajectory, GripperCommand
        self.rclpy=rclpy
        self.node=rclpy.create_node('stationary_pick_demo_202302200')
        self.positions={};self.received=0.;self.stamp=0.;self.wheel_anchor=None
        self.active=None;self.pending=None
        self.log_file=open(log_path,'x',buffering=1) if log_path else None
        self.sub=self.node.create_subscription(JointState,'/joint_states',self.receive,qos_profile_sensor_data)
        self.arm=ActionClient(self.node,FollowJointTrajectory,'/arm_controller/follow_joint_trajectory')
        self.grip=ActionClient(self.node,GripperCommand,'/gripper_controller/gripper_cmd')

    def receive(self,msg):
        if len(msg.name)!=len(msg.position) or any(not math.isfinite(v) for v in msg.position):return
        self.positions=dict(zip(msg.name,msg.position))
        self.received=time.monotonic()
        self.stamp=msg.header.stamp.sec+msg.header.stamp.nanosec/1e9

    def event(self,event,**data):
        row=json.dumps(dict(time=time.time(),event=event,**data),ensure_ascii=False)
        print(row,flush=True)
        if self.log_file:self.log_file.write(row+'\n')

    def check(self):
        if time.monotonic()-self.received>1.5 or abs(time.time()-self.stamp)>2:
            raise RuntimeError(f'joint_states stale: receipt_age={time.monotonic()-self.received:.3f}s, stamp_delta={time.time()-self.stamp:.3f}s')
        for name in JOINTS+WHEELS+['gripper_left_joint']:
            if name not in self.positions: raise RuntimeError('관절 피드백 누락: '+name)
        if self.wheel_anchor is not None:
            if any(abs(self.positions[k]-v)>.05 for k,v in zip(WHEELS,self.wheel_anchor)):
                raise RuntimeError('베이스 바퀴 움직임 감지: 정지형 미션 중단')

    def tick(self):
        self.rclpy.spin_once(self.node,timeout_sec=.05)
        self.check()

    def wait_feedback(self):
        deadline=time.monotonic()+30
        while time.monotonic()<deadline:
            self.rclpy.spin_once(self.node,timeout_sec=.1)
            try:self.check();return
            except RuntimeError:pass
        self.check()

    def stable_pose(self):
        self.wait_feedback(); samples=[]
        end=time.monotonic()+.7
        while time.monotonic()<end:
            self.tick();samples.append([self.positions[k] for k in JOINTS])
        if any(max(q[i] for q in samples)-min(q[i] for q in samples)>.015 for i in range(4)):
            raise RuntimeError('팔이 아직 움직입니다. 멈춘 뒤 다시 기록하세요.')
        q=samples[-1]
        if pose_errors('capture',q):raise RuntimeError('관절값이 URDF 범위를 벗어났습니다.')
        return q

    def wait(self,future,timeout):
        end=time.monotonic()+timeout
        while not future.done():
            self.tick()
            if time.monotonic()>end:raise RuntimeError('액션 응답 시간 초과')
        self.check()
        return future.result()

    def action(self,client,goal,timeout):
        self.pending=client.send_goal_async(goal)
        self.active=self.wait(self.pending,5)
        self.pending=None
        if not self.active.accepted:raise RuntimeError('컨트롤러가 목표를 거절했습니다.')
        result=self.wait(self.active.get_result_async(),timeout)
        self.active=None
        if result.status!=4:raise RuntimeError(f'액션 정상 성공 아님: status={result.status}')
        return result.result

    def pause(self,seconds):
        end=time.monotonic()+seconds
        while time.monotonic()<end:self.tick()

    def arm_to(self,name,c):
        from control_msgs.action import FollowJointTrajectory
        from trajectory_msgs.msg import JointTrajectoryPoint
        from builtin_interfaces.msg import Duration
        q=[self.positions[k] for k in JOINTS];target=c['poses'][name]
        seconds=max(c['move_seconds'],1.5*max(abs(a-b) for a,b in zip(q,target))/c['max_joint_speed'])
        g=FollowJointTrajectory.Goal();g.trajectory.joint_names=JOINTS
        g.goal_time_tolerance=Duration(sec=3)
        p=JointTrajectoryPoint();p.positions=q;p.velocities=[0.]*4
        end=JointTrajectoryPoint();end.positions=target;end.velocities=[0.]*4
        end.time_from_start=Duration(sec=int(seconds),nanosec=int((seconds%1)*1e9))
        g.trajectory.points=[p,end]
        result=self.action(self.arm,g,seconds+8)
        if result.error_code!=0:raise RuntimeError(f'팔 궤적 실패: {result.error_code} {result.error_string}')
        self.pause(c['settle_seconds'])
        if max(abs(self.positions[k]-v) for k,v in zip(JOINTS,target))>.04:
            raise RuntimeError('실제 팔 자세가 목표와 다릅니다: '+name)

    def gripper_to(self,name,c):
        from control_msgs.action import GripperCommand
        g=GripperCommand.Goal();g.command.position=c['gripper'][name];g.command.max_effort=5.
        result=self.action(self.grip,g,12)
        if name=='open' and not result.reached_goal:raise RuntimeError('그리퍼 개방 목표 미도달')
        if name=='close' and not (result.reached_goal or result.stalled):raise RuntimeError('그리퍼 폐쇄 미완료')
        self.pause(c['settle_seconds'])
        if name=='open' and abs(self.positions['gripper_left_joint']-c['gripper']['open'])>.003:
            raise RuntimeError('실제 그리퍼 개방 위치 불일치')
        self.event('gripper_result',name=name,reached_goal=result.reached_goal,stalled=result.stalled,
                   note='액션 결과만으로 실제 물체 파지 성공을 증명하지 않음')

    def run(self,c):
        q=self.stable_pose()
        if max(abs(a-b) for a,b in zip(q,c['poses']['home']))>.06:
            raise RuntimeError('먼저 교시한 home 자세로 맞추세요. 임의 시작 자세에서 자동 이동하지 않습니다.')
        self.wheel_anchor=[self.positions[k] for k in WHEELS]
        if not self.arm.wait_for_server(timeout_sec=5) or not self.grip.wait_for_server(timeout_sec=5):
            raise RuntimeError('팔/그리퍼 액션 서버 없음')
        # Do not compete with manual Servo commands.
        if any('servo' in n.lower() for n in self.node.get_node_names()):
            raise RuntimeError('Servo 노드를 종료한 후 자동 실행하세요.')
        for kind,name in SEQUENCE:
            self.tick();self.event('stage_start',kind=kind,name=name)
            if kind=='arm':self.arm_to(name,c)
            else:self.gripper_to(name,c)
            self.event('stage_complete',kind=kind,name=name,joints=self.positions)
        self.event('sequence_complete',note='코드 순서 완료. 무낙하·B 직립 배치·후퇴는 영상으로 확인 필요')

    def close(self):
        # No automatic gripper opening or unplanned home motion on error.
        if self.pending is not None:
            self.rclpy.spin_until_future_complete(self.node,self.pending,timeout_sec=2)
            if self.pending.done():self.active=self.pending.result()
        if self.active is not None and self.active.accepted:
            f=self.active.cancel_goal_async()
            self.rclpy.spin_until_future_complete(self.node,f,timeout_sec=2)
            self.event('cancel_requested',response_received=f.done())
        self.node.destroy_node()
        if self.log_file:self.log_file.close()


import threading,struct
import argparse,json,math,time,itertools
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
import rclpy
from moveit_msgs.srv import GetPositionFK,GetStateValidity
from moveit_msgs.msg import RobotState
from control_msgs.action import FollowJointTrajectory,GripperCommand
from trajectory_msgs.msg import JointTrajectoryPoint
from builtin_interfaces.msg import Duration
from ament_index_python.packages import get_package_share_directory
MESH=Path(get_package_share_directory('turtlebot3_manipulation_description'))/'meshes/open_manipulator_x'
ROOT=Path(__file__).resolve().parent
(ROOT/'logs').mkdir(exist_ok=True)
(ROOT/'reference').mkdir(exist_ok=True)
TEACH_GRASP=[0.06902913545485385, 0.7086991240031663, -0.3144660615165564, 0.9433981845496693]


class ThreadedRunner(Runner):
    def __init__(self,log_path=None):
        from rclpy.executors import SingleThreadedExecutor
        self.last_receive=None;self.max_receive_gap=0.;self.max_frame_age=0.
        super().__init__(log_path)
        self.executor=SingleThreadedExecutor();self.executor.add_node(self.node)
        self.spin_thread=threading.Thread(target=self.executor.spin,daemon=True);self.spin_thread.start()
    def receive(self,msg):
        now=time.monotonic()
        if self.last_receive is not None:self.max_receive_gap=max(self.max_receive_gap,now-self.last_receive)
        self.last_receive=now
        stamp=msg.header.stamp.sec+msg.header.stamp.nanosec/1e9
        self.max_frame_age=max(self.max_frame_age,time.time()-stamp)
        super().receive(msg)
    def tick(self):
        time.sleep(.02);self.check()
    def wait_feedback(self):
        deadline=time.monotonic()+30
        while time.monotonic()<deadline:
            try:self.check();return
            except RuntimeError:time.sleep(.05)
        self.check()
    def close(self):
        def settle(f,seconds):
            end=time.monotonic()+seconds
            while not f.done() and time.monotonic()<end:time.sleep(.02)
        if self.pending is not None:
            settle(self.pending,2)
            if self.pending.done():self.active=self.pending.result()
        if self.active is not None and self.active.accepted:
            f=self.active.cancel_goal_async();settle(f,2);self.event('cancel_requested',response_received=f.done())
        self.event('feedback_health',max_receive_gap=self.max_receive_gap,max_frame_age=self.max_frame_age)
        self.executor.shutdown(timeout_sec=2);self.spin_thread.join(timeout=2)
        self.node.destroy_node()
        if self.log_file:self.log_file.close()

def tip(q):
    yaw,a,j3,j4=q;b=a+j3;c=b+j4
    r=.024*math.cos(a)+.128*math.sin(a)+.124*math.cos(b)+.126*math.cos(c)
    return np.array([-.08+r*math.cos(yaw),r*math.sin(yaw),.1775-.024*math.sin(a)+.128*math.cos(a)-.124*math.sin(b)-.126*math.sin(c)])

def vertices(name):
    b=(MESH/name).read_bytes();vs=[]
    for i in range(struct.unpack_from('<I',b,80)[0]):
        a=struct.unpack_from('<12f',b,84+50*i);vs.extend([a[j:j+3] for j in (3,6,9)])
    return np.unique(np.array(vs)*.001,axis=0)

def triangles(name):
    b=(MESH/name).read_bytes();n=struct.unpack_from('<I',b,80)[0]
    return np.array([struct.unpack_from('<9f',b,84+50*i+12) for i in range(n)]).reshape(-1,3,3)*.001

def intersects(tris,center,half):
    t=np.asarray(tris)-np.asarray(center);half=np.asarray(half)
    keep=np.all(t.min(axis=1)<=half,axis=1)&np.all(t.max(axis=1)>=-half,axis=1)
    t=t[keep]
    if not len(t):return False
    edges=np.stack([t[:,1]-t[:,0],t[:,2]-t[:,1],t[:,0]-t[:,2]],axis=1)
    axes=[np.cross(edges[:,0],edges[:,1])]
    for i in range(3):
        for basis in np.eye(3):axes.append(np.cross(edges[:,i],basis))
    keep=np.ones(len(t),dtype=bool)
    for axis in axes:
        proj=np.einsum('nvi,ni->nv',t,axis);radius=np.abs(axis)@half
        keep &= (proj.min(axis=1)<=radius+1e-12)&(proj.max(axis=1)>=-radius-1e-12)
    return bool(keep.any())

def taught_box_intersects(world,center,yaw):
    """5cm square aligned by parallel jaws, with +/-5deg and small margins."""
    import math
    from scipy.spatial.transform import Rotation
    for yaw_error in [-5.,0.,5.]:
        local=Rotation.from_euler('z',-(yaw+math.radians(yaw_error))).apply((world-center).reshape(-1,3)).reshape(-1,3,3)
        if intersects(local,[0,0,0],[.0275,.0275,.053]):return True
    return False

class Cycle:
    def __init__(self):
        self.tag=str(time.time_ns());self.r=ThreadedRunner(ROOT/'logs'/('full-cycle-'+self.tag+'.jsonl'));self.rows=[];self.box=None;self.box_yaw=0.;self.attached=False;self.grasp=None
        self.fk=self.r.node.create_client(GetPositionFK,'/compute_fk');self.valid=self.r.node.create_client(GetStateValidity,'/check_state_validity')
        self.links=['link2','link3','link4','link5','gripper_left_link','gripper_right_link'];self.meshes=[triangles(k+'.stl') for k in self.links[:4]]+[triangles('gripper_left_palm.stl'),triangles('gripper_right_palm.stl')];self.meshes[0][:,:,2]+=.019
        self.mesh_bounds=[np.array(list(itertools.product(*zip(m.reshape(-1,3).min(axis=0),m.reshape(-1,3).max(axis=0))))) for m in self.meshes]
    def stable(self):
        self.r.wait_feedback();self.r.pause(1.)
        return np.array(self.r.stable_pose())
    def call(self,c,req):
        if not c.wait_for_service(timeout_sec=5):raise RuntimeError('Missing planning service')
        return self.r.wait(c.call_async(req),10)
    def cart(self,start,end_xyz,end_pitch):
        origin=tip(start);p0=sum(start[1:]);distance=float(np.linalg.norm(end_xyz-origin));n=max(20,int(math.ceil(distance/.0015)))
        path=[start];bounds=([a for a,b in LIMITS],[b for a,b in LIMITS])
        for u in np.linspace(0,1,n+1)[1:]:
            xyz=origin*(1-u)+end_xyz*u;p=p0*(1-u)+end_pitch*u
            sol=least_squares(lambda q:np.r_[tip(q)-xyz,.1*(sum(q[1:])-p)],path[-1],bounds=bounds,gtol=1e-12,xtol=1e-12,ftol=1e-12,max_nfev=600)
            if np.linalg.norm(tip(sol.x)-xyz)>.0002 or abs(sum(sol.x[1:])-p)>.002:raise RuntimeError('Unreachable Cartesian sample')
            if min(min(q-lo,hi-q) for q,(lo,hi) in zip(sol.x,LIMITS))<.02:raise RuntimeError('Joint limit margin')
            path.append(sol.x)
        return path
    def joint(self,start,end):
        return [start*(1-u)+end*u for u in np.linspace(0,1,max(25,int(max(abs(end-start))/.015))+1)]
    def check(self,path,grip):
        for sample_index,q in enumerate(path):
            state=RobotState();state.joint_state.name=JOINTS+['gripper_left_joint','gripper_right_joint']+WHEELS;state.joint_state.position=list(map(float,q))+[float(grip)]*2+[self.r.positions[k] for k in WHEELS]
            req=GetStateValidity.Request();req.robot_state=state;req.group_name='arm';valid=self.call(self.valid,req)
            if not valid.valid:raise RuntimeError('Self collision '+str([(c.contact_body_1,c.contact_body_2) for c in valid.contacts]))
            req=GetPositionFK.Request();req.header.frame_id='base_footprint';req.fk_link_names=self.links;req.robot_state=state;fk=self.call(self.fk,req)
            if fk.error_code.val!=1:raise RuntimeError('FK failure')
            center=self.box.copy();yaw=self.box_yaw
            if self.attached:
                yaw=q[0];delta=q[0]-self.grasp[0];offset=self.box[:2]-tip(self.grasp)[:2];rot=np.array([[math.cos(delta),-math.sin(delta)],[math.sin(delta),math.cos(delta)]])
                center[:2]=tip(q)[:2]+rot@offset;center[2]+=(tip(q)[2]-tip(self.grasp)[2])
                if center[2]<.0495:raise RuntimeError('Carried object below support plane')
            for name,mesh,bounds,p in zip(self.links,self.meshes,self.mesh_bounds,fk.pose_stamped):
                o=p.pose.orientation;t=p.pose.position;rotation=Rotation.from_quat([o.x,o.y,o.z,o.w]);translation=np.array([t.x,t.y,t.z]);corners=rotation.apply(bounds)+translation
                lo=corners.min(axis=0);hi=corners.max(axis=0);world=None
                if lo[2]<.015:
                    world=rotation.apply(mesh.reshape(-1,3)).reshape(-1,3,3)+translation
                    if world[:,:,2].min()<.015:raise RuntimeError('Arm/table clearance')
                if self.attached and 'gripper' in name:continue
                # Broad phase only rejects provably disjoint bounding volumes.
                if np.any(hi<center-[.04,.04,.053]) or np.any(lo>center+[.04,.04,.053]):continue
                if world is None:world=rotation.apply(mesh.reshape(-1,3)).reshape(-1,3,3)+translation
                # Taught 5cm square, faces aligned by the parallel-jaw grasp.
                # Check +/-5deg yaw with 2.5mm XY and 3mm height margin; do not
                # replace the union of possible orientations by a 7.6cm square.
                if taught_box_intersects(world,center,yaw):raise RuntimeError('Object collision '+name+' sample='+str(sample_index)+' xyz='+str(tip(q).tolist()))
    def move(self,name,path,recover=False):
        self.check(path,self.r.positions['gripper_left_joint']);now=self.stable()
        if max(abs(now-path[0]))>.015:raise RuntimeError('State changed during validation')
        goal=FollowJointTrajectory.Goal();goal.trajectory.joint_names=JOINTS;goal.goal_time_tolerance=Duration(sec=3);elapsed=0.
        for i,q in enumerate(path):
            if i:elapsed+=max(.35,1.5*float(max(abs(q-path[i-1])))/.04)
            p=JointTrajectoryPoint();p.positions=q.tolist();p.velocities=[0.]*4;p.time_from_start=Duration(sec=int(elapsed),nanosec=int((elapsed%1)*1e9));goal.trajectory.points.append(p)
        r=self.r;r.event('cycle_stage_start',name=name,mission_stage={'approach':1,'lower':2,'lift':4,'transfer':5,'place':6,'release_clearance':6,'retreat':6,'home':'home'}.get(name),duration=elapsed)
        r.pending=r.arm.send_goal_async(goal);r.active=r.wait(r.pending,5);r.pending=None
        if not r.active.accepted:raise RuntimeError('Arm goal rejected')
        result=r.wait(r.active.get_result_async(),elapsed+10);r.active=None
        actual=self.stable();error=result.result.error_code;aborted=result.status!=4 or error!=0
        row={'stage':name,'status':result.status,'error_code':error,'error_string':result.result.error_string,'actual':actual.tolist(),'xyz':tip(actual).tolist(),'target':path[-1].tolist()};self.rows.append(row);r.event('cycle_stage_result',**row);self.save(False)
        if aborted:
            if not(recover and result.status==6 and error==-5):raise RuntimeError('Unrecoverable arm action failure')
            if name=='lift':
                delta=tip(actual)-tip(self.grasp)
                if not(.015<=delta[2]<=.065 and np.linalg.norm(delta[:2])<.025 and abs(sum(actual[1:])-sum(self.grasp[1:]))<.15):raise RuntimeError('Lift not safe to continue')
            elif name=='release_clearance':
                delta=tip(actual)-tip(path[0])
                if not(delta[2]>.005 and np.linalg.norm(delta[:2])<.02 and abs(sum(actual[1:])-sum(path[0][1:]))<.15):raise RuntimeError('No verified upward clearance progress')
            elif name=='retreat':
                if tip(actual)[2]<.15:raise RuntimeError('Retreat not high enough')
            else:raise RuntimeError('Stage not eligible for recovery')
            self.check([actual],r.positions['gripper_left_joint']);r.event('verified_partial_stage',name=name,note='No tolerance change; subsequent path replanned from actual state')
        elif max(abs(actual-path[-1]))>.04:raise RuntimeError('Endpoint feedback mismatch')
        return actual
    def retreat_home(self,placed):
        end=tip(placed);end[2]=.13
        actual=self.move('release_clearance',self.cart(placed,end,sum(placed[1:])),recover=True)
        for attempt in range(3):
            if tip(actual)[2]>=.13:break
            end=tip(actual);end[2]=min(.15,end[2]+.035)
            actual=self.move('release_clearance',self.cart(actual,end,sum(placed[1:])),recover=True)
        if tip(actual)[2]<.13:raise RuntimeError('Unable to establish upward clearance')
        end=tip(actual);end[2]=.18
        actual=self.move('retreat',self.cart(actual,end,math.radians(60)),recover=True)
        return self.move('home',self.joint(actual,np.array([0.,-1.05,1.05,0.])))

    def grip(self,close):
        self.r.event('cycle_gripper_start',mission_stage=3 if close else 6,closing=close)
        targets=[.015,.011,.007,.003,0.] if close else [.019]
        for target in targets:
            goal=GripperCommand.Goal();goal.command.position=target;goal.command.max_effort=1.;result=self.r.action(self.r.grip,goal,12);self.r.pause(.5)
            actual=self.r.positions['gripper_left_joint'];self.r.event('cycle_gripper',target=target,actual=actual,stalled=result.stalled,reached=result.reached_goal)
            if not(result.reached_goal or (close and result.stalled)):raise RuntimeError('Gripper failed')
            if close and (result.stalled or abs(actual-target)>.002):break
        if not close and abs(self.r.positions['gripper_left_joint']-.019)>.003:raise RuntimeError('Opening incomplete')
    def save(self,complete):
        (ROOT/'reference'/('full_cycle_'+self.tag+'.json')).write_text(json.dumps({'stages':self.rows,'command_sequence_complete':complete,'physical_success_confirmed':False,'note':'Verify actual retention, upright placement and video separately.'},indent=2)+'\n')
    def run(self,execute):
        start=self.stable();r=self.r;r.wheel_anchor=[r.positions[k] for k in WHEELS]
        if max(abs(start-np.array([0.,-1.05,1.05,0.])))>.04:raise RuntimeError('Not at bringup home')
        if abs(r.positions['gripper_left_joint']-.019)>.003:raise RuntimeError('Gripper not open')
        if any('servo' in n.lower() for n in r.node.get_node_names()):raise RuntimeError('Servo active')
        if not r.arm.wait_for_server(timeout_sec=5) or not r.grip.wait_for_server(timeout_sec=5):raise RuntimeError('Action unavailable')
        grasp=np.array(TEACH_GRASP);point=tip(grasp);gp=sum(grasp[1:]);self.grasp=grasp
        off=.0207*math.cos(gp);self.box=np.array([point[0]+off*math.cos(grasp[0]),point[1]+off*math.sin(grasp[0]),.05]);self.box_yaw=grasp[0]
        # Nominal approach starts above the taught grasp XY.
        top=np.array([point[0],point[1],.18]);approach=self.cart(grasp,top,math.radians(60))[-1]
        approach_path=self.joint(start,approach);self.check(approach_path,.019)
        down=self.cart(approach,point,gp);self.check(down,.019)
        self.attached=True;up=self.cart(grasp,point+[0,0,.05],gp);self.check(up,0.)
        turn=-math.radians(20);rot=self.joint(up[-1],up[-1]+[turn,0,0,0]);self.check(rot,0.)
        place=self.joint(rot[-1],grasp+[turn,0,0,0]);self.check(place,0.)
        self.attached=False
        box_a=self.box.copy();yaw_a=self.box_yaw
        offset=self.box[:2]-tip(grasp)[:2];rot2=np.array([[math.cos(turn),-math.sin(turn)],[math.sin(turn),math.cos(turn)]])
        self.box[:2]=tip(place[-1])[:2]+rot2@offset;self.box_yaw=place[-1][0]
        clear=tip(place[-1]);clear[2]=.13
        first_back=self.cart(place[-1],clear,sum(place[-1][1:]));self.check(first_back,.019)
        clear[2]=.18;back=self.cart(first_back[-1],clear,math.radians(60));self.check(back,.019)
        self.check(self.joint(back[-1],np.array([0.,-1.05,1.05,0.])),.019)
        self.box=box_a;self.box_yaw=yaw_a
        r.event('full_nominal_cycle_checked')
        if not execute:return
        actual=self.move('approach',approach_path)
        actual=self.move('lower',self.cart(actual,point,gp));self.grasp=actual;self.grip(True);self.attached=True
        lifted=self.move('lift',self.cart(actual,tip(actual)+[0,0,.05],sum(actual[1:])),recover=True)
        rotated=self.move('transfer',self.joint(lifted,lifted+[turn,0,0,0]))
        placed=self.move('place',self.joint(rotated,self.grasp+[turn,0,0,0]))
        # A is now B; the object is supported before opening.
        delta=placed[0]-self.grasp[0];offset=self.box[:2]-tip(self.grasp)[:2];rot2=np.array([[math.cos(delta),-math.sin(delta)],[math.sin(delta),math.cos(delta)]])
        self.box[:2]=tip(placed)[:2]+rot2@offset;self.box_yaw=placed[0]
        self.grip(False);self.attached=False
        self.retreat_home(placed)
        self.save(True);r.event('full_cycle_command_sequence_complete',physical_success_confirmed=False)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--execute',action='store_true');args=ap.parse_args();rclpy.init();cycle=Cycle()
    try:cycle.run(args.execute)
    finally:cycle.r.close();rclpy.shutdown()

if __name__=='__main__':main()
