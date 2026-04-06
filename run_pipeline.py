import os
import json
import argparse  # <--- 引入 Python 标准库中的命令行参数解析器
import pandas as pd
from dotenv import load_dotenv  # <--- 引入环境变量加载器
from scrapers.pubmed_scraper import PubMedScraper
from extractors.prompt_templates import PROMPT_REGISTRY
from extractors.domestic_client import DomesticExtractor 
from utils.visualizer import generate_dashboard

# 自动寻找项目根目录下的 .env 文件并加载里面的变量
load_dotenv() 
# 安全地获取环境变量
EMAIL = os.getenv("NCBI_EMAIL")
API_KEY = os.getenv("DEEPSEEK_API_KEY")
# 增加一道安全防线：如果环境变量没读到，立刻报错阻断程序
if not EMAIL or not API_KEY:
    raise ValueError("🚨 致命错误：未在环境变量中找到 NCBI_EMAIL 或 DEEPSEEK_API_KEY，请检查 .env 文件！")

# 使用方法示例：
# python run_pipeline.py --query "MBNL1 AND 2015:2026[dp]" --max_results 400 --template mbnl1 --output data/processed_csv/mbnl1_all_diseases_2015_2026.csv 
def main():
    # 1. 设置命令行参数解析器
    parser = argparse.ArgumentParser(description="通用文献自动化挖掘流水线")
    parser.add_argument("--query", type=str, required=True, help="PubMed检索词")
    parser.add_argument("--max_results", type=int, default=50, help="最大抓取数量")
    parser.add_argument("--template", type=str, choices=list(PROMPT_REGISTRY.keys()), default="general", help="选择信息提取的 Prompt 模板")
    parser.add_argument("--output", type=str, default="data/processed_csv/summary.csv", help="输出路径")

    # 获取你在终端输入的参数
    args = parser.parse_args()

    print(f"=== 启动流水线 | 使用模板: [{args.template.upper()}] ===")
    scraper = PubMedScraper(email=EMAIL)
    
    extractor = DomesticExtractor(
        api_key=API_KEY,
        base_url="https://api.deepseek.com/", 
        model_name="deepseek-chat"
    )

    # 2. 直接使用终端传进来的变量，再也不用去代码里改了！
    # 动态获取用户选择的模板
    selected_prompt = PROMPT_REGISTRY[args.template]

    print(f"\n[Step 1] 启动爬虫，检索式: {args.query}")
    papers = scraper.fetch_abstracts(query=args.query, max_results=args.max_results) 
    
    if not papers:
        print("未抓取到文献，流程终止。")
        return

    print(f"\n[Step 2] 启动大模型解析，共 {len(papers)} 篇文献...")
    final_dataset = []
    
    for idx, paper in enumerate(papers):
        print(f"[{idx+1}/{len(papers)}] 正在解析: {paper['Title'][:40]}...")
        
        extracted_data = extractor.extract_info(
            abstract_text=paper['Abstract'], 
            prompt_template=selected_prompt
        )
        
        # 不管大模型返回什么乱七八糟的字段，我们只管把基础信息加进去
        # 并把列表类型的字段（如 Key_Molecules）自动转为字符串，防止 Excel 显示异常
        row_data = {"PMID": paper['PMID'], "Title": paper['Title']} # 基础信息

        for k, v in extracted_data.items(): # 动态遍历大模型返回的所有内容
            if isinstance(v, list):
                row_data[k] = ", ".join(v)
            else:
                row_data[k] = v
        
        final_dataset.append(row_data)

    print("\n[Step 3] 正在导出数据...")
    df = pd.DataFrame(final_dataset)
    
    # 使用终端传进来的输出路径
    df.to_csv(args.output, index=False, encoding='utf-8-sig')
    print(f"🎉 任务完成！结构化数据已保存至: {args.output}")
    
    # 自动触发可视化报表
    generate_dashboard(args.output)

if __name__ == "__main__":
    main()