"""
输出与历史记录管理模块
- 使用二叉搜索树(BS)按日期(YYYYMMDD)索引历史记录
- 每次识别生成日期_索引.txt文件,并存入BST
- 支持按日期查询和关键词搜索(基于txt文件内容)
"""
import os
import shutil
import json
import indexmake


# ==================== BST 数据结构 ====================
class BSTNode:
    """BST节点,key为日期整数,value为该日所有记录的列表"""
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

    def search_by_date(self, key):
        node = self._search(self.root, key)
        return node.records if node else None

    def _search(self, node, key):
        if node is None or node.key == key:
            return node
        if key < node.key:
            return self._search(node.left, key)
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
        # 优先从索引文件加载，如果失败则扫描txt
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
        except:
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
                # 跳过索引文件
                if filename == "index.json":
                    continue
                # 解析文件名：日期_编号.txt
                base = filename[:-4]
                parts = base.split('_')
                if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
                    continue
                date_key = int(parts[0])
                index = int(parts[1])
                filepath = os.path.join(root, filename)
                # 提取子文件夹名（相对于storage_dir）
                rel_dir = os.path.relpath(root, self.storage_dir)
                if rel_dir == ".":
                    record_dir = base  # 兼容旧数据（文件直接在history/下）
                else:
                    record_dir = rel_dir
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    # 如果首行是置信度，提取并移除
                    lines = content.split('\n', 1)
                    text = lines[1] if len(lines) > 1 else content
                except:
                    continue
                record = {
                    'date': date_key,
                    'index': index,
                    'record_dir': record_dir,
                    'txt_file': filename,
                    'text': text,
                    'image_path': None,
                    'file_size': None
                }
                self.bst.insert(date_key, record)

    def add_record(self, image_path, text, file_size):
        """添加新记录：生成编号、保存txt和图片、插入BST、更新索引"""
        # 使用 indexmake 生成基础前缀
        base = indexmake.get_next_base(self.storage_dir)
        date_key = int(base.split('_')[0])
        index = int(base.split('_')[1])
        
        # 子文件夹名就是 base（如 "20260708_1"）
        record_dir = base
        # 创建子文件夹
        dir_path = os.path.join(self.storage_dir, record_dir)
        os.makedirs(dir_path, exist_ok=True)
        
        # 生成文件名
        txt_file = f"{base}.txt"
        img_file = f"{base}.jpg"
        
        # 保存txt文件到子文件夹
        txt_path = os.path.join(dir_path, txt_file)
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        # 复制原始图片到子文件夹
        img_path = os.path.join(dir_path, img_file)
        shutil.copy2(image_path, img_path)
        
        # 构造记录（包含 record_dir）
        record = {
            'date': date_key,
            'index': index,
            'record_dir': record_dir,
            'txt_file': txt_file,
            'img_file': img_file,
            'text': text,
            'image_path': image_path,
            'file_size': file_size
        }
        
        # 插入BST并保存索引
        self.bst.insert(date_key, record)
        self.save_index()
        return record

    def search_by_date(self, date_str):
        """按日期查询，支持 '2026-07-07' 或 '20260707'"""
        date_str = date_str.replace('-', '')
        if not date_str.isdigit():
            return []
        key = int(date_str)
        records = self.bst.search_by_date(key)
        return records if records else []

    def search_keyword_in_date(self, date_str, keyword):
        """在指定日期的记录中搜索关键词（不区分大小写）"""
        records = self.search_by_date(date_str)
        if not records:
            return []
        matched = []
        for rec in records:
            if keyword.lower() in rec['text'].lower():
                matched.append(rec)
        return matched

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
