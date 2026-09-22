#include "monitor_display.h"
// ST7789 显示驱动占位：收到屏幕后按丝印核对 CS/DC/RST/SCLK/MOSI，再启用 TFT_eSPI。
void monitorDisplayBegin(){ Serial.println("DISPLAY,ST7789,INIT_PENDING_PIN_CHECK"); }
void monitorDisplayShow(const char* channel,const char* uid,const char* status,uint16_t retry){
  Serial.printf("DISPLAY,CH,%s,UID,%s,STATUS,%s,RETRY,%u\n",channel,uid,status,retry);
}
