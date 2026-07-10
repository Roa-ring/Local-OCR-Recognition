# -*- coding: utf-8 -*-
import cv2
import numpy as np
import math
from preprocess import bgr_to_gray

def hough_transform(edges, threshold=120):
    h, w = edges.shape
    diag_len = int(math.sqrt(w * w + h * h))
    num_theta = 180
    num_rho = 2 * diag_len + 1
    accumulator = np.zeros((num_rho, num_theta), dtype=np.int32)
    
    y_idxs, x_idxs = np.where(edges > 0)
    
    # 预计算所有角度的cos和sin（向量）
    thetas = np.arange(num_theta) * math.pi / 180.0
    cos_vals = np.cos(thetas)
    sin_vals = np.sin(thetas)
    
    # 向量化计算：一次性算出所有边缘点对所有角度的rho
    # x_idxs 形状 (N,)，cos_vals 形状 (180,)
    # 利用广播：x_idxs[:, None] * cos_vals[None, :] 得到 (N, 180)
    rhos = x_idxs[:, None] * cos_vals[None, :] + y_idxs[:, None] * sin_vals[None, :]
    rho_idxs = np.round(rhos).astype(int) + diag_len
    
    #  向量化投票：用add.at实现累加 
    valid = (rho_idxs >= 0) & (rho_idxs < num_rho)
    # 对每个有效的(rho_idx, theta_idx)投票
    for j in range(num_theta):
        mask = valid[:, j]
        np.add.at(accumulator, (rho_idxs[mask, j], j), 1)
    
    lines = []
    for rho_idx in range(num_rho):
        for theta_idx in range(num_theta):
            if accumulator[rho_idx, theta_idx] >= threshold:
                rho = rho_idx - diag_len
                theta = theta_idx * math.pi / 180.0
                lines.append((rho, theta))
    return lines

# ========== 计算倾斜角度 ==========
def calculate_skew_angle(lines):
    if not lines:
        return 0.0
    angle_histogram = [0] * 180
    for rho, theta in lines:
        angle_deg = int(theta * 180.0 / math.pi) % 180
        if angle_deg < 0:
            angle_deg += 180
        angle_histogram[angle_deg] += 1
    max_count = 0
    peak_angle = 0
    for i in range(180):
        if angle_histogram[i] > max_count:
            max_count = angle_histogram[i]
            peak_angle = i
    return peak_angle - 90.0

# ========== 主程序 ==========
# 读取图片
def rotation_creation(img_path):
    original_image = cv2.imread(img_path)
    image = original_image.copy()
    if image is None:
        print("图片没找到，请检查文件名")
        exit()

    # 最大1000像素 缩图片提速
    h, w = image.shape[:2]
    max_dim = 1000
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        new_w = int(w * scale)
        new_h = int(h * scale)
        image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    # 转灰度+ 边缘检测
    gray = bgr_to_gray(image)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    # 动态阈值
    h_img, w_img = edges.shape
    diag_len_img = int(math.sqrt(w_img * w_img + h_img * h_img))
    auto_threshold = max(30, int(diag_len_img * 0.15))

    # Hough变换检测直线（使用动态阈值）
    lines = hough_transform(edges, auto_threshold)
    print(f"检测到 {len(lines)} 条直线 (阈值={auto_threshold})")

    # 计算倾斜角度
    angle = calculate_skew_angle(lines)
    print(f"倾斜角度: {angle:.2f} 度")


    # 旋转矫正
    h, w = original_image.shape[:2]
    center = (w // 2, h // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

    # 计算新尺寸防止裁 ?
    cos = abs(rotation_matrix[0, 0])
    sin = abs(rotation_matrix[0, 1])
    new_w = int(h * sin + w * cos)
    new_h = int(h * cos + w * sin)
    rotation_matrix[0, 2] += (new_w / 2) - center[0]
    rotation_matrix[1, 2] += (new_h / 2) - center[1]

    corrected = cv2.warpAffine(original_image, rotation_matrix, (new_w, new_h))
    cv2.imwrite("./cache/rotated.png",corrected)