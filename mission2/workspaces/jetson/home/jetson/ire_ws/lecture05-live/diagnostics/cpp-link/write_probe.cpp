#include <dynamixel_sdk/dynamixel_sdk.h>
#include <dynamixel_sdk/port_handler_linux.h>
#include <cstdio>
#include <chrono>
#include <thread>
class OpenCRPort: public dynamixel::PortHandlerLinux { public: OpenCRPort():PortHandlerLinux("/dev/ttyACM0"){} void setPacketTimeout(uint16_t n) override { (void)n; PortHandlerLinux::setPacketTimeout(100.0); }};
int main(int argc,char**){dynamixel::PortHandler* p=argc>1?static_cast<dynamixel::PortHandler*>(new OpenCRPort()):dynamixel::PortHandler::getPortHandler("/dev/ttyACM0");auto k=dynamixel::PacketHandler::getPacketHandler(2.0); if(!p->openPort()||!p->setBaudRate(1000000))return 2;for(int i=0;i<8;i++){uint8_t e=0;auto t=std::chrono::steady_clock::now();int r=k->write1ByteTxRx(p,200,20,0,&e);double ms=std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-t).count();printf("%d result=%d err=%u ms=%.2f\n",i,r,e,ms);fflush(stdout);std::this_thread::sleep_for(std::chrono::milliseconds(150));}p->closePort();}
