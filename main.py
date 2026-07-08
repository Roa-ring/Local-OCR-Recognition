import cv2
import numpy as np
from paddleocr import PaddleOCR

"""图像预处理"""
def process(image_path):
    # 1. 读取图像
    img = cv2.imread(image_path)
    # 2. 灰度化
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 返回处理后的图像 (用于PaddleOCR) 和原始图像 (用于可视化)
    denoised = cv2.fastNlMeansDenoising(gray)
    # 创建 CLAHE 对象（调整参数）
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    # 应用 CLAHE
    enhanced = clahe.apply(denoised)
    cv2.imwrite('cache/output.png' , enhanced)
    return enhanced

"""调用paddleocr识别文字"""
input = "c2990ee0d065aa5b079f5d55641e47ec.jpg"
process(input)
ocr = PaddleOCR(
    text_detection_model_name="PP-OCRv6_medium_det",
    text_recognition_model_name="PP-OCRv6_medium_rec",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=True,
)
result = ocr.predict("cache/output.png")
for res in result:
    res.print()
    res.save_to_img("output")
    res.save_to_json("output")