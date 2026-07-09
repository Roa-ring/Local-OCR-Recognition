import json
import os

def calc_avg_confidence(folder_path):
    """自动查找文件夹内包含 'res' 的 JSON 文件，计算平均置信度"""
    if not os.path.isdir(folder_path):
        print(f"错误: 文件夹不存在 - {folder_path}")
        return None

    # 查找所有包含 'res'（不区分大小写）且扩展名为 .json 的文件
    json_files = [f for f in os.listdir(folder_path) if 'res' in f.lower() and f.endswith('.json')]
    if not json_files:
        print(f"警告: 在 {folder_path} 中未找到包含 'res' 的 JSON 文件")
        return None

    # 取第一个文件
    json_path = os.path.join(folder_path, json_files[0])
    print(f"读取: {json_path}")

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"读取 JSON 失败: {e}")
        return None

    # 处理嵌套结构（PaddleOCR 可能将数据包在 'res' 键下）
    if 'res' in data and isinstance(data['res'], dict):
        data = data['res']

    scores = data.get('rec_scores', [])
    if not scores:
        print("警告: 未找到 rec_scores 字段")
        return None

    return sum(scores) / len(scores)