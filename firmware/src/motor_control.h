#ifndef MOTOR_CONTROL_H
#define MOTOR_CONTROL_H

#include <AccelStepper.h>
#include "config.h"

class MotorControl {
public:
    MotorControl();
    void begin();
    
    // 相对移动（步）
    void moveRelative(long xSteps, long ySteps);
    
    // 相对移动（毫米）
    void moveRelativeMM(double xMm, double yMm);
    
    // 绝对移动到坐标（步）
    void moveTo(long xPos, long yPos);
    
    // 绝对移动到棋盘格 (row, col)
    void moveToGrid(int row, int col);
    
    // 回零（碰限位开关）
    bool home();
    
    // 阻塞等待运动完成
    void waitUntilDone();
    
    // 非阻塞运行（需在loop中调用）
    void run();
    
    // 立即停止
    void stop();
    
    // 使能/失能电机
    void enable();
    void disable();
    
    // 获取当前位置（步）
    long getXPosition();
    long getYPosition();
    
    // 获取当前位置（毫米）
    double getXMM();
    double getYMM();
    
    // 是否正在运动
    bool isRunning();
    
    // 设置速度
    void setSpeed(double speed);
    
private:
    AccelStepper _stepperX;
    AccelStepper _stepperY;
    bool _homed;
    bool _enabled;
    
    bool checkLimitX();
    bool checkLimitY();
};

#endif // MOTOR_CONTROL_H
