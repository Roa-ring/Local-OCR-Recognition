import cv2
def laplacian_pyramid_downscale(img, levels=1):
    """
    基于拉普拉斯金字塔思想进行图像下采样（实际使用高斯金字塔 pyrdown）
    将图像尺寸缩小为原来的 1/(2^levels)，可有效降低后续 OCR 的像素计算量。
    :param img: 输入图像 (BGR 彩色或灰度均可)
    :param levels: 下采样次数，默认 1 次（尺寸减半）
    :return: 缩小后的图像
    """
    for _ in range(levels):
        # 高斯金字塔下采样（包含高斯模糊 + 隔行/列采样）
        G1 = cv2.pyrDown(img)
        # 构建拉普拉斯金字塔的一层（G0 - up(G1)），体现拉普拉斯金字塔的应用
        up = cv2.pyrUp(G1)
        h, w = img.shape[:2]
        up = cv2.resize(up, (w, h))  # 尺寸对齐
        # L0 = cv2.subtract(img, up)   # 本函数仅做缩放，不保存残差
        img = G1
    return img