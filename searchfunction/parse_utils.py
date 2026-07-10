# parse_utils.py
import re
import calendar

def parse_and_complete_date_range(date_str):
    if '~' not in date_str:
        raise ValueError("日期范围必须包含 '~' 分隔符")
    left, right = date_str.split('~', 1)
    left = left.strip()
    right = right.strip()
    if not left or not right:
        raise ValueError("左右两侧不能为空")

    left_digits = re.sub(r'\D', '', left)
    right_digits = re.sub(r'\D', '', right)
    if not left_digits or not right_digits:
        raise ValueError("提取数字为空")

    if len(left_digits) < 4:
        raise ValueError("左侧日期必须包含年份")

    left_year_prefix = left_digits[:4]   # 用于右侧补年份

    def complete_side(digits, is_left, year_prefix=None):
        # 若数字串长度不足4，用 year_prefix 补齐（仅右侧可能发生）
        if len(digits) < 4:
            if year_prefix is None:
                raise ValueError("缺少年份前缀")
            # 将右侧简写视为月份（如 "07"），补齐为 "YYYYMM"
            if len(digits) <= 2:
                digits = year_prefix + digits.zfill(2)
            else:
                digits = year_prefix + digits   # 其他长度直接拼接

        if len(digits) == 4:
            year = int(digits)
            if is_left:
                return f"{year:04d}0101"
            else:
                return f"{year:04d}1231"
        elif len(digits) == 6:
            year = int(digits[:4])
            month = int(digits[4:6])
            if month < 1 or month > 12:
                raise ValueError("无效月份")
            if is_left:
                return f"{year:04d}{month:02d}01"
            else:
                last_day = calendar.monthrange(year, month)[1]
                return f"{year:04d}{month:02d}{last_day:02d}"
        elif len(digits) == 8:
            # 验证合法性
            year = int(digits[:4])
            month = int(digits[4:6])
            day = int(digits[6:8])
            import datetime
            try:
                datetime.datetime(year, month, day)
            except ValueError as e:
                raise ValueError(f"非法日期: {digits}") from e
            return digits
        else:
            raise ValueError(f"不支持的日期数字长度: {len(digits)}")

    left_complete = complete_side(left_digits, is_left=True)
    right_complete = complete_side(right_digits, is_left=False, year_prefix=left_year_prefix)

    if left_complete > right_complete:
        raise ValueError("起始日期大于结束日期")

    return [left_complete, right_complete]