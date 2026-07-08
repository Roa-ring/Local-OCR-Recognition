"""
app.py — PaddleOCR Flask HTTP API 服务
=======================================
启动命令：python app.py
服务地址：http://localhost:5000

接口说明：
  POST /ocr
    - 请求格式：multipart/form-data，字段名 "file"，值为图片文件
    - 成功响应：{"code": 0, "data": {"text": "...", "blocks": [...], "elapsed_ms": 320}}
    - 失败响应：{"code": -1, "message": "错误原因"}

图像预处理流程（按顺序执行）：
  1. preprocess_grayscale  — 图像灰度化（待完善）
  2. preprocess_denoise    — 图像去噪（待完善）
  3. preprocess_deskew     — 文本倾斜矫正（待完善）
"""

import time
import os
import tempfile

import cv2
import numpy as np
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from paddleocr import PaddleOCR

# ============================================================
# 初始化 Flask 应用
# 让 Flask 同时托管前端页面（ocr-electron/dist/ 文件夹）
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, "ocr-electron", "dist")

app = Flask(__name__, static_folder=DIST_DIR, static_url_path="")
CORS(app)

# ============================================================
# 初始化 PaddleOCR（启动时加载一次，避免每次请求都重新加载）
# ============================================================
print("正在加载 OCR 模型，请稍候...")
ocr = PaddleOCR(
    text_detection_model_name="PP-OCRv6_medium_det",
    text_recognition_model_name="PP-OCRv6_medium_rec",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=True,
)
print("OCR 模型加载完成，服务已就绪！")


# ============================================================
# 图像预处理函数（后续在此处完善算法）
# 输入/输出均为 numpy.ndarray（OpenCV 图像）
# ============================================================

def preprocess_grayscale(image: np.ndarray) -> np.ndarray:
    """
    图像灰度化
    ——————————————————————————————————————
    TODO: 在此处实现灰度化算法
    当前为直通（不做任何处理），保持原图输出。
    ——————————————————————————————————————
    """
    # 示例（取消注释即可启用）：
    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)  # 转回三通道供后续步骤使用
    return image


def preprocess_denoise(image: np.ndarray) -> np.ndarray:
    """
    图像去噪
    ——————————————————————————————————————
    TODO: 在此处实现去噪算法
    当前为直通（不做任何处理），保持原图输出。
    ——————————————————————————————————————
    """
    # 示例（取消注释即可启用）：
    # return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
    return image


def preprocess_deskew(image: np.ndarray) -> np.ndarray:
    """
    文本倾斜矫正
    ——————————————————————————————————————
    TODO: 在此处实现倾斜矫正算法
    当前为直通（不做任何处理），保持原图输出。
    ——————————————————————————————————————
    """
    # 示例思路：
    # 1. 转灰度 → 二值化 → 查找轮廓
    # 2. 用 cv2.minAreaRect 估算倾斜角度
    # 3. cv2.warpAffine 旋转矫正
    return image


def apply_preprocessing(image_path: str) -> str:
    """
    依次执行所有预处理步骤，返回处理后图像的临时文件路径。
    如果所有步骤均为直通，则直接返回原路径，不产生额外文件。
    """
    image = cv2.imread(image_path)
    if image is None:
        # 读取失败时直接返回原路径，交给 OCR 处理报错
        return image_path

    processed = image
    processed = preprocess_grayscale(processed)
    processed = preprocess_denoise(processed)
    processed = preprocess_deskew(processed)

    # 如果处理结果与原图完全相同（三个函数均为直通），跳过写文件
    if processed is image:
        return image_path

    # 将处理后的图像写入新的临时文件
    suffix = os.path.splitext(image_path)[1] or ".png"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        processed_path = tmp.name
    cv2.imwrite(processed_path, processed)
    return processed_path


# ============================================================
# 前端页面路由：访问任意路径都返回 index.html（SPA 支持）
# ============================================================
@app.route("/")
@app.route("/<path:path>")
def serve_frontend(path=""):
    full_path = os.path.join(DIST_DIR, path)
    if path and os.path.isfile(full_path):
        return send_from_directory(DIST_DIR, path)
    return send_from_directory(DIST_DIR, "index.html")


# ============================================================
# 接口：POST /ocr
# ============================================================
@app.route("/ocr", methods=["POST"])
def ocr_recognize():
    # 1. 检查是否有文件上传
    if "file" not in request.files:
        return jsonify({"code": -1, "message": "请上传图片文件，字段名为 'file'"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"code": -1, "message": "文件名为空"}), 400

    # 2. 将上传的图片保存到临时文件
    suffix = os.path.splitext(file.filename)[1] or ".png"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    processed_path = tmp_path  # 预处理后的路径（可能与 tmp_path 相同）

    try:
        # 3. 图像预处理（灰度化 → 去噪 → 倾斜矫正）
        processed_path = apply_preprocessing(tmp_path)

        # 4. 调用 PaddleOCR 识别
        start_time = time.time()
        results = ocr.predict(processed_path)
        elapsed_ms = int((time.time() - start_time) * 1000)

        # 5. 解析识别结果
        all_text_lines = []
        blocks = []

        for res in results:
            data = res.json()
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
                    block["bbox"] = dt_polys[i]
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
        return jsonify({"code": -1, "message": f"识别失败：{str(e)}"}), 500

    finally:
        # 6. 清理临时文件
        for path in {tmp_path, processed_path}:
            if path and os.path.exists(path):
                os.remove(path)


# ============================================================
# 健康检查接口
# ============================================================
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "OCR 服务运行中"})


# ============================================================
# 启动服务
# ============================================================
if __name__ == "__main__":
    print(f"前端页面地址：http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
