import cv2
import numpy as np

def denoise_nlmeans(img, h=10, template_window_size=7, search_window_size=21):
    """
    使用非局部均值去噪 (fastNlMeans) 对图像进行降噪。

    Args:
        img (numpy.ndarray): 输入图像 (灰度图: HxW, 彩色图: HxWxC)
        h (float): 滤波强度。值越大去噪越强，但也越模糊。
                   灰度图典型值 5~25；彩色图通常 3~10。
        template_window_size (int): 用于计算相似度的块大小，推荐 7 (奇数)。
        search_window_size (int): 搜索相似块的范围，推荐 21 (奇数)。
                                  值越大计算越慢，但效果可能更好。

    Returns:
        numpy.ndarray: 降噪后的图像，类型与输入一致。
    """
    if img is None:
        raise ValueError("输入图像为空")

    # 判断图像通道数
    if len(img.shape) == 3 and img.shape[2] == 3:
        # 彩色图使用 fastNlMeansDenoisingColored
        # 参数说明: h 适用于亮度通道，hColor 是颜色通道的滤波强度（通常设为 h 的 1.5~2倍）
        h_color = h * 1.5
        denoised = cv2.fastNlMeansDenoisingColored(
            img, None, h, h_color, template_window_size, search_window_size
        )
    else:
        # 灰度图
        denoised = cv2.fastNlMeansDenoising(
            img, None, h, template_window_size, search_window_size
        )
    return denoised


# ============ 使用示例 ============
img_color = cv2.imread('test.jpg')
img_gray = cv2.imread('test.jpg', cv2.IMREAD_GRAYSCALE)

# 彩色图去噪 (h=5 适合彩色)
denoised_color_nl = denoise_nlmeans(img_color, h=5, template_window_size=7, search_window_size=21)

# 灰度图去噪 (h=10 适合灰度)
denoised_gray_nl = denoise_nlmeans(img_gray, h=10, template_window_size=7, search_window_size=21)

cv2.imwrite('denoised_nlmeans_color.png', denoised_color_nl)
cv2.imwrite('denoised_nlmeans_gray.png', denoised_gray_nl)
