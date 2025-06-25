import fitz  # PyMuPDF
import os

def pdf_to_images(pdf_path, output_folder, dpi=200, fmt="png"):
    """
    将 PDF 文件按页转换为图片
    :param pdf_path: PDF 文件路径
    :param output_folder: 输出图片的文件夹路径
    :param dpi: 图片分辨率（默认 200 DPI）
    :param fmt: 输出格式（默认 png）
    """
    # 创建输出目录
    os.makedirs(output_folder, exist_ok=True)

    # 打开 PDF 文档
    doc = fitz.open(pdf_path)
    print(f"PDF 共 {len(doc)} 页")

    for page_num in range(len(doc)):
        # 获取页面对象
        page = doc.load_page(page_num)
        # 设置渲染参数
        mat = fitz.Matrix(dpi / 72, dpi / 72)  # 72 DPI 是 PDF 的默认分辨率
        # 渲染页面为 pixmap（像素图）
        pix = page.get_pixmap(matrix=mat)
        # 构造输出路径
        output_path = os.path.join(output_folder, f"page_{page_num + 1}.{fmt}")
        # 保存为图片
        pix.save(output_path)
        print(f"已保存第 {page_num + 1} 页到 {output_path}")

    doc.close()
    print("转换完成！")
