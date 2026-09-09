#!/usr/bin/env python3
"""
可靠性自动测试脚本
测试项目：移动可靠性、识别准确率、BLE延迟
"""

import serial
import time
import random
import argparse
import sys
from datetime import datetime


class ReliabilityTester:
    def __init__(self, port, baudrate=115200):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)
        self.results = {}
        
    def send_command(self, cmd, timeout=5):
        """发送指令，等待OK响应"""
        start = time.time()
        self.ser.write((cmd + '\n').encode())
        self.ser.flush()
        
        while time.time() - start < timeout:
            line = self.ser.readline().decode().strip()
            if line.startswith('OK') or line.startswith('ERR') or line.startswith('STATUS'):
                return line, time.time() - start
        return None, timeout
    
    def test_movement(self, count=20):
        """移动可靠性测试"""
        print(f"\n=== 移动可靠性测试 ({count}次) ===")
        
        success = 0
        fail = 0
        details = []
        
        # 先回零
        print("回零中...")
        self.send_command("HOME", timeout=15)
        time.sleep(2)
        
        for i in range(count):
            # 随机目标位置
            x = random.randint(-5000, 5000)
            y = random.randint(-5000, 5000)
            
            response, elapsed = self.send_command(f"MOVE,X,{x},Y,{y}", timeout=10)
            
            if response and response.startswith('OK'):
                success += 1
                status = "✓"
            else:
                fail += 1
                status = "✗"
            
            details.append(f"  第{i+1:2d}次: 目标({x:5d},{y:5d}) {status} ({elapsed:.2f}s)")
            print(details[-1])
            time.sleep(0.5)
        
        rate = success / count * 100
        self.results['movement'] = {
            'total': count, 'success': success, 'fail': fail, 'rate': rate
        }
        
        print(f"\n结果: {success}/{count} 成功，成功率 {rate:.1f}%")
        return rate >= 90
    
    def test_ble_latency(self, count=50):
        """BLE延迟测试（通过串口模拟，实际BLE延迟需用手机端测试）"""
        print(f"\n=== 指令响应延迟测试 ({count}次) ===")
        
        delays = []
        for i in range(count):
            response, elapsed = self.send_command("STATUS?", timeout=2)
            if response:
                delays.append(elapsed * 1000)  # 转ms
            time.sleep(0.1)
        
        if delays:
            avg = sum(delays) / len(delays)
            max_d = max(delays)
            min_d = min(delays)
            self.results['latency'] = {'avg': avg, 'max': max_d, 'min': min_d, 'count': len(delays)}
            print(f"  平均延迟: {avg:.1f}ms")
            print(f"  最大延迟: {max_d:.1f}ms")
            print(f"  最小延迟: {min_d:.1f}ms")
            return avg < 300
        return False
    
    def test_continuous_move(self, count=20):
        """连续移动测试（模拟实际使用）"""
        print(f"\n=== 连续移动测试 ({count}次) ===")
        
        # 回零
        self.send_command("HOME", timeout=15)
        time.sleep(2)
        
        success = 0
        for i in range(count):
            # 模拟移动一枚互动片
            from_x = random.randint(-3000, 0)
            from_y = random.randint(-3000, 0)
            to_x = random.randint(0, 3000)
            to_y = random.randint(0, 3000)
            
            # 移动到起点
            self.send_command(f"GOTO,X,{from_x},Y,{from_y}", timeout=10)
            time.sleep(0.3)
            # 吸合
            self.send_command("MAG,ON")
            time.sleep(0.2)
            # 移动到终点
            resp, _ = self.send_command(f"GOTO,X,{to_x},Y,{to_y}", timeout=10)
            time.sleep(0.3)
            # 释放
            self.send_command("MAG,OFF")
            time.sleep(0.2)
            
            if resp and resp.startswith('OK'):
                success += 1
                print(f"  第{i+1:2d}次: ✓")
            else:
                print(f"  第{i+1:2d}次: ✗ 失败")
        
        rate = success / count * 100
        self.results['continuous'] = {'total': count, 'success': success, 'rate': rate}
        print(f"\n结果: {success}/{count} 成功，成功率 {rate:.1f}%")
        return rate >= 90
    
    def generate_report(self):
        """生成测试报告"""
        report = []
        report.append("=" * 50)
        report.append("万象实体互动桌 - 可靠性测试报告")
        report.append(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 50)
        
        if 'movement' in self.results:
            r = self.results['movement']
            report.append(f"\n【移动可靠性】")
            report.append(f"  测试次数: {r['total']}")
            report.append(f"  成功: {r['success']}")
            report.append(f"  失败: {r['fail']}")
            report.append(f"  成功率: {r['rate']:.1f}% {'✓ 通过' if r['rate']>=90 else '✗ 未通过'}")
        
        if 'latency' in self.results:
            r = self.results['latency']
            report.append(f"\n【指令延迟】")
            report.append(f"  测试次数: {r['count']}")
            report.append(f"  平均: {r['avg']:.1f}ms")
            report.append(f"  最大: {r['max']:.1f}ms")
            report.append(f"  最小: {r['min']:.1f}ms")
            report.append(f"  {'✓ 通过' if r['avg']<300 else '✗ 未通过'}")
        
        if 'continuous' in self.results:
            r = self.results['continuous']
            report.append(f"\n【连续移动（含电磁铁）】")
            report.append(f"  测试次数: {r['total']}")
            report.append(f"  成功: {r['success']}")
            report.append(f"  成功率: {r['rate']:.1f}% {'✓ 通过' if r['rate']>=90 else '✗ 未通过'}")
        
        report.append("\n" + "=" * 50)
        return "\n".join(report)
    
    def close(self):
        self.ser.close()


def main():
    parser = argparse.ArgumentParser(description="可靠性测试")
    parser.add_argument("--port", required=True, help="串口端口")
    parser.add_argument("--test", choices=['movement', 'latency', 'continuous', 'all'], default='all')
    parser.add_argument("--count", type=int, default=20, help="测试次数")
    args = parser.parse_args()
    
    try:
        tester = ReliabilityTester(args.port)
    except Exception as e:
        print(f"无法打开串口: {e}")
        sys.exit(1)
    
    try:
        if args.test in ('movement', 'all'):
            tester.test_movement(args.count)
        if args.test in ('latency', 'all'):
            tester.test_ble_latency(min(args.count * 2, 50))
        if args.test in ('continuous', 'all'):
            tester.test_continuous_move(args.count)
        
        print("\n" + tester.generate_report())
    except KeyboardInterrupt:
        print("\n测试中断")
    finally:
        tester.close()


if __name__ == "__main__":
    main()
