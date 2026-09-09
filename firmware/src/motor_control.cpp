#include "motor_control.h"
#include <Arduino.h>

MotorControl::MotorControl()
    : _stepperX(AccelStepper::DRIVER, X_STEP_PIN, X_DIR_PIN),
      _stepperY(AccelStepper::DRIVER, Y_STEP_PIN, Y_DIR_PIN),
      _homed(false), _enabled(false) {}

void MotorControl::begin() {
    // 初始化引脚
    pinMode(X_EN_PIN, OUTPUT);
    pinMode(Y_EN_PIN, OUTPUT);
    pinMode(X_LIMIT_MIN, INPUT_PULLUP);
    pinMode(X_LIMIT_MAX, INPUT_PULLUP);
    pinMode(Y_LIMIT_MIN, INPUT_PULLUP);
    pinMode(Y_LIMIT_MAX, INPUT_PULLUP);
    
    // 失能电机（低电平使能，所以HIGH=失能）
    digitalWrite(X_EN_PIN, HIGH);
    digitalWrite(Y_EN_PIN, HIGH);
    
    // 设置电机参数
    _stepperX.setMaxSpeed(MAX_SPEED);
    _stepperX.setAcceleration(ACCELERATION);
    _stepperY.setMaxSpeed(MAX_SPEED);
    _stepperY.setAcceleration(ACCELERATION);
    
    Serial.println("[Motor] 初始化完成");
}

void MotorControl::enable() {
    digitalWrite(X_EN_PIN, LOW);
    digitalWrite(Y_EN_PIN, LOW);
    _enabled = true;
    Serial.println("[Motor] 电机使能");
}

void MotorControl::disable() {
    digitalWrite(X_EN_PIN, HIGH);
    digitalWrite(Y_EN_PIN, HIGH);
    _enabled = false;
    Serial.println("[Motor] 电机失能");
}

void MotorControl::moveRelative(long xSteps, long ySteps) {
    if (!_enabled) enable();
    _stepperX.move(xSteps);
    _stepperY.move(ySteps);
}

void MotorControl::moveRelativeMM(double xMm, double yMm) {
    moveRelative((long)(xMm * STEPS_PER_MM), (long)(yMm * STEPS_PER_MM));
}

void MotorControl::moveTo(long xPos, long yPos) {
    if (!_enabled) enable();
    _stepperX.moveTo(xPos);
    _stepperY.moveTo(yPos);
}

void MotorControl::moveToGrid(int row, int col) {
    // 棋盘中心为原点，转换为毫米坐标
    double centerOffset = (GRID_COUNT - 1) * GRID_SIZE_MM / 2.0;
    double xMm = col * GRID_SIZE_MM - centerOffset;
    double yMm = row * GRID_SIZE_MM - centerOffset;
    moveTo((long)(xMm * STEPS_PER_MM), (long)(yMm * STEPS_PER_MM));
}

bool MotorControl::home() {
    Serial.println("[Motor] 开始回零...");
    if (!_enabled) enable();
    
    const long homeSpeed = 500;   // 回零速度
    const long slowSpeed = 200;   // 慢速回零速度
    
    // ---- X轴回零 ----
    _stepperX.setMaxSpeed(homeSpeed);
    _stepperX.moveTo(-100000);  // 往负方向一直走
    
    while (digitalRead(X_LIMIT_MIN) == HIGH) {
        _stepperX.run();
        if (digitalRead(X_LIMIT_MIN) == LOW) break;
    }
    _stepperX.stop();
    _stepperX.setCurrentPosition(0);
    
    // 退一点再慢速碰一次（提高精度）
    _stepperX.setMaxSpeed(slowSpeed);
    _stepperX.move(200);
    waitUntilDone();
    _stepperX.moveTo(-100000);
    while (digitalRead(X_LIMIT_MIN) == HIGH) {
        _stepperX.run();
    }
    _stepperX.stop();
    _stepperX.setCurrentPosition(0);
    
    // ---- Y轴回零 ----
    _stepperY.setMaxSpeed(homeSpeed);
    _stepperY.moveTo(-100000);
    while (digitalRead(Y_LIMIT_MIN) == HIGH) {
        _stepperY.run();
    }
    _stepperY.stop();
    _stepperY.setCurrentPosition(0);
    
    _stepperY.setMaxSpeed(slowSpeed);
    _stepperY.move(200);
    waitUntilDone();
    _stepperY.moveTo(-100000);
    while (digitalRead(Y_LIMIT_MIN) == HIGH) {
        _stepperY.run();
    }
    _stepperY.stop();
    _stepperY.setCurrentPosition(0);
    
    // 恢复正常速度
    _stepperX.setMaxSpeed(MAX_SPEED);
    _stepperY.setMaxSpeed(MAX_SPEED);
    
    _homed = true;
    Serial.println("[Motor] 回零完成");
    return true;
}

void MotorControl::waitUntilDone() {
    while (_stepperX.isRunning() || _stepperY.isRunning()) {
        _stepperX.run();
        _stepperY.run();
    }
}

void MotorControl::run() {
    _stepperX.run();
    _stepperY.run();
}

void MotorControl::stop() {
    _stepperX.stop();
    _stepperY.stop();
}

long MotorControl::getXPosition() { return _stepperX.currentPosition(); }
long MotorControl::getYPosition() { return _stepperY.currentPosition(); }
double MotorControl::getXMM() { return _stepperX.currentPosition() / STEPS_PER_MM; }
double MotorControl::getYMM() { return _stepperY.currentPosition() / STEPS_PER_MM; }
bool MotorControl::isRunning() { return _stepperX.isRunning() || _stepperY.isRunning(); }

void MotorControl::setSpeed(double speed) {
    _stepperX.setMaxSpeed(speed);
    _stepperY.setMaxSpeed(speed);
}
