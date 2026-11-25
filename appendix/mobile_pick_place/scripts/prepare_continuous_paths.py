#!/usr/bin/env python3
"""Generate slow taught-pose trajectories; verify robot/floor collisions in MoveIt.
Object contact is based on the user's taught poses. This does not infer object
size or claim validation against unmodeled objects.
"""
import copy,json,math,time
from pathlib import Path
import numpy as np
from scipy.optimize import root
import rclpy
from sensor_msgs.msg import JointState
from moveit_msgs.srv import GetStateValidity,GetPositionFK,ApplyPlanningScene
from moveit_msgs.msg import CollisionObject
from shape_msgs.msg import SolidPrimitive
from geometry_msgs.msg import Pose
ROOT=Path(__file__).resolve().parents[1]
JOINTS=['joint1','joint2','joint3','joint4']
LIMITS=[(-2.827,2.827),(-1.790,1.570),(-.942,1.382),(-1.790,2.042)]
def tip(q):
 yaw,a,j3,j4=q;b=a+j3;c=b+j4
 radius=.024*math.cos(a)+.128*math.sin(a)+.124*math.cos(b)+.126*math.cos(c)
 return np.array([-.08+radius*math.cos(yaw),radius*math.sin(yaw),.1775-.024*math.sin(a)+.128*math.cos(a)-.124*math.sin(b)-.126*math.sin(c)])
def ik(xyz,pitch,seed):
 yaw=math.atan2(xyz[1],xyz[0]+.08)
 def f(v):
  p=tip([yaw,*v])
  return [math.hypot(p[0]+.08,p[1])-math.hypot(xyz[0]+.08,xyz[1]),p[2]-xyz[2],sum(v)-pitch]
 sol=root(f,seed[1:]);q=[yaw,*sol.x.tolist()]
 if not sol.success or max(abs(x) for x in f(sol.x))>1e-6:raise RuntimeError('IK failed')
 if any(not lo<=x<=hi for x,(lo,hi) in zip(q,LIMITS)):raise RuntimeError('Joint limit')
 return q
def trajectory(start,goal,cartesian):
 qs=[];count=80;last=start;begin=tip(start);end=tip(goal)
 for i in range(count+1):
  u=i/count;v=u*u*(3-2*u)
  if cartesian:
   q=ik(begin+(end-begin)*v,sum(start[1:])+(sum(goal[1:])-sum(start[1:]))*v,last)
  else:q=[a+(b-a)*v for a,b in zip(start,goal)]
  if max(abs(a-b) for a,b in zip(q,last))>.04:raise RuntimeError('Joint discontinuity')
  qs.append(q);last=q
 if max(abs(a-b) for a,b in zip(qs[-1],goal))>.005:raise RuntimeError('Endpoint mismatch')
 arr=np.array(qs);vmax=np.max(np.abs(np.diff(arr,axis=0)))*count
 amax=np.max(np.abs(np.diff(arr,n=2,axis=0)))*count**2
 duration=max(5.,vmax/.07*1.2,math.sqrt(amax/.10)*1.2)
 dt=duration/count;points=[]
 for i,q in enumerate(qs):
  vel=((arr[i+1]-arr[i-1])/(2*dt)).tolist() if 0<i<count else [0.]*4
  points.append({'positions':q,'velocities':vel,'time':i*dt})
 return {'duration':duration,'points':points,'start':start,'goal':goal,'cartesian':cartesian}
mission=json.loads((ROOT/'mission_config/mission_20261119_195253.json').read_text())
poses={k:json.loads((ROOT/v).read_text()) for k,v in mission['taught_poses'].items()}
pre=[poses['pre_grasp']['joints'][k] for k in JOINTS]
grasp=[poses['grasp']['joints'][k] for k in JOINTS]
home=[0.,-1.05,1.05,0.]
# This command held the object successfully during the observed B transfer.
carry_record=json.loads((ROOT/'execution_logs/pick_to_lift_result.json').read_text())
carry=[carry_record['final_joints'][k] for k in JOINTS]
upper=ik(tip(pre)+[0,0,.10],sum(pre[1:]),pre)
stages={'approach':trajectory(home,upper,False),'lower':trajectory(upper,pre,True),'carry':trajectory(pre,carry,True),'place':trajectory(carry,grasp,True),'home':trajectory(grasp,home,False)}
rclpy.init();n=rclpy.create_node('validate_continuous_paths')
def call(typ,name,req):
 if name not in clients:
  clients[name]=n.create_client(typ,name)
 client=clients[name]
 if not client.wait_for_service(timeout_sec=12):raise RuntimeError('Unavailable: '+name)
 f=client.call_async(req);rclpy.spin_until_future_complete(n,f,timeout_sec=8)
 if not f.done():raise RuntimeError('Validation timeout')
 return f.result()
clients={}
obj=CollisionObject();obj.header.frame_id='base_footprint';obj.id='week11_floor';obj.operation=CollisionObject.ADD
obj.primitives=[SolidPrimitive(type=SolidPrimitive.BOX,dimensions=[3.,3.,.02])]
p=Pose();p.orientation.w=1.;p.position.z=-.02;obj.primitive_poses=[p]
r=ApplyPlanningScene.Request();r.scene.is_diff=True;r.scene.robot_state.is_diff=True;r.scene.world.collision_objects=[obj]
if not call(ApplyPlanningScene,'/apply_planning_scene',r).success:raise RuntimeError('Scene failed')
try:
 for name,t in stages.items():
  opening=.019 if name in ('approach','lower','home') else poses['grasp']['gripper_joints']['gripper_left_joint']
  for i,pt in enumerate(t['points']):
   state=JointState();state.name=JOINTS+['gripper_left_joint','gripper_right_joint','wheel_left_joint','wheel_right_joint'];state.position=pt['positions']+[opening,opening,0.,0.]
   r=GetStateValidity.Request();r.group_name='arm';r.robot_state.joint_state=state
   check=call(GetStateValidity,'/check_state_validity',r)
   if not check.valid:raise RuntimeError(f'{name} waypoint {i} collision: {check.contacts}')
   if i in (0,len(t['points'])-1):
    f=GetPositionFK.Request();f.header.frame_id='base_footprint';f.fk_link_names=['end_effector_link'];f.robot_state.joint_state=state
    actual=call(GetPositionFK,'/compute_fk',f)
    if actual.error_code.val!=1:raise RuntimeError('FK service failed')
    p=actual.pose_stamped[0].pose.position
    if math.dist([p.x,p.y,p.z],tip(pt['positions']))>.001:raise RuntimeError('FK/model mismatch')
  print(name,'validated',len(t['points']),'duration',round(t['duration'],1),'goal_tip',tip(t['goal']).tolist(),flush=True)
 out={'joint_names':JOINTS,'stages':stages,'gripper_open':.019,'gripper_close_command':-.010,'gripper_taught_contact':poses['grasp']['gripper_joints']['gripper_left_joint'],'inter_stage_delay_s':2.5,'collision_check':'robot self-collision and floor; user-taught object contact','validated_at':time.time(),'autonomous_pick_success_verified':False}
 (ROOT/'mission_config/continuous_paths.json').write_text(json.dumps(out,indent=2)+'\n')
finally:n.destroy_node();rclpy.shutdown()
