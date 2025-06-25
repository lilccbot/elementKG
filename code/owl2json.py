from rdflib import Graph, URIRef, RDF, RDFS, OWL
import json

def extract_functional_group_tree(owl_file_path, output_file_path):
    # 创建 RDF 图
    g = Graph()
    g.parse(owl_file_path, format="xml")  # 支持 RDF/XML、Turtle 等格式

    # 定义常用命名空间
    rdfs = RDFS
    owl = OWL

    # 获取所有类
    classes = [uri for uri in g.subjects(RDF.type, OWL.Class)]

    # 构建父类 → 子类映射
    parent_child_map = {}
    for s, p, o in g:
        if p == RDFS.subClassOf and s in classes and o in classes:
            if o not in parent_child_map:
                parent_child_map[o] = []
            parent_child_map[o].append(s)

    # 获取类的本地名称（如 http://example.org/functionalGroup → functionalGroup）
    def get_local_name(uri):
        return uri.split("#")[-1].split("/")[-1]

    # 找到所有名为 'functionalGroup' 的类
    functional_groups = [cls for cls in classes if get_local_name(cls) == "functionalGroup"]

    # 递归构建树
    def build_tree(class_uri):
        class_name = get_local_name(class_uri)
        children = []
        if class_uri in parent_child_map:
            for child_uri in parent_child_map[class_uri]:
                children.append(build_tree(child_uri))
        return {"name": class_name, "children": children}

    # 构建所有以 functionalGroup 为根的子树
    trees = [build_tree(cls) for cls in functional_groups]

    # 保存为 JSON（直接以 functionalGroup 为根节点）
    with open(output_file_path, "w", encoding="utf-8") as f:
        if trees:
            json.dump(trees[0], f, ensure_ascii=False, indent=4)  # 取第一个 functionalGroup 的子树作为根
        else:
            json.dump({"name": "functionalGroup", "children": []}, f, ensure_ascii=False, indent=4)

    print(f"类层次结构已保存到 {output_file_path}")
    
if __name__ == "__main__":
    # 示例调用
    owl_file = "/home/userdata/rmy/elementKG/data/elementkg.owl"
    output_path = "/home/userdata/rmy/elementKG/schema/functiongroup_tree.json"
    extract_functional_group_tree(owl_file, output_path)