import json
from openai import OpenAI

class DomesticExtractor:
    """
    通用国产大模型提取器 (兼容 OpenAI 接口标准，支持智谱、DeepSeek等)
    """
    def __init__(self, api_key: str, base_url: str, model_name: str):
        # 初始化客户端
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model_name = model_name

    def extract_info(self, abstract_text: str, prompt_template: str) -> dict:
        if not abstract_text or len(abstract_text.strip()) < 50:
            return {"error": "摘要过短或为空"}

        full_prompt = prompt_template.format(abstract_text=abstract_text)

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "你是一个严谨的科学数据提取器。"},
                    {"role": "user", "content": full_prompt}
                ],
                response_format={"type": "json_object"}, # 强制输出 JSON
                temperature=0.1
            )
            
            result_str = response.choices[0].message.content
            return json.loads(result_str)
            
        except Exception as e:
            print(f"[!] 大模型抽取失败: {str(e)}")
            return {"error": "API调用或解析失败"}