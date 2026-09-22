#pragma once
#include <Arduino.h>
void monitorDisplayBegin();
void monitorDisplayShow(const char* channel, const char* uid, const char* status, uint16_t retry);
