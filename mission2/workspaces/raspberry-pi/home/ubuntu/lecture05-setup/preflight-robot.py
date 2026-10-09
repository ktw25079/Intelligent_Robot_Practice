#!/usr/bin/env python3
"""Read-only pre-bringup checks. Sends only OpenCR PING and READ packets."""
import json, os, subprocess, sys, time
from pathlib import Path
from ament_index_python.packages import get_package_prefix, PackageNotFoundError
sys.path.insert(0, str(Path.home()/'lecture05-setup/DynamixelSDK/python/src'))
from dynamixel_sdk import PortHandler, PacketHandler, COMM_SUCCESS
result={}; failures=[]
for key, expected in [('ROS_DOMAIN_ID','4'),('ROS_LOCALHOST_ONLY','0'),('LDS_MODEL','LDS-01')]:
 result[key]=os.getenv(key)
 if result[key]!=expected: failures.append(f'{key} must be {expected}')
names=['turtlebot3_manipulation_bringup','turtlebot3_manipulation_hardware','turtlebot3_manipulation_description','controller_manager','hls_lfcd_lds_driver','diff_drive_controller','joint_trajectory_controller','gripper_controllers','joint_state_broadcaster','imu_sensor_broadcaster']
result['missing_packages']=[]
for name in names:
 try:get_package_prefix(name)
 except PackageNotFoundError:result['missing_packages'].append(name)
if result['missing_packages']:failures.append('Missing ROS packages')
for port in ['/dev/ttyACM0','/dev/ttyUSB0']:
 access=os.access(port,os.R_OK|os.W_OK)
 busy=subprocess.run(['fuser',port],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
 result[port]={'read_write_access':access,'busy':busy}
 if not access or busy:failures.append(f'{port}: inaccessible or in use')
result['power_samples']=[]
power=Path('/sys/devices/platform/soc/soc:firmware/get_throttled')
for i in range(5):
 raw=power.read_text().strip(); flags=int(raw,16)
 result['power_samples'].append('0x'+raw)
 if flags&5:failures.append('Current undervoltage or throttling detected')
 if i:time.sleep(1)
if any(int(v,16)&0x50000 for v in result['power_samples'][1:]):
 failures.append('Undervoltage/throttling event detected during observation')
port_state=result['/dev/ttyACM0']
if port_state['read_write_access'] and not port_state['busy']:
 p=PortHandler('/dev/ttyACM0');k=PacketHandler(2.0)
 try:
  if not p.openPort() or not p.setBaudRate(1000000):raise RuntimeError('Cannot open OpenCR port')
  model,res,err=k.ping(p,200)
  if res!=COMM_SUCCESS or err:raise RuntimeError(f'OpenCR ping: {k.getTxRxResult(res)}, device error {err}')
  data,res,err=k.readTxRx(p,200,0,344)
  if res!=COMM_SUCCESS or err or len(data)!=344:raise RuntimeError('OpenCR control table read failed')
  result['opencr']={'model_number':model,'model_information':int.from_bytes(bytes(data[2:6]),'little'),'firmware_version':data[6],'arm_connected_at_boot':bool(data[16]),'wheels_connected_at_boot':bool(data[148]),'input_voltage_V':int.from_bytes(bytes(data[42:46]),'little',signed=True)*.01}
  if result['opencr']['model_information']!=3:failures.append('OpenCR model is not Waffle_OpenManipulator')
  if not data[16]:failures.append('Arm motors not detected at OpenCR boot')
  if not data[148]:failures.append('Wheel motors not detected at OpenCR boot')
 except Exception as e:failures.append(str(e))
 finally:p.closePort()
result['failures']=list(dict.fromkeys(failures))
result['software_and_electronic_checks_passed']=not failures
result['physical_clearance_checked']=False
result['note']='Does not test motion or start LiDAR. OpenCR input voltage is not Raspberry Pi 5V supply voltage.'
out=Path.home()/'lecture05-setup/preflight-latest.json'
out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
sys.exit(1 if failures else 0)
