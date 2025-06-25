import os
import json
from triplet_generate import extract_and_save_triplets
from image2text import image_to_latex_text
from pdf2image import pdf_to_images

def process_pdf_pipeline(
    pdf_path: str,
    schema_file_path: str,
    image_output_folder: str = "images",
    text_output_folder: str = "texts",
    triplet_output_folder: str = "triplets",
    dpi: int = 300,
    fmt: str = "png"
):
    """
    完整处理流程：PDF → 图片 → 文本 → 三元组提取（每页独立处理）
    
    Args:
        pdf_path (str): 输入 PDF 文件路径
        schema_file_path (str): Schema 文件路径
        image_output_folder (str): 保存图片的文件夹路径
        text_output_folder (str): 保存文本的文件夹路径
        triplet_output_folder (str): 保存三元组的文件夹路径
        dpi (int): 图片分辨率
        fmt (str): 图片格式（默认 png）
    
    Returns:
        list: 各页的三元组提取结果列表
    """
    try:
        # Step 1: 创建输出目录（如果不存在）
        os.makedirs(image_output_folder, exist_ok=True)
        os.makedirs(text_output_folder, exist_ok=True)
        os.makedirs(triplet_output_folder, exist_ok=True)

        # Step 2: 读取 Schema
        print("🔄 步骤1：加载 Schema 文件")
        with open(schema_file_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        # Step 3: PDF 转图片
        print(f"🔄 步骤2：将 PDF 转换为图片（保存到 {image_output_folder}）")
        pdf_to_images(pdf_path, image_output_folder, dpi=dpi, fmt=fmt)
        image_files = [f for f in os.listdir(image_output_folder) if f.endswith((".png", ".jpg"))]
        print(f"✅ 已生成 {len(image_files)} 张图片")

        # Step 4: 图片转文本 & 三元组提取（每页独立处理）
        print("🔄 步骤3：逐页处理图片 → 文本 → 三元组")
        results = []
        for img_file in sorted(image_files):  # 按页码排序
            # 构造路径
            image_path = os.path.join(image_output_folder, img_file)
            text_file = os.path.splitext(img_file)[0] + ".txt"
            text_path = os.path.join(text_output_folder, text_file)
            triplet_file = os.path.splitext(img_file)[0] + "_triplets.json"
            triplet_path = os.path.join(triplet_output_folder, triplet_file)

            # 图片转文本
            print(f"  🔹 处理图片 {img_file}")
            success = image_to_latex_text(
                image_path=image_path,
                output_path=text_path
            )
            if not success:
                print(f"⚠️ 跳过图片 {img_file}：文本转换失败")
                continue

            # 读取文本
            with open(text_path, "r", encoding="utf-8") as f:
                page_text = f.read()

            # 提取三元组
            page_result = extract_and_save_triplets("qwen-plus-latest", schema, page_text)
            if page_result:
                # 保存三元组结果
                with open(triplet_path, "w", encoding="utf-8") as f:
                    json.dump(page_result, f, ensure_ascii=False, indent=2)
                print(f"  ✅ 已保存三元组到 {triplet_path}")
                results.append(page_result)
            else:
                print(f"⚠️ 页面 {img_file} 三元组提取失败")

        print("✅ 三元组提取完成")
        return results

    except Exception as e:
        print(f"❌ Pipeline 处理失败: {str(e)}")
        return None

if __name__ == "__main__":
    # 输入路径
    pdf_path = "/home/userdata/rmy/elementKG/data/pdfs/en_March高等有机化学_100-101.pdf"
    schema_file_path = "/home/userdata/rmy/elementKG/schema/Basic_schema.json"
    
    # 输出路径
    image_output_folder = "/home/userdata/rmy/elementKG/data/images"
    text_output_folder = "/home/userdata/rmy/elementKG/data/text"
    triplet_output_folder = "/home/userdata/rmy/elementKG/data/triplets"

    # 启动 pipeline
    results = process_pdf_pipeline(
        pdf_path=pdf_path,
        schema_file_path=schema_file_path,
        image_output_folder=image_output_folder,
        text_output_folder=text_output_folder,
        triplet_output_folder=triplet_output_folder,
        dpi=300,
        fmt="png"
    )

    if results:
        print(f"✅ 共提取到 {len(results)} 页三元组")
    else:
        print("Pipeline 处理失败，请检查日志。")