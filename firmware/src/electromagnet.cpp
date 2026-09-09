#include "electromagnet.h"
#include <Arduino.h>

Electromagnet::Electromagnet() : _isOn(false), _onStartTime(0) {}

void Electromagnet::begin() {
    // 使用LEDC PWM控制
    ledcSetup(MAG_PWM_CHANNEL, MAG_PWM_FREQ, 8);
    ledcAttachPin(MAG_PIN, MAG_PWM_CHANNEL);
    ledcWrite(MAG_PWM_CHANNEL, 0);  // 初始关闭
    Serial.println("[Mag] 电磁铁初始化完成");
}

void Electromagnet::on() {
    ledcWrite(MAG_PWM_CHANNEL, 255);  // 满占空比
    _isOn = true;
    _onStartTime = millis();
    Serial.println("[Mag] 电磁铁吸合");
}

void Electromagnet::off() {
    ledcWrite(MAG_PWM_CHANNEL, 0);
    _isOn = false;
    Serial.println("[Mag] 电磁铁释放");
}

void Electromagnet::pulse(int ms) {
    on();
    delay(ms);
    off();
}

bool Electromagnet::isOn() { return _isOn; }

void Electromagnet::tick() {
    // 过热保护：连续吸合超过设定时间自动释放
    if (_isOn && (millis() - _onStartTime > MAG_HOLD_TIME_MS)) {
        Serial.println("[Mag] 过热保护：自动释放电磁铁");
        off();
    }
}
