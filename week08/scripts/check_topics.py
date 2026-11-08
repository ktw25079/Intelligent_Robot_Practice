import json,time,sys
from pathlib import Path
import cv2,rclpy
from cv_bridge import CvBridge
from sensor_msgs.msg import Image,CameraInfo
from geometry_msgs.msg import PoseStamped
from rclpy.qos import qos_profile_sensor_data
rclpy.init(); n=rclpy.create_node('vision_lab_check'); b=CvBridge()
s={'images':0,'infos':0,'poses':0,'ids':[]}; root=Path(sys.argv[1]); root.mkdir(parents=True,exist_ok=True)
d=cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
def im(m):
 s['images']+=1
 frame=b.imgmsg_to_cv2(m,'bgr8')
 _,ids,_=cv2.aruco.detectMarkers(frame,d)
 if ids is not None:s['ids']=sorted(set(s['ids']+ids.ravel().tolist()))
 if s['images']==1 or ids is not None:cv2.imwrite(str(root/'camera.jpg'),frame)
def info(m):
 s['infos']+=1;s['K']=list(m.k);s['D']=list(m.d);s['size']=[m.width,m.height]
def pose(m):
 s['poses']+=1;s['pose_frame']=m.header.frame_id;s['last_position']=[m.pose.position.x,m.pose.position.y,m.pose.position.z]
subs=[n.create_subscription(Image,'/camera/image_raw',im,qos_profile_sensor_data),n.create_subscription(CameraInfo,'/camera/camera_info',info,qos_profile_sensor_data),n.create_subscription(PoseStamped,'/aruco/pose',pose,10)]
end=time.monotonic()+(float(sys.argv[2]) if len(sys.argv)>2 else 20)
while time.monotonic()<end:rclpy.spin_once(n,timeout_sec=.2)
(root/'check.json').write_text(json.dumps(s,indent=2));print(json.dumps(s),flush=True)
n.destroy_node();rclpy.shutdown()
