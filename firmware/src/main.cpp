// ============================================================
// 万象实体互动桌 - ESP32-S3 主固件
// 功能：XY电机控制 + 电磁铁 + BLE通信 + 限位保护
// ============================================================

#include <Arduino.h>
#include "config.h"
#include "motor_control.h"
#include "electromagnet.h"
#include "ble_service.h"
#include "command_parser.h"

MotorControl motor;
Electromagnet mag;
BLEService ble;

unsigned long lastCommandTime = 0;

// 处理BLE/串口收到的指令
void handleCommand(const std::string& command) {
    lastCommandTime = millis();
    
    auto args = CommandParser::parse(command);
    if (args.empty()) return;
    
    std::string type = CommandParser::getType(command);
    std::string response;
    
    if (type == "MOVE") {
        // MOVE,X,200,Y,-100  (相对移动，单位：步)
        long x = CommandParser::getArgInt(args, "X", 0);
        long y = CommandParser::getArgInt(args, "Y", 0);
        motor.moveRelative(x, y);
        motor.waitUntilDone();
        response = "OK,MOVE_DONE";
    }
    else if (type == "MOVEMM") {
        // MOVEMM,X,10,Y,-5  (相对移动，单位：毫米)
        double x = CommandParser::getArgInt(args, "X", 0);
        double y = CommandParser::getArgInt(args, "Y", 0);
        motor.moveRelativeMM(x, y);
        motor.waitUntilDone();
        response = "OK,MOVE_DONE";
    }
    else if (type == "GOTO") {
        // GOTO,X,1000,Y,500  (绝对移动，单位：步)
        long x = CommandParser::getArgInt(args, "X", 0);
        long y = CommandParser::getArgInt(args, "Y", 0);
        motor.moveTo(x, y);
        motor.waitUntilDone();
        response = "OK,GOTO_DONE";
    }
    else if (type == "GRID") {
        // GRID,ROW,3,COL,4  (移动到棋盘格)
        int row = CommandParser::getArgInt(args, "ROW", 0);
        int col = CommandParser::getArgInt(args, "COL", 0);
        motor.moveToGrid(row, col);
        motor.waitUntilDone();
        response = "OK,GRID_DONE";
    }
    else if (type == "PIECE") {
        // PIECE,FROMROW,3,FROMCOL,2,TOROW,5,TOCOL,4
        // 完整移动一枚互动片：移动到起点→吸合→移动到终点→释放
        int fromRow = CommandParser::getArgInt(args, "FROMROW", 0);
        int fromCol = CommandParser::getArgInt(args, "FROMCOL", 0);
        int toRow = CommandParser::getArgInt(args, "TOROW", 0);
        int toCol = CommandParser::getArgInt(args, "TOCOL", 0);
        
        if (args.size() < 9 || fromRow < 0 || fromRow > 7 || fromCol < 0 || fromCol > 7 ||
            toRow < 0 || toRow > 7 || toCol < 0 || toCol > 7) {
            response = "ERR,INVALID_PIECE";
            Serial.println(response.c_str());
            ble.notify(response);
            return;
        }
        
        motor.moveToGrid(fromRow, fromCol);
        motor.waitUntilDone();
        mag.on();
        delay(100);
        motor.moveToGrid(toRow, toCol);
        motor.waitUntilDone();
        mag.off();
        response = "OK,PIECE_DONE";
    }
    else if (type == "HOME") {
        motor.home();
        response = "OK,HOME_DONE";
    }
    else if (type == "MAG") {
        // MAG,ON 或 MAG,OFF 或 MAG,PULSE,500
        std::string action = args.size() > 1 ? args[1] : "";
        if (action == "ON") {
            mag.on();
            response = "OK,MAG_ON";
        } else if (action == "OFF") {
            mag.off();
            response = "OK,MAG_OFF";
        } else if (action == "PULSE") {
            int ms = args.size() > 2 ? std::stol(args[2]) : 300;
            mag.pulse(ms);
            response = "OK,MAG_PULSE";
        }
    }
    else if (type == "SPEED") {
        // SPEED,1500
        double speed = args.size() > 1 ? std::stod(args[1]) : MAX_SPEED;
        motor.setSpeed(speed);
        response = "OK,SPEED_SET";
    }
    else if (type == "STATUS" || type == "STATUS?") {
        char buf[128];
        snprintf(buf, sizeof(buf), "STATUS,X:%ld,Y:%ld,MAG:%s,READY",
                 motor.getXPosition(), motor.getYPosition(),
                 mag.isOn() ? "ON" : "OFF");
        response = buf;
    }
    else if (type == "ENABLE") {
        motor.enable();
        response = "OK,ENABLED";
    }
    else if (type == "DISABLE") {
        motor.disable();
        response = "OK,DISABLED";
    }
    else if (type == "STOP") {
        motor.stop();
        mag.off();
        response = "OK,STOPPED";
    }
    else if (type == "HELP") {
        response = "COMMANDS:MOVE,MOVEMM,GOTO,GRID,PIECE,HOME,MAG,SPEED,STATUS,ENABLE,DISABLE,STOP";
    }
    else {
        response = "ERR,UNKNOWN_CMD";
    }
    
    // 发送响应
    Serial.println(response.c_str());
    ble.notify(response);
}

void setup() {
    Serial.begin(115200);
    delay(1000);
    
    Serial.println("\n========================================");
    Serial.println("  万象实体互动桌 - ESP32-S3 固件");
    Serial.println("  版本: v1.0");
    Serial.println("========================================");
    
    // 初始化各模块
    motor.begin();
    mag.begin();
    ble.begin(handleCommand);
    
    // 上电自动回零（可选，注释掉可跳过）
    // motor.home();
    
    Serial.println("[System] 初始化完成，等待指令...");
    Serial.println("[System] 输入 HELP 查看可用指令");
}

void loop() {
    // 电机非阻塞运行
    motor.run();
    
    // 电磁铁过热保护
    mag.tick();
    
    // 串口指令（调试用）
    if (Serial.available()) {
        String cmd = Serial.readStringUntil('\n');
        cmd.trim();
        if (cmd.length() > 0) {
            handleCommand(cmd.c_str());
        }
    }
    
    // 指令超时保护：长时间无指令自动断电电机
    if (motor.isRunning() == false && 
        millis() - lastCommandTime > COMMAND_TIMEOUT_MS &&
        lastCommandTime > 0) {
        // 电机失能省电（不影响电磁铁）
        // motor.disable();  // 如需启用超时断电，取消注释
    }
    
    delay(1);
}
