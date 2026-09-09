# 万象实体互动桌 · 全包工程

> 基于通用磁吸交互载体与低成本自动移动机构的多场景智能桌面产品

## 这是什么

一个**从零到一**的完整工程项目包，包含8个阶段的技术文档、可直接编译运行的固件代码、电脑端识别与AI代码、网页控制端、硬件BOM和组装指南。即使你是嵌入式新手，也能照着文档一步步做出可运行的样机。

## 工程结构

```
万象实体互动桌_全包工程/
├── README.md                    ← 你在这里
├── 00_快速开始.md               ← 新手先看这个
├── docs/                        ← 8个阶段技术文档
│   ├── 阶段1_需求与方案.md
│   ├── 阶段2_单元验证.md
│   ├── 阶段3_机械样机.md
│   ├── 阶段4_主控通信.md
│   ├── 阶段5_游戏闭环.md
│   ├── 阶段6_内容包装.md
│   ├── 阶段7_可靠性测试.md
│   └── 阶段8_答辩展示.md
├── firmware/                    ← ESP32-S3 固件（PlatformIO）
│   ├── platformio.ini
│   ├── src/                     ← 主程序源码
│   └── test/                    ← 单元测试代码
├── pc/                          ← 电脑端 Python 代码
│   ├── camera_recognition.py    ← 摄像头ArUco识别
│   ├── gomoku/                  ← 五子棋规则+AI
│   ├── chess_integration.py     ← 国际象棋集成
│   └── test_scripts/            ← 测试脚本
├── web/                         ← 网页控制端（BLE直连）
│   ├── index.html
│   ├── style.css
│   └── app.js
├── hardware/                    ← 硬件资料
│   ├── BOM.csv                  ← 物料清单
│   ├── wiring_diagram.md        ← 接线图说明
│   └── 3D_models/               ← 3D打印模型说明
└── tools/                       ← 工具脚本
    ├── calibration.py           ← 标定工具
    └── reliability_test.py      ← 可靠性自动测试
```

## 技术栈

| 层级 | 技术 | 说明 |
|---|---|---|
| 主控 | ESP32-S3 + Arduino框架 | 双核240MHz，Wi-Fi+BLE 5.0 |
| 电机驱动 | A4988 + 42步进电机 | 16细分，XY两轴 |
| 识别 | OpenCV + ArUco标记 | 电脑/手机端运行 |
| 通信 | BLE GATT | 手机/网页直连底座 |
| 五子棋AI | Minimax + α-β剪枝 | 纯Python实现 |
| 国际象棋 | python-chess + Stockfish | 开源引擎集成 |
| 控制端 | Web Bluetooth API | 浏览器直接连，无需装App |

## 预计总成本

- 极简版（用实验室设备）：约500元
- 标准版（全部采购）：约750～1100元
- 详见 `hardware/BOM.csv`

## 从哪里开始

1. **完全新手** → 先读 `00_快速开始.md`
2. **有基础** → 直接看 `docs/阶段1_需求与方案.md`
3. **只想看代码** → `firmware/` 和 `pc/` 目录

## 开源参考

- [ESP-IDF](https://github.com/espressif/esp-idf) / [Arduino-ESP32](https://github.com/espressif/arduino-esp32)
- [OpenCV](https://opencv.org/) / [ArUco标记](https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html)
- [Stockfish](https://github.com/official-stockfish/Stockfish)（国际象棋AI）
- [python-chess](https://github.com/niklasf/python-chess)
- [AccelStepper](http://www.airspayce.com/mikem/arduino/AccelStepper/)（步进电机库）
