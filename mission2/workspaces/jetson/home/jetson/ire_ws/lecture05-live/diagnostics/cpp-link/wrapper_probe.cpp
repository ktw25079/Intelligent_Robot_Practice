#include "turtlebot3_manipulation_hardware/dynamixel_sdk_wrapper.hpp"
#include <chrono>
#include <cstdio>
#include <stdexcept>
using robotis::turtlebot3_manipulation_hardware::DynamixelSDKWrapper;
int main(){
 {DynamixelSDKWrapper absent(199);if(!absent.open_port("/dev/ttyACM0")||!absent.set_baud_rate(1000000))return 2;bool failed=false;try{absent.read_byte(16);}catch(const std::runtime_error&){failed=true;}if(!failed)return 3;puts("PASS absent device read fails explicitly");}
 DynamixelSDKWrapper w(200);if(!w.open_port("/dev/ttyACM0")||!w.set_baud_rate(1000000))return 4;
 if(w.read_byte(16)!=1||w.read_byte(148)!=1)return 5;
 uint8_t v=1;auto t=std::chrono::steady_clock::now();if(!w.write(59,1,&v))return 6;
 printf("PASS IMU acknowledgement %.2f ms\n",std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-t).count());
 for(int i=0;i<20;i++){uint8_t d[344]={};if(!w.read(0,344,d)||!d[16]||!d[148])return 7;uint8_t led=w.read_byte(20);if(!w.write(20,1,&led))return 8;}
 puts("PASS 20 alternating table reads and same-value LED writes after calibration");
}
