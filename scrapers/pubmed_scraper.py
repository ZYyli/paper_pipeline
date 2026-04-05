import time
from typing import List, Dict, Optional
from Bio import Entrez
from Bio.Entrez import Parser

class PubMedScraper:
    """
    负责从 NCBI PubMed 批量抓取文献摘要的抓取器。
    """
    def __init__(self, email: str, max_retries: int = 3, sleep_time: float = 0.5):
        # 必须提供真实邮箱，这是 NCBI 的规定
        Entrez.email = email
        self.max_retries = max_retries
        self.sleep_time = sleep_time

    def fetch_abstracts(self, query: str, max_results: int = 20) -> List[Dict[str, str]]:
        """
        根据检索词获取文献摘要列表
        """
        print(f"[*] 正在检索 PubMed，检索式: '{query}'")
        try:
            # 1. 第一步：搜索并获取 PMID 列表
            handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
            record = Entrez.read(handle)
            handle.close()
            
            id_list = record.get("IdList", [])
            if not id_list:
                print("[-] 未找到匹配的文献。")
                return []
                
            print(f"[+] 找到 {len(id_list)} 篇文献，正在下载详情...")
            
            # 2. 第二步：根据 PMID 批量下载详细信息 (XML格式)
            return self._download_details(id_list)
            
        except Exception as e:
            print(f"[!] 检索过程发生致命错误: {str(e)}")
            return []

    def _download_details(self, id_list: List[str]) -> List[Dict[str, str]]:
        """内部方法：处理批量下载和解析，带重试机制"""
        results = []
        
        # 为了避免被封 IP，批量下载通常分块进行，这里为了简化演示一次性拉取
        for attempt in range(self.max_retries):
            try:
                handle = Entrez.efetch(db="pubmed", id=id_list, retmode="xml")
                records = Entrez.read(handle)
                handle.close()
                
                for paper in records.get('PubmedArticle', []):
                    medline = paper['MedlineCitation']
                    article = medline['Article']
                    
                    # 提取核心字段
                    pmid = str(medline.get('PMID', ''))
                    title = article.get('ArticleTitle', '')
                    
                    # 提取摘要（需处理复杂的 XML 嵌套情况）
                    abstract = ""
                    if 'Abstract' in article and 'AbstractText' in article['Abstract']:
                        abstract_texts = article['Abstract']['AbstractText']
                        # 有时候摘要分段（背景、方法、结论），需要拼接
                        abstract = " ".join([str(text) for text in abstract_texts])
                        
                    results.append({
                        "PMID": pmid,
                        "Title": title,
                        "Abstract": abstract
                    })
                
                # 成功拉取则跳出重试循环
                break 
                
            except Exception as e:
                print(f"[!] 下载详情失败 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}")
                time.sleep(2)  # 失败后稍作等待再重试
                
        # 强制休眠，遵守 NCBI 的访问频率限制
        time.sleep(self.sleep_time)
        return results