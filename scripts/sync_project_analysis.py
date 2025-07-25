#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROJECT_STRUCTURE_ANALYSIS.md 文档同步脚本

用途：保持根目录和docs/project/目录下的PROJECT_STRUCTURE_ANALYSIS.md文档同步
使用：python scripts/sync_project_analysis.py [--from-root|--from-docs]
"""

import os
import argparse
import shutil
from pathlib import Path


def get_project_root():
    """获取项目根目录"""
    current_dir = Path(__file__).parent
    return current_dir.parent


def sync_documents(source_path: str, direction: str = "from-root"):
    """同步两个PROJECT_STRUCTURE_ANALYSIS.md文档"""
    
    project_root = get_project_root()
    root_doc = project_root / "PROJECT_STRUCTURE_ANALYSIS.md"
    docs_doc = project_root / "docs" / "project" / "PROJECT_STRUCTURE_ANALYSIS.md"
    
    if direction == "from-root":
        source = root_doc
        target = docs_doc
        print(f"📄 从根目录同步到docs/project/目录")
    else:
        source = docs_doc
        target = root_doc
        print(f"📄 从docs/project/目录同步到根目录")
    
    if not source.exists():
        print(f"❌ 源文件不存在: {source}")
        return False
    
    try:
        # 读取源文件内容
        with open(source, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 更新同步信息
        if direction == "from-root":
            content = content.replace(
                "**📄 文档同步**: 本文档与 `docs/project/PROJECT_STRUCTURE_ANALYSIS.md` 保持同步",
                "**📄 文档同步**: 本文档与根目录 `PROJECT_STRUCTURE_ANALYSIS.md` 保持同步"
            )
        else:
            content = content.replace(
                "**📄 文档同步**: 本文档与根目录 `PROJECT_STRUCTURE_ANALYSIS.md` 保持同步",
                "**📄 文档同步**: 本文档与 `docs/project/PROJECT_STRUCTURE_ANALYSIS.md` 保持同步"
            )
        
        # 写入目标文件
        with open(target, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 文档同步完成")
        print(f"   源文件: {source}")
        print(f"   目标文件: {target}")
        return True
        
    except Exception as e:
        print(f"❌ 同步失败: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(description="同步PROJECT_STRUCTURE_ANALYSIS.md文档")
    parser.add_argument(
        "--from-root", 
        action="store_true", 
        help="从根目录同步到docs/project/"
    )
    parser.add_argument(
        "--from-docs", 
        action="store_true", 
        help="从docs/project/同步到根目录"
    )
    
    args = parser.parse_args()
    
    if args.from_docs:
        direction = "from-docs"
    else:
        direction = "from-root"  # 默认方向
    
    print("🔄 PROJECT_STRUCTURE_ANALYSIS.md 文档同步工具")
    print("=" * 50)
    
    success = sync_documents("", direction)
    
    if success:
        print("✅ 同步完成")
        print("\n⚠️  提醒：请记住在修改任一文档后运行此脚本以保持同步")
    else:
        print("❌ 同步失败")
        exit(1)


if __name__ == "__main__":
    main()