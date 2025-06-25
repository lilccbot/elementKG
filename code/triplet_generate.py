import json
import csv
import os
import re
import openai
from openai import OpenAI
from datetime import datetime
import uuid

# 从环境变量读取 API Key（不再硬编码）
openai_api_key = os.getenv("DASHSCOPE_API_KEY")

def extract_and_save_triplets(model, schema, text):
    """
    使用 Qwen 推理模型抽取三元组并保存到 CSV 文件
    同时将思考过程和最终回复保存到指定路径
    
    参数:
    model (str): 使用的模型名称（如 "qwen-plus-2025-04-28"）
    schema (str): 关系模式定义
    text (str): 要处理的输入文本
    
    返回:
    list: 抽取的三元组列表
    """
    # 设置文件路径
    prompt_file = "/home/userdata/rmy/elementKG/code/prompt.json"
    output_file = "/home/userdata/rmy/elementKG/data/triplet.csv"
    reasoning_output_dir = "/home/userdata/rmy/elementKG/data/reasoning_outputs"
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    os.makedirs(reasoning_output_dir, exist_ok=True)
    
    try:
        # 检查 API Key 是否已设置
        if not openai_api_key:
            raise ValueError("❌ 未设置 DASHSCOPE_API_KEY 环境变量，请先配置 API Key")

        # 1. 从 JSON 文件加载提示模板
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_config = json.load(f)
        
        system_prompt = prompt_config.get("triple_extraction_prompt", "")
        
        if not system_prompt:
            raise ValueError("未在 prompt.json 中找到 triple_extraction_prompt")

        # 2. 创建 OpenAI 客户端
        client = OpenAI(
            api_key=openai_api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )

        # 构建用户消息，包含 schema 和 text
        user_content = {
            "schema": schema,
            "text": text
        }
        
        # 3. 调用 Qwen 推理模型（流式处理）
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_content, ensure_ascii=False)}
        ]
        
        # 初始化内容存储
        reasoning_content = ""
        answer_content = ""
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            extra_body={"enable_thinking": True},  # 启用推理模式
            stream=True
        )
        
        for chunk in completion:
            if chunk.choices and hasattr(chunk.choices[0].delta, "content"):
                content = chunk.choices[0].delta.content
                if content is not None:
                    answer_content += content
            
            if chunk.choices and hasattr(chunk.choices[0].delta, "reasoning_content"):
                reasoning = chunk.choices[0].delta.reasoning_content
                if reasoning is not None:
                    reasoning_content += reasoning
        
        # 4. 生成唯一文件名（基于时间戳和 UUID）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename_prefix = f"{timestamp}_{unique_id}"
        
        reasoning_file = os.path.join(reasoning_output_dir, f"{filename_prefix}_reasoning.txt")
        answer_file = os.path.join(reasoning_output_dir, f"{filename_prefix}_answer.txt")
        
        # 5. 保存思考过程和最终回复
        with open(reasoning_file, "w", encoding="utf-8") as f:
            f.write("思考过程:\n")
            f.write(reasoning_content.strip())
        
        with open(answer_file, "w", encoding="utf-8") as f:
            f.write("最终回复:\n")
            f.write(answer_content.strip())
        
        print(f"✅ 已保存思考过程至: {reasoning_file}")
        print(f"✅ 已保存最终回复至: {answer_file}")

        # 6. 处理响应内容并提取三元组
        if not answer_content:
            raise ValueError("未收到有效的回复内容")
        
        pattern = r'\{[^{}]*\}'  # 匹配三元组的 JSON 格式
        matches = re.findall(pattern, answer_content)
        
        if not matches:
            raise ValueError("在回复中未找到三元组数据")
        
        triplets = []
        for match in matches:
            try:
                triplet_data = json.loads(match)
                if all(key in triplet_data for key in ["Head", "Head_type", "Relation", "Tail", "Tail_type"]):
                    triplets.append({
                        "Head": triplet_data["Head"],
                        "Head_type": triplet_data["Head_type"],
                        "Relation": triplet_data["Relation"],
                        "Tail": triplet_data["Tail"],
                        "Tail_type": triplet_data["Tail_type"]
                    })
                else:
                    print(f"警告: 三元组格式不完整: {match}")
            except json.JSONDecodeError:
                print(f"警告: 无法解析为 JSON 的三元组: {match}")

        if not triplets:
            raise ValueError("未提取到有效的三元组数据")
        
        # 7. 保存到 CSV 文件
        file_exists = os.path.isfile(output_file)
        required_keys = ["Head", "Head_type", "Relation", "Tail", "Tail_type"]
        
        with open(output_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=required_keys)
            if not file_exists:
                writer.writeheader()
            for triplet in triplets:
                writer.writerow(triplet)

        print(f"✅ 成功抽取并保存 {len(triplets)} 个三元组")
        return triplets

    except Exception as e:
        print(f"❌ 处理失败: {str(e)}")
        return None