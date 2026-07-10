# searchnew.py（关键修改部分）
import re
from base import get_manager
from datefill import parse_date_token
from date_parser import normalize_date
from parse_utils import parse_and_complete_date_range

def search_by_fields(date_str=None, keyword_str=None):
    from_date, to_date = None, None

    if date_str:
        date_str = date_str.strip()
        if '~' in date_str:
            try:
                left_comp, right_comp = parse_and_complete_date_range(date_str)
                from_date = int(left_comp)
                to_date = int(right_comp)
            except ValueError as e:
                raise ValueError(f"日期范围解析失败: {e}")
        else:
            # 单个日期：提取数字串（不补缺省）
            clean = normalize_date(date_str)
            if clean and clean.isdigit():
                token_result = parse_date_token(clean)
                if token_result:
                    from_date, to_date = token_result

    manager = get_manager()
    all_records = manager.get_all_records()

    # 日期过滤
    if from_date is not None and to_date is not None:
        filtered = [rec for rec in all_records if rec.get('date') is not None and from_date <= rec['date'] <= to_date]
    elif from_date is not None:
        filtered = [rec for rec in all_records if rec.get('date') is not None and rec['date'] >= from_date]
    elif to_date is not None:
        filtered = [rec for rec in all_records if rec.get('date') is not None and rec['date'] <= to_date]
    else:
        filtered = all_records

    # 关键词过滤（单字符全部出现）
    if keyword_str:
        chars = [ch for ch in keyword_str if not ch.isspace()]
        if chars:
            chars_lower = [ch.lower() for ch in chars]
            filtered = [rec for rec in filtered 
                        if all(ch in rec.get('text', '').lower() for ch in chars_lower)]

    filtered.sort(key=lambda x: (x.get('date', 0), x.get('index', 0)), reverse=True)
    return filtered


def export_to_txt(records, filename="search_result.txt"):
    """导出搜索结果到文本文件（只写路径）"""
    with open(filename, 'w', encoding='utf-8') as f:
        if not records:
            f.write("未找到匹配记录")
            return
        f.write(f"搜索结果（共 {len(records)} 条）\n")
        f.write("=" * 70 + "\n")
        for rec in records:
            f.write(f"日期: {rec.get('date', '')}  #{rec.get('index', '')}\n")
            f.write(f"目录: history/{rec.get('record_dir', '')}/\n")
            f.write("-" * 70 + "\n")
    print(f"结果已导出到 {filename}")


def print_results(records, max_chars=80):
    """打印搜索结果（只显示路径）"""
    if not records:
        print("未找到匹配记录")
        return
    print(f"找到 {len(records)} 条记录：")
    print("-" * 70)
    for rec in records:
        date_str = str(rec.get('date', ''))
        index = rec.get('index', '')
        record_dir = rec.get('record_dir', '')
        print(f"[{date_str} #{index}] 路径: history/{record_dir}/")
    print("-" * 70)


