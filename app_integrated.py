"""
app.py — 本地 OCR 文字识别服务
用法：python app.py
浏览器访问：http://localhost:5000
"""

import time
import os
import tempfile
import traceback
import uuid

import cv2
import numpy as np
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from paddleocr import PaddleOCR
from preprocess import bgr_to_gray, histogram_median_filter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, "ocr-electron", "dist")
TMP_DIR = os.path.join(BASE_DIR, "_tmp")
CACHE_DIR = os.path.join(BASE_DIR, "cache")
os.makedirs(TMP_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

app = Flask(__name__, static_folder=DIST_DIR, static_url_path="")
CORS(app)

print("正在加载 OCR 模型，请稍候...")
ocr = PaddleOCR(
    text_detection_model_name="PP-OCRv6_medium_det",
    text_recognition_model_name="PP-OCRv6_medium_rec",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=True,
)
print("OCR 模型加载完成！")
print("前端页面地址：http://localhost:5000")


def apply_preprocessing(image_path: str) -> str:
    """
    图像预处理流程：
    1. 灰度化（bgr_to_gray）
    2. 直方图滑动中值滤波去噪（histogram_median_filter）
    3. CLAHE 对比度增强
    返回处理后图像的临时文件路径。
    """
    img = cv2.imread(image_path)
    if img is None:
        return image_path

    # 1. 灰度化
    gray = bgr_to_gray(img)

    # 2. 直方图滑动中值滤波去噪
    denoised = histogram_median_filter(gray)

    # 3. CLAHE 对比度增强
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)

    # 保存到临时文件供 OCR 使用
    suffix = os.path.splitext(image_path)[1] or ".png"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=TMP_DIR) as tmp:
        processed_path = tmp.name
    cv2.imwrite(processed_path, enhanced)
    return processed_path


@app.route("/")
@app.route("/<path:path>")
def serve_frontend(path=""):
    full_path = os.path.join(DIST_DIR, path)
    if path and os.path.isfile(full_path):
        return send_from_directory(DIST_DIR, path)
    return send_from_directory(DIST_DIR, "index.html")


@app.route("/ocr", methods=["POST"])
def ocr_recognize():
    if "file" not in request.files:
        return jsonify({"code": -1, "message": "请上传图片文件，字段名为 'file'"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"code": -1, "message": "文件名为空"}), 400

    suffix = os.path.splitext(file.filename)[1] or ".png"
    tmp_path = os.path.join(TMP_DIR, f"{uuid.uuid4().hex}{suffix}")
    file.save(tmp_path)

    processed_path = tmp_path

    try:
        processed_path = apply_preprocessing(tmp_path)

        start_time = time.time()
        results = ocr.predict(processed_path)
        elapsed_ms = int((time.time() - start_time) * 1000)

        all_text_lines = []
        blocks = []

        for res in results:
            # res.json 结构: {'res': {'rec_texts': [...], 'rec_scores': [...], 'dt_polys': [...], ...}}
            data = res.json.get("res", res.json)
            rec_texts = data.get("rec_texts", [])
            rec_scores = data.get("rec_scores", [])
            dt_polys = data.get("dt_polys", [])

            for i, text in enumerate(rec_texts):
                if not text.strip():
                    continue
                all_text_lines.append(text)
                block = {
                    "text": text,
                    "confidence": round(float(rec_scores[i]) if i < len(rec_scores) else 0.0, 4),
                }
                if i < len(dt_polys):
                    poly = dt_polys[i]
                    block["bbox"] = poly.tolist() if hasattr(poly, "tolist") else poly
                blocks.append(block)

        full_text = "\n".join(all_text_lines)

        return jsonify({
            "code": 0,
            "data": {
                "text": full_text,
                "blocks": blocks,
                "elapsed_ms": elapsed_ms,
            }
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"code": -1, "message": f"识别失败：{str(e)}"}), 500

    finally:
        for path in {tmp_path, processed_path}:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "OCR 服务运行中"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
