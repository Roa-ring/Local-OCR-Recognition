"""
输出与历史记录管理模块
- 使用二叉搜索树（BST）按日期（YYYYMMDD）索引历史记录
- 每次识别生成日期_索引.txt文件，并存入BST
- 支持按日期查询和关键词搜索（基于txt文件内容）
"""
import os
import shutil
import json
import time
import indexmake


# ==================== BST 数据结构 ====================

class BSTNode:
    """BST节点，key为日期整数，value为该日所有记录的列表"""
    def __init__(self, key, record):
        self.key = key
        self.records = [record]
        self.left = None
        self.right = None


class HistoryBST:
    def __init__(self):
        self.root = None

    def insert(self, key, record):
        if self.root is None:
            self.root = BSTNode(key, record)
        else:
            self._insert(self.root, key, record)

    def _insert(self, node, key, record):
        if key == node.key:
            node.records.append(record)
        elif key < node.key:
            if node.left is None:
                node.left = BSTNode(key, record)
            else:
                self._insert(node.left, key, record)
        else:
            if node.right is None:
                node.right = BSTNode(key, record)
            else:
                self._insert(node.right, key, record)

    def search_by_date(self, key: int):
        """按日期整数精确查找，返回该日所有记录列表，未找到返回 []"""
        return self._search(self.root, key)

    def _search(self, node, key: int):
        if node is None:
            return []
        if key == node.key:
            return node.records
        elif key < node.key:
            return self._search(node.left, key)
        else:
            return self._search(node.right, key)

    def inorder(self):
        """返回所有记录（按日期升序）"""
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if node:
            self._inorder(node.left, result)
            result.extend(node.records)
            self._inorder(node.right, result)


# ==================== 历史记录管理器 ====================

class HistoryManager:
    def __init__(self, storage_dir="history"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        self.index_file = os.path.join(storage_dir, "index.json")
        self.bst = HistoryBST()
        if not self._load_from_index():
            self._load_existing_records()

    def _load_from_index(self):
        """从索引文件加载记录到BST，返回是否成功"""
        if not os.path.exists(self.index_file):
            return False
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                records = json.load(f)
            for rec in records:
                self.bst.insert(rec['date'], rec)
            return True
        except Exception:
            return False

    def save_index(self):
        """将BST所有记录保存到索引文件"""
        all_records = self.bst.inorder()
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(all_records, f, ensure_ascii=False, indent=4)

    def _load_existing_records(self):
        """扫描存储目录，根据已有文件重建BST（兼容旧数据）"""
        for root, dirs, files in os.walk(self.storage_dir):
            for filename in files:
                if not filename.endswith(".txt"):
                    continue
                if filename == "index.json":
                    continue
                base = filename[:-4]
                parts = base.split('_')
                if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
                    continue
                date_key = int(parts[0])
                index = int(parts[1])
                filepath = os.path.join(root, filename)
                rel_dir = os.path.relpath(root, self.storage_dir)
                record_dir = base if rel_dir == "." else rel_dir
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    lines = content.split('\n', 1)
                    text = lines[1] if len(lines) > 1 else content
                except Exception:
                    continue
                record = {
                    'date': date_key,
                    'index': index,
                    'record_dir': record_dir,
                    'txt_file': filename,
                    'text': text,
                    'image_path': None,
                    'file_size': None,
                }
                self.bst.insert(date_key, record)

    def add_record(self, image_path, text, file_size):
        """添加新记录：生成编号、保存txt和图片、插入BST、更新索引"""
        base = indexmake.get_next_base(self.storage_dir)
        date_key = int(base.split('_')[0])
        index = int(base.split('_')[1])

        record_dir = base
        dir_path = os.path.join(self.storage_dir, record_dir)
        os.makedirs(dir_path, exist_ok=True)

        txt_file = f"{base}.txt"
        img_file = f"{base}.jpg"

        txt_path = os.path.join(dir_path, txt_file)
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)

        img_path = os.path.join(dir_path, img_file)
        shutil.copy2(image_path, img_path)

        record = {
            'date': date_key,
            'index': index,
            'record_dir': record_dir,
            'txt_file': txt_file,
            'img_file': img_file,
            'text': text,
            'image_path': image_path,
            'file_size': file_size,
        }
        self.bst.insert(date_key, record)
        self.save_index()
        return record

    def search_by_date(self, date_str):
        """按日期查询，支持 '2026-07-07' 或 '20260707'"""
        date_str = date_str.replace('-', '')
        if not date_str.isdigit():
            return []
        key = int(date_str)
        return self.bst.search_by_date(key)

    def search_keyword_in_date(self, date_str, keyword):
        """在指定日期的记录中搜索关键词（不区分大小写）"""
        records = self.search_by_date(date_str)
        return [r for r in records if keyword.lower() in r.get('text', '').lower()]

    def get_all_records(self):
        """获取所有记录（按日期升序）"""
        return self.bst.inorder()


# ==================== 对外接口（供主程序调用） ====================

_manager = None


def get_manager():
    global _manager
    if _manager is None:
        _manager = HistoryManager(storage_dir="history")
    return _manager


def extract_text_from_result(result):
    """从PaddleOCR返回结果中提取完整文本"""
    texts = []
    for res in result:
        if isinstance(res, dict) and 'rec_texts' in res:
            texts.extend(res['rec_texts'])
        elif hasattr(res, 'rec_texts'):
            texts.extend(res.rec_texts)
        else:
            for item in res:
                if isinstance(item, list) and len(item) >= 2:
                    texts.append(item[1][0] if isinstance(item[1], list) else str(item[1]))
    return '\n'.join(texts)


def save_and_record_result(result, image_path):
    """供主程序调用的主要函数"""
    manager = get_manager()
    text = extract_text_from_result(result)
    file_size = os.path.getsize(image_path)
    record = manager.add_record(image_path, text, file_size)
    print(f"[历史记录] 已保存：{record['txt_file']} (图片：{record['img_file']})")
    return record


def query_by_date(date_str):
    """按日期查询，返回记录列表"""
    return get_manager().search_by_date(date_str)


def query_keyword(date_str, keyword):
    """按日期和关键词查询"""
    return get_manager().search_keyword_in_date(date_str, keyword)


def export_report(filename="history_report.txt"):
    """导出所有记录为人类可读的文本报告"""
    records = get_manager().get_all_records()
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("历史记录报告\n")
        f.write("=" * 50 + "\n")
        for rec in records:
            f.write(f"日期: {rec['date']}\n")
            f.write(f"文件夹: {rec['record_dir']}\n")
            f.write(f"文本文件: {rec['txt_file']}\n")
            f.write(f"图片文件: {rec.get('img_file', 'N/A')}\n")
            f.write(f"内容: {rec['text'][:100]}{'...' if len(rec['text']) > 100 else ''}\n")
            f.write("-" * 30 + "\n")
    print(f"[报告] 已导出到 {filename}")
