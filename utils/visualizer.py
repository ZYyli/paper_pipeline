import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def save_figure_formats(fig, output_dir, base_name, suffix, formats=['png', 'pdf'], dpi=600):
    """
    保存图形为多种格式
    
    参数:
        fig: matplotlib 图形对象
        output_dir: 输出目录
        base_name: 基础文件名
        suffix: 文件后缀
        formats: 需要保存的格式列表，默认 ['png', 'pdf']
        dpi: PNG 等位图格式的 DPI，默认 600
    """
    saved_files = []
    
    for fmt in formats:
        file_path = os.path.join(output_dir, f"{base_name}_{suffix}.{fmt}")
        
        if fmt in ['png', 'jpg', 'jpeg', 'tiff']:  # 位图格式
            fig.savefig(file_path, dpi=dpi, bbox_inches='tight')
        else:  # 矢量格式（pdf, svg 等）
            fig.savefig(file_path, bbox_inches='tight')
        
        saved_files.append(file_path)
        print(f"已保存: {file_path}")
    
    return saved_files

# 使用示例：
# save_figure_formats(plt, output_dir, base_name, "mechanism_pie", 
#                     formats=['png', 'pdf', 'svg'], dpi=600)

def generate_dashboard(csv_path):
    print("\n[Step 4] 启动自动可视化引擎...")
    
    # 尝试读取刚生成的 CSV
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"  [!] 读取表格失败，跳过画图: {e}")
        return
    
    # 智能提取输出目录和文件前缀，保证图片和 CSV 存在同一个文件夹，且名字对应
    output_dir = os.path.dirname(csv_path)
    base_name = os.path.splitext(os.path.basename(csv_path))[0]
    
    # 设置画图风格（自动适配英文字体，避免中文乱码警告）
    sns.set_theme(style="whitegrid")
    
    # ==============================
    # 绘制 图表 1: 机制饼图
    # ==============================
    plt.figure(figsize=(6, 4))
    mechanism_data = df[~df['Mechanism_Category'].isin(['Error', 'None'])]
    
    if not mechanism_data.empty:
        mechanism_counts = mechanism_data['Mechanism_Category'].value_counts()
        plt.pie(mechanism_counts, 
                labels=mechanism_counts.index, 
                autopct='%1.1f%%', 
                startangle=140, 
                colors=sns.color_palette("pastel")[0:len(mechanism_counts)])
        
        plt.title("Distribution of Regulatory Mechanisms", fontsize=14, pad=20)
        plt.axis('equal')
        
        save_figure_formats(plt, output_dir, base_name, "mechanism_pie", formats=['png', 'pdf'])
        print(f"  👉 机制分布饼图已自动保存至: {output_dir}")
    
    plt.close() # 极其重要：关闭画板，防止大批量跑图时服务器内存泄漏

    # ==============================
    # 绘制 图表 2: 疾病条形图
    # ==============================
    plt.figure(figsize=(6, 4.5))
    disease_df = df.dropna(subset=['Disease_Type'])
    disease_df = disease_df[~disease_df['Disease_Type'].isin(["None", "Error", "Not Mentioned"])]
    
    if not disease_df.empty:
        disease_df.loc[:, 'Disease_Type'] = disease_df['Disease_Type'].str.title()
        disease_counts = disease_df['Disease_Type'].value_counts().head(15)
        
        ax = sns.barplot(x=disease_counts.values, y=disease_counts.index, 
                        hue=disease_counts.index,  # 按y轴变量分组
                        palette="mako",
                        legend=False)
        
        for i, v in enumerate(disease_counts.values):
            ax.text(v + 0.1, i, str(v), color='black', va='center', fontsize=10)
            
        plt.title("Top 15 Diseases/Cancers", fontsize=14, pad=15)
        plt.xlabel("Number of Publications", fontsize=12)
        plt.ylabel("Disease Type", fontsize=12)
        
        save_figure_formats(plt, output_dir, base_name, "_disease_bar", formats=['png', 'pdf'])
        print(f"  👉 疾病排名柱状图已自动保存至: {output_dir}")
        
    plt.close()
    print("✨ 可视化报表生成完毕！")