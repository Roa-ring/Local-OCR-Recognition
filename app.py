"""
app.py — 本地 OCR 文字识别服务（最终整合版）
用法：python app.py
浏览器访问：http://localhost:5000

整合功能：
- 图像预处理：灰度化、中值滤波去噪、CLAHE 对比度增强
- 倾斜矫正：基于 Hough 变换自动检测并矫正文本倾斜（skew.py）
- 细笔画补偿：置信度 < 0.9 时跳过中值滤波重试，取更优结果
- 历史记录：每次识别自动保存到 history/ 目录（output.py）
- 置信度计算：基于 rec_scores 计算平均置信度（json_cal.py）
- 历史搜索 API：支持按日期查询、关键词搜索
"""

import time
import os
import shutil
import traceback
import uuid
import json
import math
import threading

import cv2
import numpy as np
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from paddleocr import PaddleOCR

from preprocess import bgr_to_gray, histogram_median_filter
from skew import rotation_creation
from output import get_manager, extract_text_from_result
import indexmake

# ─── 目录配置 ─────────────────────────────────────────────────────────────────

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
FRONTEND   = os.path.join(BASE_DIR, "frontend")
TMP_DIR    = os.path.join(BASE_DIR, "_tmp")
CACHE_DIR  = os.path.join(BASE_DIR, "cache")
HISTORY_DIR = os.path.join(BASE_DIR, "history")

for d in (TMP_DIR, CACHE_DIR, HISTORY_DIR):
    os.makedirs(d, exist_ok=True)

# ─── Flask 初始化 ──────────────────────────────────────────────────────────────

app = Flask(__name__, static_folder=FRONTEND, static_url_path="")
CORS(app)

# ─── OCR 模型（全局单例，启动时加载一次） ──────────────────────────────────────

print("正在加载 OCR 模型，请稍候...")
ocr = PaddleOCR(
    text_detection_model_name="PP-OCRv6_medium_det",
    text_recognition_model_name="PP-OCRv6_medium_rec",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=True,
)
print("OCR 模型加载完成！访问 http://localhost:5000")

# OCR 全局锁：PaddleOCR 非线程安全，同一时刻只允许一个请求执行识别
_ocr_lock = threading.Lock()


# ─── 工具函数 ──────────────────────────────────────────────────────────────────

def _basename(path: str) -> str:
    return os.path.splitext(os.path.basename(path))[0]


def _limit_resolution(img: np.ndarray, max_dim: int = 4000) -> np.ndarray:
    """限制最大分辨率，防止 PaddleOCR Unknown exception"""
    h, w = img.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    return img


def _parse_ocr_results(results):
    """
    解析 PaddleOCR predict() 返回值，提取文本行、置信度列表和坐标块。
    返回: (all_text_lines, rec_scores, blocks)
    """
    all_text_lines = []
    rec_scores = []
    blocks = []

    for res in results:
        data = res.json.get("res", res.json)
        texts  = data.get("rec_texts",  [])
        scores = data.get("rec_scores", [])
        polys  = data.get("dt_polys",   [])

        for i, text in enumerate(texts):
            if not text.strip():
                continue
            score = float(scores[i]) if i < len(scores) else 0.0
            all_text_lines.append(text)
            rec_scores.append(score)
            block = {
                "text": text,
                "confidence": round(score, 4),
            }
            if i < len(polys):
                poly = polys[i]
                block["bbox"] = poly.tolist() if hasattr(poly, "tolist") else poly
            blocks.append(block)

    return all_text_lines, rec_scores, blocks


def _calc_avg_confidence(rec_scores: list) -> float:
    """直接从 rec_scores 列表计算平均置信度"""
    if not rec_scores:
        return 0.0
    return sum(rec_scores) / len(rec_scores)


def apply_preprocessing(image_path: str, use_denoise: bool = True) -> str:
    """
    图像预处理流程：
      1. 倾斜矫正（skew.rotation_creation → cache/rotated.png）
      2. 灰度化
      3. 中值滤波去噪（可选，use_denoise=False 时跳过，用于细笔画补偿）
      4. CLAHE 对比度增强
    返回处理后图像的临时文件路径。
    """
    # 1. 倾斜矫正：结果写入 cache/rotated.png
    try:
        rotation_creation(image_path)
        rotated_path = os.path.join(CACHE_DIR, "rotated.png")
        img = cv2.imread(rotated_path)
    except Exception:
        img = None

    if img is None:
        img = cv2.imread(image_path)
    if img is None:
        return image_path

    # 限制分辨率
    img = _limit_resolution(img)

    # 2. 灰度化
    gray = bgr_to_gray(img)

    # 3. 中值滤波去噪（细笔画补偿时跳过）
    if use_denoise:
        processed = histogram_median_filter(gray)
    else:
        processed = gray

    # 4. CLAHE 对比度增强
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(processed)

    # 保存到临时文件
    tmp_path = os.path.join(TMP_DIR, f"{uuid.uuid4().hex}.png")
    cv2.imwrite(tmp_path, enhanced)
    return tmp_path


def run_ocr(processed_path: str):
    """调用 OCR 并返回 (results, elapsed_ms)"""
    start = time.time()
    results = ocr.predict(processed_path)
    elapsed_ms = int((time.time() - start) * 1000)
    return results, elapsed_ms


def save_history(image_path: str, full_text: str, avg_conf: float, rec_scores: list):
    """
    将识别结果保存到历史记录目录。
    目录结构：history/<YYYYMMDD>_<N>/
      - <base>.txt   首行为置信度，其余为识别文本
      - <base>.jpg   原始图片副本
    """
    try:
        manager = get_manager()
        base = indexmake.get_next_base(HISTORY_DIR)
        record_dir = os.path.join(HISTORY_DIR, base)
        os.makedirs(record_dir, exist_ok=True)

        txt_file = f"{base}.txt"
        img_file = f"{base}.jpg"
        txt_path = os.path.join(record_dir, txt_file)
        img_path = os.path.join(record_dir, img_file)

        # 写入 txt（首行置信度）
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"置信度: {avg_conf:.4%}\n")
            f.write(full_text)

        # 复制原始图片
        shutil.copy2(image_path, img_path)

        # 构造记录并插入 BST
        date_key = int(base.split("_")[0])
        index    = int(base.split("_")[1])
        record = {
            "date":       date_key,
            "index":      index,
            "record_dir": base,
            "txt_file":   txt_file,
            "img_file":   img_file,
            "text":       full_text,
            "confidence": round(avg_conf, 6),
            "image_path": image_path,
            "file_size":  os.path.getsize(image_path),
        }
        manager.bst.insert(date_key, record)
        manager.save_index()
        return record
    except Exception:
        traceback.print_exc()
        return None


# ─── 前端路由 ──────────────────────────────────────────────────────────────────

@app.route("/")
@app.route("/<path:path>")
def serve_frontend(path=""):
    full_path = os.path.join(FRONTEND, path)
    if path and os.path.isfile(full_path):
        return send_from_directory(FRONTEND, path)
    return send_from_directory(FRONTEND, "index.html")


# ─── OCR 识别接口 ──────────────────────────────────────────────────────────────

@app.route("/ocr", methods=["POST"])
def ocr_recognize():
    if "file" not in request.files:
        return jsonify({"code": -1, "message": "请上传图片文件，字段名为 'file'"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"code": -1, "message": "文件名为空"}), 400

    suffix   = os.path.splitext(file.filename)[1] or ".png"
    tmp_path = os.path.join(TMP_DIR, f"{uuid.uuid4().hex}{suffix}")
    file.save(tmp_path)

    processed_path  = None
    processed_path2 = None

    try:
        # ── 串行锁：同一时刻只允许一个请求进入 OCR ──
        with _ocr_lock:
            # ── 第一次识别（含中值滤波） ──
            processed_path = apply_preprocessing(tmp_path, use_denoise=True)
            results, elapsed_ms = run_ocr(processed_path)
            text_lines, rec_scores, blocks = _parse_ocr_results(results)
            avg_conf = _calc_avg_confidence(rec_scores)

            # ── 细笔画补偿：置信度 < 0.9 时跳过去噪重试 ──
            if avg_conf < 0.9:
                processed_path2 = apply_preprocessing(tmp_path, use_denoise=False)
                results2, elapsed_ms2 = run_ocr(processed_path2)
                text_lines2, rec_scores2, blocks2 = _parse_ocr_results(results2)
                avg_conf2 = _calc_avg_confidence(rec_scores2)

                if avg_conf2 > avg_conf:
                    text_lines, rec_scores, blocks = text_lines2, rec_scores2, blocks2
                    avg_conf  = avg_conf2
                    elapsed_ms = elapsed_ms2

        full_text = "\n".join(text_lines)

        # ── 保存历史记录 ──
        save_history(tmp_path, full_text, avg_conf, rec_scores)

        return jsonify({
            "code": 0,
            "data": {
                "text":       full_text,
                "blocks":     blocks,
                "elapsed_ms": elapsed_ms,
                "confidence": round(avg_conf, 4),
            }
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"code": -1, "message": f"识别失败：{str(e)}"}), 500

    finally:
        for p in filter(None, [tmp_path, processed_path, processed_path2]):
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass
        # 清理 cache 目录中的临时文件
        for item in os.listdir(CACHE_DIR):
            item_path = os.path.join(CACHE_DIR, item)
            if os.path.isfile(item_path):
                try:
                    os.remove(item_path)
                except Exception:
                    pass


# ─── 历史记录接口 ──────────────────────────────────────────────────────────────

@app.route("/history", methods=["GET"])
def history_list():
    """
    GET /history
    可选参数：
      date=YYYYMMDD 或 YYYY-MM-DD  按日期过滤
      keyword=xxx                  在日期结果中再按关键词过滤
      page=1&size=20               分页
    """
    try:
        manager   = get_manager()
        date_str  = request.args.get("date", "").strip()
        keyword   = request.args.get("keyword", "").strip()
        page      = max(1, int(request.args.get("page",  1)))
        size      = max(1, int(request.args.get("size", 20)))

        if date_str:
            records = manager.search_by_date(date_str)
            if keyword:
                records = [r for r in records if keyword.lower() in r.get("text", "").lower()]
        elif keyword:
            all_records = manager.get_all_records()
            records = [r for r in all_records if keyword.lower() in r.get("text", "").lower()]
        else:
            records = manager.get_all_records()

        # 倒序（最新在前）
        records = list(reversed(records))
        total   = len(records)
        start   = (page - 1) * size
        paged   = records[start: start + size]

        return jsonify({
            "code": 0,
            "data": {
                "total":   total,
                "page":    page,
                "size":    size,
                "records": paged,
            }
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"code": -1, "message": str(e)}), 500


@app.route("/history/<record_dir>/image", methods=["GET"])
def history_image(record_dir):
    """返回历史记录中的原始图片"""
    dir_path = os.path.join(HISTORY_DIR, record_dir)
    if not os.path.isdir(dir_path):
        return jsonify({"code": -1, "message": "记录不存在"}), 404
    for f in os.listdir(dir_path):
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            return send_from_directory(dir_path, f)
    return jsonify({"code": -1, "message": "图片不存在"}), 404


@app.route("/history/<record_dir>/text", methods=["GET"])
def history_text(record_dir):
    """返回历史记录的识别文本"""
    dir_path = os.path.join(HISTORY_DIR, record_dir)
    if not os.path.isdir(dir_path):
        return jsonify({"code": -1, "message": "记录不存在"}), 404
    for f in os.listdir(dir_path):
        if f.endswith(".txt"):
            with open(os.path.join(dir_path, f), "r", encoding="utf-8") as fp:
                content = fp.read()
            return jsonify({"code": 0, "data": {"content": content}})
    return jsonify({"code": -1, "message": "文本文件不存在"}), 404


# ─── 健康检查 ──────────────────────────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "OCR 服务运行中"})


# ─── 启动 ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
