""""""
"""
搜索模块
单一输入框，自动识别日期、关键词、混合查询
支持多种日期格式：纯数字,分隔符,空格,中文
"""
import re
from output import get_manager


# ==================== 日期解析工具 ====================

def parse_date_token(token):
    """
    解析单个日期片段，返回 (from_date, to_date) 或 None
    支持:YYYYMMDD, YYYYMM, YYYY, YYYYMMDD-YYYYMMDD
    年份必须在 2000~2100 之间，否则不视为日期
    """
    token = token.strip()
    
    # 1. 范围格式：20260701-20260710
    if '-' in token:
        parts = token.split('-')
        if len(parts) == 2 and all(p.isdigit() for p in parts):
            from_date, to_date = parts
            if len(from_date) == 8 and len(to_date) == 8:
                year = int(from_date[:4])
                if 2000 <= year <= 2100:
                    return int(from_date), int(to_date)
    
    # 2. 精确日期：20260709 (8位)
    if token.isdigit() and len(token) == 8:
        year = int(token[:4])
        if 2000 <= year <= 2100:
            d = int(token)
            return d, d
    
    # 3. 月份：202607 (6位)
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
    
    # 4. 年份：2026 (4位)
    if token.isdigit() and len(token) == 4:
        year = int(token)
        if 2000 <= year <= 2100:
            from_date = int(token + "0101")
            to_date = int(token + "1231")
            return from_date, to_date
    
    return None


def parse_search_input(user_input):
    """
    解析用户搜索输入，返回 (date_from, date_to, keyword)
    支持多种日期格式和混合输入
    """
    user_input = user_input.strip()
    if not user_input:
        return None, None, None
    
 # ========== 新增：专门处理中文日期 ==========
    # 1. 提取完整的 年-月-日 格式：2026年7月9日 或 2026年07月09日
    chinese_full = re.compile(r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日')
    match = chinese_full.search(user_input)
    if match:
        year = match.group(1)
        month = match.group(2).zfill(2)
        day = match.group(3).zfill(2)
        date_str = year + month + day
        remainder = chinese_full.sub('', user_input).strip()
        from_date, to_date = parse_date_token(date_str)
        if from_date is not None:
            keyword = remainder if remainder else None
            return from_date, to_date, keyword

    # 2. 提取 年-月 格式：2026年7月
    chinese_month = re.compile(r'(\d{4})\s*年\s*(\d{1,2})\s*月')
    match = chinese_month.search(user_input)
    if match:
        year = match.group(1)
        month = match.group(2).zfill(2)
        date_str = year + month
        remainder = chinese_month.sub('', user_input).strip()
        from_date, to_date = parse_date_token(date_str)
        if from_date is not None:
            keyword = remainder if remainder else None
            return from_date, to_date, keyword

    # 3. 提取 年 格式：2026年
    chinese_year = re.compile(r'(\d{4})\s*年')
    match = chinese_year.search(user_input)
    if match:
        year = match.group(1)
        date_str = year
        remainder = chinese_year.sub('', user_input).strip()
        from_date, to_date = parse_date_token(date_str)
        if from_date is not None:
            keyword = remainder if remainder else None
            return from_date, to_date, keyword


    # ===== 1. 预处理：将常见分隔符替换为空格 =====
    text = user_input
    # 将 / - . ，,、 等替换为空格
    text = re.sub(r'[/\-\.，,、]', ' ', text)
    # 将中文年月日替换为空格（保留数字）
    text = re.sub(r'[年月日]', ' ', text)
    # 多个空格合并为一个
    text = re.sub(r'\s+', ' ', text).strip()
    
    # ===== 2. 将分散的数字片段合并（如 "2026 07 09" -> "20260709"） =====
    tokens = text.split()
    merged_tokens = []
    temp_digits = []
    
    for token in tokens:
        # 如果是纯数字且长度不超过4，可能是日期的一部分
        if token.isdigit() and len(token) <= 4:
            temp_digits.append(token)
        else:
            # 遇到非数字，先合并之前的数字片段
            if temp_digits:
                merged_tokens.append(''.join(temp_digits))
                temp_digits = []
            merged_tokens.append(token)
    
    # 处理末尾的数字片段
    if temp_digits:
        merged_tokens.append(''.join(temp_digits))
    
    # ===== 3. 解析日期和关键词 =====
    date_parts = []
    keyword_parts = []
    
    for token in merged_tokens:
        date_range = parse_date_token(token)
        if date_range is not None:
            date_parts.append(date_range)
        else:
            # 如果 token 是纯数字但日期解析失败（如 9999），当作关键词
            keyword_parts.append(token)
    
    # 合并日期范围（取并集）
    if date_parts:
        from_date = min(d[0] for d in date_parts)
        to_date = max(d[1] for d in date_parts)
    else:
        from_date, to_date = None, None
    
    keyword = ' '.join(keyword_parts) if keyword_parts else None
    
    return from_date, to_date, keyword


# ==================== 搜索主函数 ====================

def search_records(user_input):
    """
    单一入口搜索
    - 输入: 用户输入的字符串
    - 返回: 匹配的记录列表，按日期降序排列
    """
    from_date, to_date, keyword = parse_search_input(user_input)
    
    manager = get_manager()
    all_records = manager.get_all_records()
    
    # 1. 日期过滤
    if from_date is not None:
        filtered = [rec for rec in all_records 
                    if rec.get('date') is not None and from_date <= rec['date'] <= to_date]
    else:
        filtered = all_records
    
    # 2. 关键词过滤
    if keyword:
        keyword_lower = keyword.lower()
        filtered = [rec for rec in filtered 
                    if keyword_lower in rec.get('text', '').lower()]
    
    # 3. 排序：按日期降序（近期优先），同日期按索引降序
    filtered.sort(key=lambda x: (x.get('date', 0), x.get('index', 0)), reverse=True)
    
    return filtered


def print_results(records, max_chars=80):
    """打印搜索结果"""
    if not records:
        print("未找到匹配记录")
        return
    
    print(f"找到 {len(records)} 条记录：")
    print("-" * 70)
    for rec in records:
        date_str = str(rec.get('date', ''))
        text = rec.get('text', '')
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        print(f"[{date_str} #{rec.get('index', '')}] {text}")
        print(f"  目录: {rec.get('record_dir', '')}")
        print("-" * 70)


def export_to_txt(records, filename="search_result.txt"):
    """导出搜索结果到文本文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        if not records:
            f.write("未找到匹配记录")
            return
        f.write(f"搜索结果（共 {len(records)} 条）\n")
        f.write("=" * 70 + "\n")
        for rec in records:
            f.write(f"日期: {rec.get('date', '')}  #{rec.get('index', '')}\n")
            f.write(f"文本: {rec.get('text', '')}\n")
            f.write(f"目录: {rec.get('record_dir', '')}\n")
            f.write("-" * 70 + "\n")
    print(f"结果已导出到 {filename}")
    """"""