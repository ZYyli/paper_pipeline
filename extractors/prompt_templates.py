# extractors/prompt_templates.py

"""
这里集中管理所有的 Prompt 模板。
使用 {abstract_text} 作为占位符，在实际调用时会被替换为真实的文献摘要。
"""

MBNL1_EXTRACTION_PROMPT = """
你是一个顶级的计算生物学专家和生物医学期刊审稿人。请仔细阅读以下 PubMed 文献摘要，并严格提取相关信息。
你必须且只能输出一个合法的 JSON 字典，绝对不要包含任何 Markdown 标记（如 ```json）、换行符或任何额外的解释性问候文字。

提取字段严格要求如下：
1. "Target_Genes" (List[str]): 文献中明确提到的受 MBNL1 调控的下游靶基因或靶 RNA 列表。如果摘要中没有明确提及具体基因名，请返回空列表 []。
2. "Disease_Type" (str): 研究涉及的具体疾病或癌症类型（例如 Myotonic Dystrophy, Breast Cancer, Colorectal Cancer 等）。如果是一般的基础细胞机制研究，完全没有涉及具体疾病模型，请填 "None"。
3. "Cell_Lines" (List[str]): 实验中使用的具体细胞系名称（例如 WiDr, HeLa, C2C12 等）。如果摘要中完全未提及，返回空列表 []。
4. "Mechanism_Category" (str): 核心调控机制分类。请仔细甄别，并仅从以下三个固定选项中选择一个最符合的：
   - "RNA Stability/Decay" (侧重于转录本半衰期、降解或稳定性调控)
   - "Alternative Splicing" (侧重于转录后可变剪接)
   - "Other" (未明确或属于翻译、定位等其他层面)
5. "Key_Finding" (str): 用一句简练的中文总结 MBNL1 在该研究中的核心生物学功能、临床意义或关键发现。

待分析的文献摘要：
{abstract_text}
"""

# 新增：通用生物医学文献提取模板
GENERAL_BIO_PROMPT = """
你是一个资深的科研助手。请阅读以下 PubMed 文献摘要，并严格以 JSON 格式提取关键信息。
不要包含任何 Markdown 标记或额外解释。如果摘要中没有相关信息，请填入 "Not Mentioned" 或 []。

提取字段严格要求如下：
1. "Study_Objective" (str): 这项研究的主要目的或试图解决的核心问题是什么？（一句话总结）
2. "Key_Molecules" (List[str]): 研究中关注的核心分子（如基因、蛋白质、非编码 RNA、药物等）名称。
3. "Disease_Model" (str): 研究涉及的疾病名称或细胞系/动物模型。
4. "Main_Conclusion" (str): 研究得出的最核心结论是什么？

待分析的文献摘要：
{abstract_text}
"""

# 核心枢纽：用一个字典来管理所有模板
PROMPT_REGISTRY = {
    "mbnl1": MBNL1_EXTRACTION_PROMPT,
    "general": GENERAL_BIO_PROMPT
}
