#!/usr/bin/env python3
"""
标定工具 - 校准电机步距和棋盘坐标
"""

import serial
import time
import argparse
import sys


class Calibrator:
    def __init__(self, port, baudrate=115200):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # 等待ESP32启动
        
    def send_command(self, cmd, wait=True):
        """发送指令并等待响应"""
        self.ser.write((cmd + '\n').encode())
        if wait:
            time.sleep(0.1)
            response = self.ser.read_all().decode().strip()
            return response
        return ""
    
    def calibrate_steps_per_mm(self):
        """
        标定每毫米步数
        方法：让电机移动指定距离，测量实际移动距离，计算比例
        """
        print("=== 步距标定 ===")
        print("请准备尺子，测量实际移动距离")
        
        # 回零
        print("\n1. 回零...")
        print(self.send_command("HOME"))
        time.sleep(3)
        
        # 移动100mm（假设STEPS_PER_MM=80，即8000步）
        test_mm = 100
        test_steps = int(test_mm * 80)  # 用默认值先移动
        print(f"\n2. 移动 {test_mm}mm (发送 {test_steps} 步)...")
        print(self.send_command(f"MOVE,X,{test_steps}"))
        time.sleep(3)
        
        # 询问实际距离
        actual_mm = float(input(f"\n3. 请测量实际移动距离(mm): "))
        
        # 计算正确的STEPS_PER_MM
        correct_steps_per_mm = test_steps / actual_mm
        print(f"\n4. 标定结果:")
        print(f"   预期移动: {test_mm}mm")
        print(f"   实际移动: {actual_mm}mm")
        print(f"   正确的 STEPS_PER_MM = {correct_steps_per_mm:.2f}")
        print(f"\n请修改 firmware/src/config.h 中的 STEPS_PER_MM 为 {correct_steps_per_mm:.1f}")
        
        return correct_steps_per_mm
    
    def calibrate_grid(self):
        """
        标定棋盘格坐标
        让电磁铁移动到每个角，记录坐标
        """
        print("\n=== 棋盘格标定 ===")
        print("请观察电磁铁是否对准棋盘格中心")
        
        corners = [
            ("左上", 0, 0),
            ("右上", 0, 7),
            ("右下", 7, 7),
            ("左下", 7, 0),
            ("中心", 3, 3),
        ]
        
        for name, row, col in corners:
            input(f"\n按回车移动到 {name} (row={row}, col={col})...")
            print(self.send_command(f"GRID,ROW,{row},COL,{col}"))
            time.sleep(2)
            ok = input("是否对准？(y/n): ").strip().lower()
            if ok != 'y':
                print("需要调整GRID_SIZE_MM或中心偏移")
                print("当前 GRID_SIZE_MM = 30.0")
                print("如果整体偏移，修改 moveToGrid 中的 centerOffset")
        
        print("\n棋盘格标定完成")
    
    def close(self):
        self.ser.close()


def main():
    parser = argparse.ArgumentParser(description="标定工具")
    parser.add_argument("--port", required=True, help="串口端口，如 COM3 或 /dev/ttyUSB0")
    parser.add_argument("--mode", choices=['steps', 'grid', 'all'], default='all')
    args = parser.parse_args()
    
    try:
        cal = Calibrator(args.port)
    except Exception as e:
        print(f"无法打开串口: {e}")
        print("请检查端口号和连接")
        sys.exit(1)
    
    try:
        if args.mode in ('steps', 'all'):
            cal.calibrate_steps_per_mm()
        if args.mode in ('grid', 'all'):
            cal.calibrate_grid()
    except KeyboardInterrupt:
        print("\n标定中断")
    finally:
        cal.close()


if __name__ == "__main__":
    main()
