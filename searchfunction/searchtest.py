from searchnew import search_by_fields, print_results

test_cases = [
    ("20260710", "\n"),
    
]

for date_str, keyword_str in test_cases:
    print(f"\n=== 搜索: 日期='{date_str}', 关键词='{keyword_str}' ===")
    results = search_by_fields(date_str, keyword_str)
    print_results(results)