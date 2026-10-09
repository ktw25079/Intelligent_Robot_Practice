#include "protocol2_packet_handler.h"
#include <vector>
#include <cstring>
#include <algorithm>
#include <cstdio>
#include <cassert>
class Fake : public dynamixel::PortHandler {
 public:
 std::vector<uint8_t> rx; size_t at=0;
 Fake(){is_using_=false;}
 void status(size_t payload, uint8_t byte=0){std::vector<uint8_t> v={255,255,253,0,200,uint8_t((payload+4)&255),uint8_t((payload+4)>>8),85,0};v.resize(9+payload,byte);uint16_t c=0;for(auto b:v){c^=uint16_t(b)<<8;for(int i=0;i<8;i++)c=(c&0x8000)?(c<<1)^0x8005:c<<1;}v.push_back(c&255);v.push_back(c>>8);rx.insert(rx.end(),v.begin(),v.end());}

 bool openPort() override{return true;} void closePort() override{} void clearPort() override{}
 void setPortName(const char*) override{} char* getPortName() override {return nullptr;}
 bool setBaudRate(int) override{return true;} int getBaudRate() override{return 1000000;}
 int getBytesAvailable() override{return rx.size()-at;}
 int readPort(uint8_t* b,int n) override {n=std::min(n,int(rx.size()-at));memcpy(b,rx.data()+at,n);at+=n;return n;}
 int writePort(uint8_t*,int n) override{return n;}
 void setPacketTimeout(uint16_t) override{} void setPacketTimeout(double) override{}
 bool isPacketTimeout() override{return at>=rx.size();}
};
int main(){
 auto h=dynamixel::Protocol2PacketHandler::getInstance();uint8_t value=0,error=0;
 {Fake f;f.status(20);f.status(0);int r=h->writeTxRx(&f,200,20,1,&value,&error);assert(r==0 && f.at==42);puts("PASS stale READ discarded then normal WRITE accepted");}
 {Fake f;f.status(20);int r=h->writeTxRx(&f,200,20,1,&value,&error);assert(r!=0);puts("PASS stale READ alone rejected");}
 {Fake f;f.status(344,42);uint8_t data[344]={};int r=h->readTxRx(&f,200,0,344,data,&error);assert(r==0 && data[0]==42 && data[343]==42);puts("PASS normal 344-byte READ");}
 {Fake f;f.status(0);f.status(344,42);uint8_t data[344]={};int r=h->readTxRx(&f,200,0,344,data,&error);assert(r==0 && data[343]==42);puts("PASS stale WRITE discarded then normal READ accepted");}
 {Fake f;f.status(0);int r=h->writeTxRx(&f,200,20,1,&value,&error);assert(r==0);puts("PASS normal WRITE");}
 {Fake f;f.status(1020);int r=h->writeTxRx(&f,200,20,1,&value,&error);assert(r!=0);puts("PASS declared LENGTH 1024 rejected (total exceeds buffer)");}
 {Fake f;f.status(3);f.rx[9]=0; /* regenerate using default zeros, model 0 is valid */ uint16_t model=1;int r=h->ping(&f,200,&model,&error);assert(r==0 && model==0);puts("PASS normal PING");}
}
