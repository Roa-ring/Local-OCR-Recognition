"""
日期解析工具模块
只处理标准化的纯数字日期，支持单个（4/6/8位）或范围（含~）
所有格式预处理（中文、分隔符、补零）由 date_parser 完成
"""
import re

def parse_date_token(token):
    """
    解析单个纯数字日期片段，返回 (from_date, to_date) 或 None
    支持：
        - 8位：精确日期（YYYYMMDD）
        - 6位：月份（YYYYMM），自动扩展为当月首日至末日
        - 4位：年份（YYYY），自动扩展为当年首日至末日
    年份必须在 2000~2100 之间，否则返回 None
    """
    token = token.strip()
    
    # 精确日期：20260709 (8位)
    if token.isdigit() and len(token) == 8:
        year = int(token[:4])
        if 2000 <= year <= 2100:
            d = int(token)
            return d, d
    
    # 月份：202607 (6位)
    if token.isdigit() and len(token) == 6:
        year = int(token[:4])
        if 2000 <= year <= 2100:
            month = int(token[4:6])
            from_date = int(token + "01")
            # 计算该月最后一天
            if month == 2:
                days = 29 if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0) else 28
            elif month in (4, 6, 9, 11):
                days = 30
            else:
                days = 31
            to_date = int(token + str(days).zfill(2))
            return from_date, to_date
    
    # 年份：2026 (4位)
    if token.isdigit() and len(token) == 4:
        year = int(token)
        if 2000 <= year <= 2100:
            from_date = int(token + "0101")
            to_date = int(token + "1231")
            return from_date, to_date
    
    return None


def parse_date_range(date_str):
    """
    解析标准化的日期字符串，返回 (from_date, to_date) 或 (None, None)
    输入格式要求：
        - 单个日期：如 "20260709"、"202607"、"2026"
        - 日期范围：如 "20260701~20260710"、"202607~202608"（左右均为完整纯数字）
    注意：此函数不处理分隔符、中文或补零，这些预处理由 date_parser 完成。
    """
    if not date_str:
        return None, None
    
    date_str = date_str.strip()
    
    if '~' in date_str:
        left, right = date_str.split('~', 1)
        left = left.strip()
        right = right.strip()
        f = parse_date_token(left)
        r = parse_date_token(right)
        if f and r:
            return f[0], r[1]   # 左侧起始，右侧结束
        elif f:
            return f[0], f[1]
        elif r:
            return r[0], r[1]
        else:
            return None, None
    else:
        token = parse_date_token(date_str)
        if token:
            return token[0], token[1]
        return None, None