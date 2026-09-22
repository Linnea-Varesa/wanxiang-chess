#include "pn5180_reader.h"
// PN5180 SPI 实际命令待根据到货 PNEV5180B/OM25180FDK 接口确认。
void pn5180Begin(){ Serial.println("PN5180,INIT_PENDING_WIRING_CHECK"); }
Pn5180Reading pn5180Read(){ return {false, "", "NOT_IMPLEMENTED"}; }
