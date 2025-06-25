import json
import os
import re

class TreeNode:
    def __init__(self, name):
        self.name = name
        self.children = {}
    
    def add_child(self, path):
        if not path:
            return
        current = path[0]
        if current not in self.children:
            self.children[current] = TreeNode(current)
        if len(path) > 1:
            self.children[current].add_child(path[1:])
    
    def to_dict(self, include_children=True):
        result = {"name": self.name}
        if include_children and self.children:
            result["children"] = [child.to_dict() for child in self.children.values()]
        return result

# 定义需要保持完整的特殊节点列表
SPECIAL_NODES = [
    "烷基、烯基和炔基的取代反应 (亲电的和金属有机的反应) (Substitution Reactions at Aliphatic, Vinylic, and Acetylenic Carbon (Electrophilic and Organometallic))",
    "α,β-环氧酸的开环",
    "[1,j]-σ迁移",
    "碳[1,j]-σ迁移",
    "[2,3]-σ迁移重排",
    "氮-碳,氧-碳和硫-碳迁移",
    "1,1,1-三卤化物的水解",
    "杂原子α位的烷基化：1,3-二噻烷的烷基化",
    "二氢-1,3-噁嗪的烷基化：醛、酮和羧酸的Meyers合成",
    "金属有机化合物与活泼双键的1,4-加成",
    "1,3-偶极加成（加成氧、氮和碳）",
    "Tebbe,Petasis和交替的烯基化",
    "自由基与C=O,C=S,C≡N化合物的加成",
    "1,3-二醇的断链",
    "1,2-重排",
    "环丁烯和1,3-环己二烯的电环化重排",
    "醛和酮双分子还原成1,2-二醇"
]

def protect_special_nodes(line):
    """保护特殊节点不被分割"""
    protected_line = line
    for i, node in enumerate(SPECIAL_NODES):
        placeholder = f"__SPECIAL_NODE_{i}__"
        protected_line = protected_line.replace(node, placeholder)
    return protected_line

def restore_special_nodes(parts):
    """恢复特殊节点"""
    restored_parts = []
    for part in parts:
        for i, node in enumerate(SPECIAL_NODES):
            placeholder = f"__SPECIAL_NODE_{i}__"
            if placeholder in part:
                part = part.replace(placeholder, node)
        restored_parts.append(part)
    return restored_parts

def convert_to_english_symbols(text):
    """将所有符号转换为英文格式"""
    symbol_map = {
        "（": "(",
        "）": ")",
        "，": ",",
        "：": ":",
        "；": ";",
        "！": "!",
        "？": "?",
        "、": ","  # 中文顿号转换为英文逗号
    }
    for cn, en in symbol_map.items():
        text = text.replace(cn, en)
    return text

def parse_reaction_line(line):
    """解析反应路径行，特殊节点保持完整"""
    # 移除花括号和空白
    cleaned = line.strip().strip('{}').strip()
    
    # 保护特殊节点不被分割
    protected_line = protect_special_nodes(cleaned)
    
    # 分割其他节点
    parts = protected_line.split(',')
    
    # 恢复特殊节点
    parts = restore_special_nodes(parts)
    
    # 清理每个部分并转换符号
    cleaned_parts = []
    for part in parts:
        part = part.strip()
        if part:
            # 转换符号为英文格式
            part = convert_to_english_symbols(part)
            cleaned_parts.append(part)
    
    return cleaned_parts

def build_reaction_tree(file_path):
    """构建反应树结构"""
    root = TreeNode("Reactions")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            parts = parse_reaction_line(line)
            if parts:
                root.add_child(parts)
    
    return root

def save_tree_to_json(tree, output_path):
    """保存树结构为JSON文件"""
    tree_dict = {
        "name": "Reactions",
        "children": [child.to_dict() for child in tree.children.values()]
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(tree_dict, f, ensure_ascii=False, indent=2)

def main():
    input_file = "/home/userdata/rmy/elementKG/schema/reaction_tree.txt"
    output_dir = "/home/userdata/rmy/elementKG/schema"
    output_file = os.path.join(output_dir, "reaction_tree.json")
    
    reaction_tree = build_reaction_tree(input_file)
    save_tree_to_json(reaction_tree, output_file)
    print(f"Tree structure successfully saved to: {output_file}")

if __name__ == "__main__":
    main()