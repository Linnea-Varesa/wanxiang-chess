#!/usr/bin/env python3
"""摄像头测试脚本 - 验证摄像头是否正常工作"""

import cv2
import sys

def test_camera(camera_id=0):
    print(f"正在打开摄像头 {camera_id}...")
    cap = cv2.VideoCapture(camera_id)
    
    if not cap.isOpened():
        print(f"错误: 无法打开摄像头 {camera_id}")
        print("请检查:")
        print("  1. 摄像头是否连接")
        print("  2. 尝试其他 camera_id (0, 1, 2...)")
        return False
    
    # 读取一帧测试
    ret, frame = cap.read()
    if not ret or frame is None:
        print("错误: 无法读取画面")
        cap.release()
        return False
    
    h, w = frame.shape[:2]
    print(f"摄像头已打开，分辨率: {w}x{h}")
    print("按 'q' 退出测试")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        cv2.putText(frame, "Camera OK - Press 'q' to quit", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("Camera Test", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("测试完成")
    return True

if __name__ == "__main__":
    camera_id = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    test_camera(camera_id)
