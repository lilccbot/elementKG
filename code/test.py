from pdf2image import pdf_to_images


# 示例用法
if __name__ == "__main__":
    pdf_path = "/home/userdata/rmy/elementKG/data/pdfs/en_March高等有机化学_100-101.pdf"
    output_folder = "/home/userdata/rmy/elementKG/data/images"
    pdf_to_images(pdf_path, output_folder, dpi=300, fmt="png")