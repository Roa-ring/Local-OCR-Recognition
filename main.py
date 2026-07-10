import cv2
from paddleocr import PaddleOCR
from preprocess import bgr_to_gray, histogram_median_filter
from history_manage import history_manage
from skew import rotation_creation
from js_cal import json_cal
import os

def filename(path):
    return os.path.splitext(os.path.basename(path))[0]

"""图像预处理"""
def process(image_path):
    # 1. 文本倾斜矫正
    rotation_creation(image_path)
    # 2. 读取图片
    img = cv2.imread("cache/rotated.png")
    if img is None:
        raise ValueError(f"无法解码图像文件: {image_path}，请检查文件格式是否支持或文件是否损坏。")
    # 3. 灰度化
    gray = bgr_to_gray(img)
    # 4. 中值滤波
    denoised = histogram_median_filter(gray)
    # 5. 创建 CLAHE 对象（调整参数）
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)
    cv2.imwrite("cache/"+filename(image_path)+".png" , enhanced)
    return enhanced

"""图像预处理"""
def reprocess(image_path):
    # 1. 文本倾斜矫正
    rotation_creation(image_path)
    # 2. 读取图片
    img = cv2.imread("cache/rotated.png")
    if img is None:
        raise ValueError(f"无法解码图像文件: {image_path}，请检查文件格式是否支持或文件是否损坏。")
    # 3. 灰度化
    gray = bgr_to_gray(img)
    # 5. 创建 CLAHE 对象（调整参数）
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    cv2.imwrite("cache/"+filename(image_path)+"2.png" , enhanced)
    return enhanced

def main(input):
    """调用paddleocr识别文字"""
    process(input)
    ocr = PaddleOCR(
        text_detection_model_name="PP-OCRv6_medium_det",
        text_recognition_model_name="PP-OCRv6_medium_rec",
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=True,
    )
    result = ocr.predict("./cache/"+filename(input)+".png")
    for res in result:
        res.print()
        res.save_to_json("cache")
    avg = json_cal("./cache/"+filename(input)+"_res.json")
    if avg < 0.9:
        reprocess(input)
        result2 = ocr.predict("./cache/"+filename(input)+"2.png")
        for res in result2:
            res.print()
            res.save_to_json("cache")
        if json_cal("./cache/"+filename(input)+"_res.json")>avg:
            result = result2
    history_manage(result=result,image_path=input)
main(input = "IMG_4648.PNG")
    
