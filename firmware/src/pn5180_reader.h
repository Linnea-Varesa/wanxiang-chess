#pragma once
#include <Arduino.h>
struct Pn5180Reading { bool ok; String uid; String error; };
void pn5180Begin();
Pn5180Reading pn5180Read();
