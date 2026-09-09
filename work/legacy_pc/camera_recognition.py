#!/usr/bin/env python3
"""
万象实体互动桌 - 摄像头ArUco识别模块
功能：从顶部摄像头识别棋盘上互动片的位置和ID
"""

import cv2
import numpy as np
import argparse
import time


class ArucoRecognizer:
    """ArUco标记识别器"""
    
    def __init__(self, camera_id=0, grid_size=8, grid_mm=30.0):
        self.camera_id = camera_id
        self.grid_size = grid_size  # 8×8
        self.grid_mm = grid_mm      # 格距mm
        self.cap = None
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.aruco_params = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.aruco_params)
        
        # 棋盘角点标定（需要先运行calibration）
        self.board_corners = None  # [[x1,y1],[x2,y2],[x3,y3],[x4,y4]] 左上、右上、右下、左下
        
    def open(self):
        """打开摄像头"""
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            raise RuntimeError(f"无法打开摄像头 {self.camera_id}")
        # 设置分辨率
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        print(f"[Camera] 摄像头已打开: {self.camera_id}")
        
    def close(self):
        if self.cap:
            self.cap.release()
            
    def capture(self):
        """捕获一帧"""
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame
    
    def detect_markers(self, frame):
        """
        检测ArUco标记
        返回: list of (marker_id, center_x, center_y, corners)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = self.detector.detectMarkers(gray)
        
        results = []
        if ids is not None:
            for i, marker_id in enumerate(ids.flatten()):
                corner = corners[i][0]
                cx = int(np.mean(corner[:, 0]))
                cy = int(np.mean(corner[:, 1]))
                results.append((int(marker_id), cx, cy, corner))
        return results
    
    def pixel_to_grid(self, px, py):
        """将像素坐标转换为棋盘格坐标(row, col)"""
        if self.board_corners is None:
            # 未标定，用简单映射（假设棋盘占满画面）
            h, w = 720, 1280
            col = int(px / w * self.grid_size)
            row = int(py / h * self.grid_size)
            return max(0, min(self.grid_size-1, row)), max(0, min(self.grid_size-1, col))
        
        # 透视变换标定
        src = np.float32(self.board_corners)
        dst = np.float32([[0, 0], [self.grid_size, 0], 
                          [self.grid_size, self.grid_size], [0, self.grid_size]])
        M = cv2.getPerspectiveTransform(src, dst)
        point = np.array([[[px, py]]], dtype=np.float32)
        transformed = cv2.perspectiveTransform(point, M)
        col = int(transformed[0][0][0])
        row = int(transformed[0][0][1])
        return max(0, min(self.grid_size-1, row)), max(0, min(self.grid_size-1, col))
    
    def get_board_state(self, frame=None):
        """
        获取当前棋盘状态
        返回: dict {(row, col): marker_id}
        """
        if frame is None:
            frame = self.capture()
            if frame is None:
                return {}
        
        markers = self.detect_markers(frame)
        board = {}
        for marker_id, cx, cy, _ in markers:
            row, col = self.pixel_to_grid(cx, cy)
            board[(row, col)] = marker_id
        return board
    
    def calibrate(self):
        """
        交互式标定棋盘角点
        在画面中依次点击四个角：左上、右上、右下、左下
        """
        print("[Calibration] 请依次点击棋盘的四个角：左上、右上、右下、左下")
        corners = []
        
        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN and len(corners) < 4:
                corners.append([x, y])
                print(f"  已选择角点 {len(corners)}: ({x}, {y})")
        
        cv2.namedWindow("Calibration")
        cv2.setMouseCallback("Calibration", mouse_callback)
        
        while len(corners) < 4:
            frame = self.capture()
            if frame is None:
                break
            # 画已选角点
            for i, (x, y) in enumerate(corners):
                cv2.circle(frame, (x, y), 8, (0, 0, 255), -1)
                cv2.putText(frame, str(i+1), (x+10, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(frame, f"Select corner {len(corners)+1}/4 (press ESC to cancel)", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.imshow("Calibration", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
        
        cv2.destroyWindow("Calibration")
        
        if len(corners) == 4:
            self.board_corners = corners
            print("[Calibration] 标定完成")
            return True
        return False
    
    def show_overlay(self, frame, board_state):
        """在画面上叠加识别结果"""
        # 画网格
        h, w = frame.shape[:2]
        for i in range(self.grid_size + 1):
            cv2.line(frame, (0, i * h // self.grid_size), (w, i * h // self.grid_size), (100, 100, 100), 1)
            cv2.line(frame, (i * w // self.grid_size, 0), (i * w // self.grid_size, h), (100, 100, 100), 1)
        
        # 标记识别到的互动片
        for (row, col), marker_id in board_state.items():
            cx = int((col + 0.5) * w / self.grid_size)
            cy = int((row + 0.5) * h / self.grid_size)
            cv2.circle(frame, (cx, cy), 20, (0, 255, 0), 2)
            cv2.putText(frame, f"ID:{marker_id}", (cx-20, cy+30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        return frame


def main():
    parser = argparse.ArgumentParser(description="ArUco识别测试")
    parser.add_argument("--camera", type=int, default=0, help="摄像头ID")
    parser.add_argument("--show", action="store_true", help="显示画面")
    parser.add_argument("--calibrate", action="store_true", help="运行标定")
    args = parser.parse_args()
    
    recognizer = ArucoRecognizer(camera_id=args.camera)
    recognizer.open()
    
    if args.calibrate:
        recognizer.calibrate()
    
    if args.show:
        print("按 'q' 退出")
        while True:
            frame = recognizer.capture()
            if frame is None:
                break
            
            board = recognizer.get_board_state(frame)
            frame = recognizer.show_overlay(frame, board)
            
            cv2.putText(frame, f"Markers: {len(board)}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("Aruco Recognition", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()
    else:
        # 只输出识别结果
        try:
            while True:
                board = recognizer.get_board_state()
                print(f"检测到 {len(board)} 枚互动片: {board}")
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
    
    recognizer.close()


if __name__ == "__main__":
    main()
