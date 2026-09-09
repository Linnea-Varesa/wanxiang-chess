#ifndef CONFIG_H
#define CONFIG_H

// ============================================================
// 万象实体互动桌 - 配置文件
// 根据你的实际接线修改这里的引脚定义
// ============================================================

// ---------- 电机引脚 ----------
#define X_DIR_PIN   13
#define X_STEP_PIN  14
#define X_EN_PIN    15
#define Y_DIR_PIN   26
#define Y_STEP_PIN  27
#define Y_EN_PIN    25

// ---------- 电磁铁引脚 ----------
#define MAG_PIN     32   // PWM输出，经MOS管控制电磁铁

// ---------- 限位开关引脚 ----------
// 接线：一端接GPIO，一端接GND（使用内部上拉）
#define X_LIMIT_MIN 34   // X轴左限位
#define X_LIMIT_MAX 35   // X轴右限位
#define Y_LIMIT_MIN 36   // Y轴前限位
#define Y_LIMIT_MAX 39   // Y轴后限位

// ---------- 蜂鸣器（可选） ----------
#define BUZZER_PIN  4

// ---------- 机械参数（需标定后修改） ----------
#define STEPS_PER_MM    80.0    // 每毫米步数（同步带+20齿同步轮约80）
#define MAX_SPEED       2000    // 最大速度（步/秒）
#define ACCELERATION    1500    // 加速度（步/秒²）
#define TRAVEL_MM_X     250     // X轴行程(mm)
#define TRAVEL_MM_Y     250     // Y轴行程(mm)

// ---------- 棋盘参数 ----------
#define GRID_SIZE_MM    30.0    // 棋盘格距(mm)
#define GRID_COUNT      8       // 棋盘格数（8×8）

// ---------- 电磁铁参数 ----------
#define MAG_PWM_FREQ    1000    // PWM频率
#define MAG_PWM_CHANNEL 0       // LEDC通道
#define MAG_HOLD_TIME_MS 30000  // 连续吸合最大时间（过热保护）

// ---------- BLE参数 ----------
#define BLE_DEVICE_NAME "WanxiangTable"
#define BLE_SERVICE_UUID        "0000ffe0-0000-1000-8000-00805f9b34fb"
#define BLE_CHARACTERISTIC_UUID "0000ffe1-0000-1000-8000-00805f9b34fb"

// ---------- 安全参数 ----------
#define COMMAND_TIMEOUT_MS  10000   // 指令超时（无指令自动断电电机）
#define DEBOUNCE_MS         10      // 限位开关消抖

#endif // CONFIG_H
