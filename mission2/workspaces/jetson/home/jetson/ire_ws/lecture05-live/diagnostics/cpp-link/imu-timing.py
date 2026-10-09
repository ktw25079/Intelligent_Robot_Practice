import sys,time,json
from pathlib import Path
sys.path.insert(0,str(Path.home()/'lecture05-setup/DynamixelSDK/python/src'))
from dynamixel_sdk import PortHandler,PacketHandler,COMM_SUCCESS
p=PortHandler('/dev/ttyACM0');k=PacketHandler(2.0);assert p.openPort() and p.setBaudRate(1000000)
p.setPacketTimeout=lambda size:p.setPacketTimeoutMillis(6500)
rows=[]
try:
 for name,addr,value in [('led_same_value',20,0),('imu_recalibration',59,1),('led_same_value_after',20,0)]:
  if addr==20:
   value,res,err=k.read1ByteTxRx(p,200,addr)
   assert res==COMM_SUCCESS and not err
  t=time.monotonic();res,err=k.write1ByteTxRx(p,200,addr,value)
  row={'operation':name,'result':res,'error':err,'elapsed_ms':round((time.monotonic()-t)*1000,2)};rows.append(row);print(json.dumps(row),flush=True)
finally:
 p.closePort();(Path.home()/'lecture05-setup/imu-timing.json').write_text(json.dumps(rows,indent=2))
