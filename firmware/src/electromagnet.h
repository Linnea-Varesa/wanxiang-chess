#ifndef ELECTROMAGNET_H
#define ELECTROMAGNET_H

#include "config.h"

class Electromagnet {
public:
    Electromagnet();
    void begin();
    
    void on();           // 吸合
    void off();          // 释放
    void pulse(int ms);  // 吸合指定毫秒后释放
    bool isOn();
    
    // 过热保护检查（在loop中调用）
    void tick();
    
private:
    bool _isOn;
    unsigned long _onStartTime;
};

#endif // ELECTROMAGNET_H
