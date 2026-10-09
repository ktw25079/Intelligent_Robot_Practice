import sys,time,json
from pathlib import Path
sys.path.insert(0,str(Path.home()/'lecture05-setup/DynamixelSDK/python/src'))
from dynamixel_sdk import PortHandler,PacketHandler,COMM_SUCCESS
p=PortHandler('/dev/ttyACM0'); assert p.openPort()
report={'scope':'PING and READ only; no motor configuration or motion writes','found':[],'search':[]}
fields=[('model',0,2),('firmware',6,1),('id',7,1),('baud_code',8,1),('return_delay',9,1),('drive_mode',10,1),('operating_mode',11,1),('secondary_id',12,1),('protocol',13,1),('torque',64,1),('hardware_error',70,1),('voltage_raw',144,2),('temperature_C',146,1)]
try:
 for baud in [1000000,57600,115200,9600,2000000,3000000,4000000,4500000]:
  if not p.setBaudRate(baud):
   report['search'].append({'baud':baud,'error':'unsupported host baud'});continue
  time.sleep(.2);p.clearPort()
  k=PacketHandler(2.0);found,res=k.broadcastPing(p)
  ids=set(found)
  for ident in [1,2,11,12,13,14,15]:
   model,r,e=k.ping(p,ident)
   if r==COMM_SUCCESS:ids.add(ident)
  report['search'].append({'baud':baud,'protocol':2,'ids':sorted(ids),'broadcast_result':res})
  for ident in sorted(ids):
   item={'baud':baud,'protocol_used':2,'ping_id':ident}
   for name,addr,size in fields:
    data,r,e=k.readTxRx(p,ident,addr,size)
    item[name]=int.from_bytes(bytes(data),'little') if r==COMM_SUCCESS and not e else {'comm':r,'device_error':e}
   report['found'].append(item);print(json.dumps(item),flush=True)
  k=PacketHandler(1.0);ids=[]
  for ident in range(253):
   model,r,e=k.ping(p,ident)
   if r==COMM_SUCCESS:
    ids.append(ident);item={'baud':baud,'protocol_used':1,'ping_id':ident,'ping_model':model}
    for name,addr,size in fields:
     data,r,e=k.readTxRx(p,ident,addr,size)
     item[name]=int.from_bytes(bytes(data),'little') if r==COMM_SUCCESS and not e else {'comm':r,'device_error':e}
    report['found'].append(item);print(json.dumps(item),flush=True)
  report['search'].append({'baud':baud,'protocol':1,'ids':ids})
  print('completed baud',baud,flush=True)
finally:
 p.closePort();(Path.home()/'lecture05-setup/motor-scan.json').write_text(json.dumps(report,indent=2))
