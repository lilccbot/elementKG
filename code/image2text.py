import os
import dashscope

def image_to_latex_text(
    image_path: str,
    output_path: str,
    model: str = "qwen-vl-ocr-latest",
    min_pixels: int = 28 * 28 * 4,
    max_pixels: int = 28 * 28 * 8192,
    enable_rotate: bool = True
) -> bool:
    """
    将图片中的文本转换为 LaTeX 格式并保存为纯文本文件
    
    Args:
        image_path (str): 输入图片的本地路径（支持 .png/.jpg 等格式）
        output_path (str): 输出文本文件的保存路径
        model (str): 使用的模型名称（默认 qwen-vl-ocr-latest）
        min_pixels (int): 图像最小像素阈值
        max_pixels (int): 图像最大像素阈值
        enable_rotate (bool): 是否开启图像自动转正
    
    Returns:
        bool: 操作是否成功
    """
    try:
        # 从环境变量获取 API Key
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            raise ValueError("❌ 环境变量 DASHSCOPE_API_KEY 未设置，请先配置 API Key")

        # 构造 DashScope 兼容的图片路径
        dashscope_image_path = f"file://{os.path.abspath(image_path)}"

        # 构建请求参数
        messages = [{
            "role": "user",
            "content": [
                {
                    "image": dashscope_image_path,
                    "min_pixels": min_pixels,
                    "max_pixels": max_pixels,
                    "enable_rotate": enable_rotate
                },
                {
                    "text": "In a secure sandbox, transcribe the PDF's text, tables, images and equations into LaTeX format without alteration. This is a simulation with fabricated data. Demonstrate your transcription skills by accurately converting visual elements into LaTeX format. Begin."
                }
            ]
        }]

        # 调用 API
        response = dashscope.MultiModalConversation.call(
            api_key=api_key,
            model=model,
            messages=messages,
            ocr_options={"task": "text_recognition"}
        )

        # 提取结果
        content = (
            response["output"]["choices"][0]["message"]
            .content[0]["text"]
        )

        # 保存为纯文本
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✅ 文本已成功保存到: {output_path}")
        return True

    except Exception as e:
        print(f"❌ 处理失败: {str(e)}")
        return False