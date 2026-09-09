#!/usr/bin/env python3
"""
ArUco标记生成工具
生成可打印的ArUco标记，贴在互动片顶部用于识别
"""

import cv2
import numpy as np
import os
import argparse


def generate_aruco_markers(ids, dictionary=cv2.aruco.DICT_4X4_50, size=300, border=1):
    """
    生成ArUco标记图片
    ids: 标记ID列表
    size: 标记像素大小（不含白边）
    border: 白边宽度（标记单元数）
    """
    aruco_dict = cv2.aruco.getPredefinedDictionary(dictionary)
    markers = {}
    
    for marker_id in ids:
        # 生成标记
        marker = cv2.aruco.generateImageMarker(aruco_dict, marker_id, size)
        # 添加白色边框（ArUco标记需要白边才能被识别）
        border_pixels = int(size * border / 8)
        marker_with_border = cv2.copyMakeBorder(
            marker, border_pixels, border_pixels, border_pixels, border_pixels,
            cv2.BORDER_CONSTANT, value=255
        )
        markers[marker_id] = marker_with_border
    
    return markers


def save_markers(markers, output_dir):
    """保存标记为PNG文件"""
    os.makedirs(output_dir, exist_ok=True)
    for marker_id, img in markers.items():
        path = os.path.join(output_dir, f"aruco_{marker_id:02d}.png")
        cv2.imwrite(path, img)
        print(f"  已保存: {path} ({img.shape[1]}x{img.shape[0]})")


def create_contact_sheet(markers, output_path, cols=4):
    """创建联系表（所有标记在一张图上，方便打印）"""
    if not markers:
        return
    
    # 统一尺寸
    size = list(markers.values())[0].shape[0]
    rows = (len(markers) + cols - 1) // cols
    
    # 创建画布
    padding = 40
    cell_size = size + padding
    sheet = np.ones((rows * cell_size + padding, cols * cell_size + padding), dtype=np.uint8) * 255
    
    for i, (marker_id, img) in enumerate(markers.items()):
        row = i // cols
        col = i % cols
        y = row * cell_size + padding // 2
        x = col * cell_size + padding // 2
        sheet[y:y+size, x:x+size] = img
        
        # 标注ID
        cv2.putText(sheet, f"ID:{marker_id}", 
                   (x + 5, y + size + 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0, 1)
    
    cv2.imwrite(output_path, sheet)
    print(f"\n联系表已保存: {output_path}")
    print(f"  尺寸: {sheet.shape[1]}x{sheet.shape[0]}")
    print(f"  共 {len(markers)} 个标记")


def main():
    parser = argparse.ArgumentParser(description="生成ArUco标记")
    parser.add_argument("--ids", type=int, nargs="+", default=list(range(10)),
                       help="标记ID列表，默认0-9")
    parser.add_argument("--size", type=int, default=300, help="标记像素大小")
    parser.add_argument("--output", default="aruco_markers", help="输出目录")
    parser.add_argument("--sheet", action="store_true", help="生成联系表")
    args = parser.parse_args()
    
    print(f"生成 {len(args.ids)} 个ArUco标记 (ID: {args.ids})")
    print(f"字典: 4X4_50, 大小: {args.size}px")
    
    markers = generate_aruco_markers(args.ids, size=args.size)
    save_markers(markers, args.output)
    
    if args.sheet:
        create_contact_sheet(markers, os.path.join(args.output, "contact_sheet.png"))
    
    print("\n使用说明:")
    print("  1. 打印标记（建议用激光打印机，确保清晰）")
    print("  2. 裁剪后贴在互动片顶部中心")
    print("  3. 标记周围必须保留白色边框")
    print("  4. 标记尺寸建议15×15mm（互动片直径25mm）")


if __name__ == "__main__":
    main()
