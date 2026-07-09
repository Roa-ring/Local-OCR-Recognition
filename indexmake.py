import os
import time

def get_next_index(directory, prefix=None):
    """扫描目录，返回下一个可用编号"""
    os.makedirs(directory, exist_ok=True)
    if prefix is None:
        prefix = time.strftime("%Y%m%d")
    
    max_num = 0
    for filename in os.listdir(directory):
        if filename.startswith(prefix + "_"):
            parts = filename.split('_')
            if len(parts) >= 2:
                num_part = parts[1].split('.')[0]
                if num_part.isdigit():
                    max_num = max(max_num, int(num_part))
    return max_num + 1

def get_next_base(directory, prefix=None):
    """返回下一个可用的基础前缀（如 '20260708_1'）"""
    if prefix is None:
        prefix = time.strftime("%Y%m%d")
    idx = get_next_index(directory, prefix)
    return f"{prefix}_{idx}"