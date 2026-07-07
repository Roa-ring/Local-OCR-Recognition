import time
import os
import tempfile

from flask import Flask, request, jsonify
from flask_cors import CORS
from paddleocr import PaddleOCR

app = Flask(__name__)
CORS(app)

print("正在加载 OCR 模型，请稍候...")
ocr = PaddleOCR(
    text_detection_model_name="PP-OCRv6_medium_det",
    text_recognition_model_name="PP-OCRv6_medium_rec",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=True,
)
print("OCR 模型加载完成，服务已就绪！")


@app.route("/ocr", methods=["POST"])
def ocr_recognize():
    if "file" not in request.files:
        return jsonify({"code": -1, "message": "请上传图片文件"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"code": -1, "message": "文件名为空"}), 400

    suffix = os.path.splitext(file.filename)[1] or ".png"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    try:
        start_time = time.time()
        results = ocr.predict(tmp_path)
        elapsed_ms = int((time.time() - start_time) * 1000)

        all_text_lines = []
        blocks = []
        for res in results:
            data = res.json
            inner = data.get("res", data)  # 兼容新旧版本结构
            rec_texts = inner.get("rec_texts", [])
            rec_scores = inner.get("rec_scores", [])
            dt_polys = inner.get("dt_polys", [])

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

        return jsonify({
            "code": 0,
            "data": {
                "text": "\n".join(all_text_lines),
                "blocks": blocks,
                "elapsed_ms": elapsed_ms,
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"code": -1, "message": f"识别失败：{str(e)}"}), 500

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "OCR 服务运行中"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
