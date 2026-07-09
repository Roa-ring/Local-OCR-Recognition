from output import extract_text_from_result
import indexmake
import os
import json_cal

def history_manage(result,image_path):
    # ===== 1. 生成统一的基础名称 =====
    base_name = indexmake.get_next_base("history")

    # ===== 4. 实际存储路径 =====
    record_dir = os.path.join("history", base_name)
    os.makedirs(record_dir, exist_ok=True)

    # ===== 5. 保存 PaddleOCR 输出到 record_dir =====
    for res in result:
        res.print()
        res.save_to_img(record_dir)
        res.save_to_json(record_dir)

    # ===== 6. 保存识别文本（再次写入，确保内容） =====
    txt_path = os.path.join(record_dir, f"{base_name}.txt")
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(extract_text_from_result(result))

    # ===== 7. 计算置信度并写入 txt 首行 =====
    avg_conf = json_cal.calc_avg_confidence(record_dir)
    with open(txt_path, 'r', encoding='utf-8') as f:
        old = f.read()
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"置信度: {avg_conf:.4%}\n")
        f.write(old)
    if os.path.exists("cache/"+image_path+".png"):
        os.remove("cache/"+image_path+".png")