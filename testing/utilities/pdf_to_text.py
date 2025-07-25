#!/usr/bin/env python3
"""
PDF到文本转换工具
用于将FR3和Hermes的PDF文档批量转换为文本文件
"""

import os
import sys
import PyPDF2
import pdfplumber
from pathlib import Path

def convert_pdf_to_text_pypdf2(pdf_path, output_path):
    """使用PyPDF2转换PDF为文本"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += f"\n--- 第 {page_num + 1} 页 ---\n"
                text += page.extract_text()
                
        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write(text)
        
        print(f"✅ 成功转换: {pdf_path} -> {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ PyPDF2转换失败 {pdf_path}: {e}")
        return False

def convert_pdf_to_text_pdfplumber(pdf_path, output_path):
    """使用pdfplumber转换PDF为文本（更好的中文支持）"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            
            for page_num, page in enumerate(pdf.pages):
                text += f"\n--- 第 {page_num + 1} 页 ---\n"
                page_text = page.extract_text()
                if page_text:
                    text += page_text
                    
                # 尝试提取表格
                tables = page.extract_tables()
                if tables:
                    text += "\n[表格数据]\n"
                    for table in tables:
                        for row in table:
                            if row:
                                text += " | ".join(str(cell) if cell else "" for cell in row) + "\n"
                
        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write(text)
        
        print(f"✅ 成功转换: {pdf_path} -> {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ pdfplumber转换失败 {pdf_path}: {e}")
        return False

def batch_convert_pdfs():
    """批量转换PDF文件"""
    
    # 项目根目录
    project_root = Path(__file__).parent.parent
    
    # PDF文件夹路径
    pdf_folders = [
        project_root / "fr3 pdf",
        project_root / "hermes pdf"
    ]
    
    # 输出目录
    output_dir = project_root / "docs_converted"
    output_dir.mkdir(exist_ok=True)
    
    # 创建子目录
    fr3_output = output_dir / "fr3_docs"
    hermes_output = output_dir / "hermes_docs"
    fr3_output.mkdir(exist_ok=True)
    hermes_output.mkdir(exist_ok=True)
    
    converted_count = 0
    failed_count = 0
    
    for pdf_folder in pdf_folders:
        if not pdf_folder.exists():
            print(f"⚠️  文件夹不存在: {pdf_folder}")
            continue
            
        folder_name = pdf_folder.name
        if folder_name == "fr3 pdf":
            current_output = fr3_output
        else:
            current_output = hermes_output
            
        print(f"\n🔄 处理文件夹: {pdf_folder}")
        
        for pdf_file in pdf_folder.glob("*.pdf"):
            # 生成输出文件名
            output_name = pdf_file.stem + ".txt"
            output_path = current_output / output_name
            
            print(f"📄 转换: {pdf_file.name}")
            
            # 先尝试pdfplumber（对中文支持更好）
            success = convert_pdf_to_text_pdfplumber(pdf_file, output_path)
            
            # 如果pdfplumber失败，尝试PyPDF2
            if not success:
                print(f"🔄 尝试PyPDF2方法...")
                success = convert_pdf_to_text_pypdf2(pdf_file, output_path)
            
            if success:
                converted_count += 1
            else:
                failed_count += 1
    
    print(f"\n📊 转换完成:")
    print(f"✅ 成功: {converted_count} 个文件")
    print(f"❌ 失败: {failed_count} 个文件")
    print(f"📁 输出目录: {output_dir}")
    
    # 生成索引文件
    create_index_file(output_dir)

def create_index_file(output_dir):
    """创建文档索引文件"""
    index_path = output_dir / "README.md"
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write("# FR3和Hermes文档索引\n\n")
        f.write("## FR3机器人文档\n\n")
        
        fr3_dir = output_dir / "fr3_docs"
        if fr3_dir.exists():
            for txt_file in sorted(fr3_dir.glob("*.txt")):
                f.write(f"- [{txt_file.stem}]({txt_file.relative_to(output_dir)})\n")
        
        f.write("\n## Hermes底盘文档\n\n")
        
        hermes_dir = output_dir / "hermes_docs"
        if hermes_dir.exists():
            for txt_file in sorted(hermes_dir.glob("*.txt")):
                f.write(f"- [{txt_file.stem}]({txt_file.relative_to(output_dir)})\n")
    
    print(f"📋 索引文件已创建: {index_path}")

if __name__ == "__main__":
    print("🚀 开始批量转换PDF文档...")
    
    # 检查依赖
    try:
        import PyPDF2
        import pdfplumber
        print("✅ 依赖检查通过")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请安装: pip install PyPDF2 pdfplumber")
        sys.exit(1)
    
    batch_convert_pdfs()