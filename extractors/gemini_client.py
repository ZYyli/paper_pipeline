import json
from google import genai
from google.genai import types

class GeminiExtractor:
    """
    负责调用 Gemini API 解析文献摘要的提取器。
    """
    def __init__(self, api_key: str):
        # 初始化 Gemini 客户端
        self.client = genai.Client(api_key=api_key)
        # 我们使用 2.5 Flash，因为它速度极快，处理几千篇摘要成本极低
        self.model_name = 'gemini-2.5-flash'

    def extract_info(self, abstract_text: str, prompt_template: str) -> dict:
        """
        传入摘要和 Prompt 模板，返回结构化的 JSON 字典
        """
        if not abstract_text or len(abstract_text.strip()) < 50:
            return {"error": "摘要过短或为空"}

        # 将摘要塞进我们设计好的提示词模板中
        full_prompt = prompt_template.format(abstract_text=abstract_text)

        try:
            # 调用大模型，强制要求返回 JSON 格式
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1, # 温度设低一点，保证大模型回答严谨，不乱瞎编
                ),
            )
            
            # 将大模型返回的 JSON 字符串转化为 Python 字典
            result_dict = json.loads(response.text)
            return result_dict
            
        except Exception as e:
            print(f"[!] Gemini 抽取失败: {str(e)}")
            return {"error": "API调用或解析失败"}