# ===== 测试查询功能 =====
from output import query_by_date, query_keyword

print("\n===== 测试按日期查询 =====")
records = query_by_date("20260709")
if records:
    print(f"找到 {len(records)} 条记录：")
    for r in records:
        print(f"  - {r['record_dir']}: {r['text'][:50]}...")
else:
    print("未找到记录")

print("\n===== 测试关键词查询 =====")
keyword = "毕业"
matched = query_keyword("20260709", keyword)
if matched:
    print(f"找到 {len(matched)} 条包含 '{keyword}' 的记录：")
    for r in matched:
        print(f"  - {r['record_dir']}: {r['text'][:50]}...")
else:
    print(f"未找到包含 '{keyword}' 的记录")