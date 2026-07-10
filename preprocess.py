import cv2
import numpy as np
from numba import njit, prange

def bgr_to_gray(image):
    """
    等效于 cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    """
    # NumPy 矩阵乘法加速: B * 0.114 + G * 0.587 + R * 0.299
    gray = np.dot(image[..., :3], [0.114, 0.587, 0.299])
    return np.round(gray).astype(np.uint8)

@njit(parallel=True, cache=True)
def histogram_median_filter(image: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    """
    Histogram Sliding Median Filter (row-wise sliding)
    Parameters
    ----------
    image : uint8 2D ndarray
    kernel_size : odd integer (3,5,...)

    Returns
    -------
    uint8 ndarray
    """
    if kernel_size % 2 == 0:
        raise ValueError("kernel_size must be odd")

    h, w = image.shape
    r = kernel_size // 2
    total = kernel_size * kernel_size
    target = total // 2 + 1

    result = np.empty_like(image)

    for y in prange(h):

        hist = np.zeros(256, dtype=np.int32)

        # ---------- Build histogram for first window ----------
        for dy in range(-r, r + 1):
            yy = y + dy
            if yy < 0:
                yy = 0
            elif yy >= h:
                yy = h - 1

            for dx in range(-r, r + 1):
                xx = dx
                if xx < 0:
                    xx = 0
                elif xx >= w:
                    xx = w - 1

                hist[image[yy, xx]] += 1

        # ---------- Slide horizontally ----------
        for x in range(w):

            count = 0
            median = 0
            for gray in range(256):
                count += hist[gray]
                if count >= target:
                    median = gray
                    break

            result[y, x] = median

            if x == w - 1:
                continue

            remove_x = x - r
            add_x = x + r + 1

            for dy in range(-r, r + 1):

                yy = y + dy
                if yy < 0:
                    yy = 0
                elif yy >= h:
                    yy = h - 1

                rx = remove_x
                if rx < 0:
                    rx = 0
                elif rx >= w:
                    rx = w - 1

                ax = add_x
                if ax < 0:
                    ax = 0
                elif ax >= w:
                    ax = w - 1

                hist[image[yy, rx]] -= 1
                hist[image[yy, ax]] += 1

    return result