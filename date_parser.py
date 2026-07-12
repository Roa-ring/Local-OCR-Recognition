# date_parser.py
import re

def normalize_date(text):
    """
    提取日期中的数字，不补缺省值。
    返回 4/6/8 位纯数字串：
        - 仅年份 → 'YYYY'
        - 年+月   → 'YYYYMM'
        - 年+月+日 → 'YYYYMMDD'
    若输入为纯数字，原样返回（需保证长度合法）。
    """
    text = text.strip()
    if not text:
        return ""
    if text.isdigit():
        return text

    # 替换分隔符为空格，中文也替换
    s = re.sub(r'[年/月/日\-\.,,、]', ' ', text)
    s = re.sub(r'\s+', ' ', s).strip()
    parts = s.split()
    if not parts:
        return ""

    year = parts[0].strip().zfill(4)
    result = year
    if len(parts) >= 2:
        month = parts[1].strip().zfill(2)
        result += month
        if len(parts) >= 3:
            day = parts[2].strip().zfill(2)
            result += day
    return result