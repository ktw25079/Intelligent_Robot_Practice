#include <dynamixel_sdk/dynamixel_sdk.h>
#include <cstdio>
#include <chrono>
#include <thread>
int main(){auto p=dynamixel::PortHandler::getPortHandler("/dev/ttyACM0");auto k=dynamixel::PacketHandler::getPacketHandler(2.0); if(!p->openPort()||!p->setBaudRate(1000000))return 2; for(int i=0;i<20;i++){uint8_t d[4096]={},e=0;auto t=std::chrono::steady_clock::now();int r=k->readTxRx(p,200,0,344,d,&e);double ms=std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-t).count();printf("%d result=%d err=%u ms=%.2f arm=%u wheels=%u\n",i,r,e,ms,d[16],d[148]);fflush(stdout);std::this_thread::sleep_for(std::chrono::milliseconds(100));}p->closePort();}
