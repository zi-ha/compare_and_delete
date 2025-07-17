#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建测试环境脚本
用于演示重复文件清理工具的功能
"""

import os
import shutil
from pathlib import Path


def create_test_environment():
    """创建测试环境"""
    base_path = Path("测试环境")
    
    # 清理旧的测试环境
    if base_path.exists():
        shutil.rmtree(base_path)
    
    # 创建文件夹结构
    source_folder = base_path / "源文件夹"
    target_folder = base_path / "目标文件夹"
    
    source_folder.mkdir(parents=True, exist_ok=True)
    target_folder.mkdir(parents=True, exist_ok=True)
    
    # 创建子文件夹
    (source_folder / "文档").mkdir(exist_ok=True)
    (source_folder / "图片").mkdir(exist_ok=True)
    (target_folder / "备份文档").mkdir(exist_ok=True)
    (target_folder / "下载图片").mkdir(exist_ok=True)
    (target_folder / "其他文件").mkdir(exist_ok=True)
    
    # 创建测试文件
    test_files = [
        # 源文件夹中的文件
        (source_folder / "文档" / "重要文档.txt", "这是一个重要的文档内容。"),
        (source_folder / "文档" / "会议记录.txt", "今天的会议讨论了项目进展。"),
        (source_folder / "图片" / "风景照.txt", "这是一张美丽的风景照片。"),  # 用txt模拟图片
        (source_folder / "readme.txt", "这是项目的说明文件。"),
        
        # 目标文件夹中的文件（包含重复和非重复）
        (target_folder / "备份文档" / "重要文档.txt", "这是一个重要的文档内容。"),  # 重复
        (target_folder / "备份文档" / "会议记录.txt", "今天的会议讨论了项目进展。"),  # 重复
        (target_folder / "备份文档" / "新文档.txt", "这是一个新的文档。"),  # 不重复
        (target_folder / "下载图片" / "风景照.txt", "这是一张美丽的风景照片。"),  # 重复
        (target_folder / "下载图片" / "另一张照片.txt", "这是另一张照片。"),  # 不重复
        (target_folder / "其他文件" / "readme.txt", "这是项目的说明文件。"),  # 重复
        (target_folder / "其他文件" / "配置文件.txt", "这是配置文件内容。"),  # 不重复
        (target_folder / "临时文件.txt", "这是一个临时文件。"),  # 不重复
    ]
    
    # 写入文件
    for file_path, content in test_files:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print("测试环境创建完成！")
    print(f"源文件夹: {source_folder.absolute()}")
    print(f"目标文件夹: {target_folder.absolute()}")
    print("\n文件结构:")
    print_directory_tree(base_path)
    
    print("\n预期重复文件:")
    print("- 重要文档.txt")
    print("- 会议记录.txt") 
    print("- 风景照.txt")
    print("- readme.txt")
    print("\n现在可以使用GUI工具测试重复文件检测功能！")


def print_directory_tree(path, prefix="", max_depth=3, current_depth=0):
    """打印目录树结构"""
    if current_depth > max_depth:
        return
        
    path = Path(path)
    if not path.exists():
        return
        
    items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))
    
    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        current_prefix = "└── " if is_last else "├── "
        print(f"{prefix}{current_prefix}{item.name}")
        
        if item.is_dir() and current_depth < max_depth:
            next_prefix = prefix + ("    " if is_last else "│   ")
            print_directory_tree(item, next_prefix, max_depth, current_depth + 1)


if __name__ == "__main__":
    create_test_environment()