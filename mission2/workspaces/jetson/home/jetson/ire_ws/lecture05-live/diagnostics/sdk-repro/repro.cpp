#include "protocol2_packet_handler.h"
#include <vector>
#include <cstring>
#include <algorithm>
#include <cstdio>
class Fake : public dynamixel::PortHandler {
 public:
 std::vector<uint8_t> rx; size_t at=0;
 Fake() {is_using_=false; rx={255,255,253,0,200,24,0,85,0}; rx.resize(29,0); uint16_t c=0; for(auto b:rx){c^=uint16_t(b)<<8;for(int i=0;i<8;i++)c=(c&0x8000)?(c<<1)^0x8005:c<<1;}rx.push_back(c&255);rx.push_back(c>>8);}
 bool openPort() override{return true;} void closePort() override{} void clearPort() override{}
 void setPortName(const char*) override{} char* getPortName() override {return nullptr;}
 bool setBaudRate(int) override{return true;} int getBaudRate() override{return 1000000;}
 int getBytesAvailable() override{return rx.size()-at;}
 int readPort(uint8_t* b,int n) override {n=std::min(n,int(rx.size()-at));memcpy(b,rx.data()+at,n);at+=n;return n;}
 int writePort(uint8_t*,int n) override{return n;}
 void setPacketTimeout(uint16_t) override{} void setPacketTimeout(double) override{}
 bool isPacketTimeout() override{return at>=rx.size();}
};
int main(){Fake f; uint8_t value=0,error=0; int r=dynamixel::Protocol2PacketHandler::getInstance()->writeTxRx(&f,200,20,1,&value,&error);printf("result=%d error=%u bytes=%zu\n",r,error,f.at);}
