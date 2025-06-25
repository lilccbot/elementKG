import json

def get_immediate_children(node_name, json_file_path):
    """
    获取树结构中指定节点的直接子节点名称列表
    
    参数:
    node_name: str - 要查询的节点名称
    json_file_path: str - 树结构JSON文件路径
    
    返回:
    list - 直接子节点名称列表，如果节点不存在或没有子节点则返回空列表
    """
    try:
        # 加载JSON树结构
        with open(json_file_path, 'r', encoding='utf-8') as f:
            tree = json.load(f)
    except FileNotFoundError:
        print(f"错误: 文件 {json_file_path} 不存在")
        return []
    except json.JSONDecodeError:
        print(f"错误: 文件 {json_file_path} 格式不正确")
        return []
    
    # 构建节点名称索引
    index = {}
    
    def build_index(node, parent_path=None):
        """递归构建节点名称索引"""
        current_path = parent_path + [node['name']] if parent_path else [node['name']]
        path_str = "→".join(current_path)
        
        # 添加到索引
        if node['name'] not in index:
            index[node['name']] = []
        index[node['name']].append({
            "node": node,
            "path": path_str
        })
        
        # 递归处理子节点
        if 'children' in node:
            for child in node['children']:
                build_index(child, current_path)
    
    # 构建整个树的索引
    build_index(tree)
    
    # 查找指定节点
    if node_name not in index:
        return []  # 节点不存在
    
    # 收集所有直接子节点
    all_children = []
    for node_info in index[node_name]:
        if 'children' in node_info['node']:
            for child in node_info['node']['children']:
                all_children.append(child['name'])
    
    # 去重但保持顺序
    seen = set()
    unique_children = [child for child in all_children if not (child in seen or seen.add(child))]
    
    return unique_children

# 使用示例
if __name__ == "__main__":
    # JSON文件路径
    json_file = "/home/userdata/rmy/elementKG/data/reaction_tree.json"
    
    # 查询循环
    while True:
        print("\n" + "="*50)
        print("反应树查询系统")
        print("="*50)
        node_name = input("请输入节点名称 (输入 'exit' 退出): ").strip()
        
        if node_name.lower() == 'exit':
            print("退出查询系统")
            break
            
        if not node_name:
            print("请输入有效的节点名称")
            continue
            
        # 查询直接子节点
        children = get_immediate_children(node_name, json_file)
        
        # 显示结果
        print(f"\n节点 '{node_name}' 的直接子节点:")
        if children:
            print(f"({','.join(children)})")
        else:
            print("(无直接子节点)")