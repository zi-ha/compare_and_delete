#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件夹重复文件清理工具
比较两个文件夹中文件的哈希值，删除第二个文件夹中与第一个文件夹重复的文件
"""

import os
import hashlib
import argparse
import sys
from pathlib import Path
from typing import Dict, Set, List, Tuple


def calculate_file_hash(file_path: str, algorithm: str = 'md5') -> str:
    """
    计算文件的哈希值
    
    Args:
        file_path: 文件路径
        algorithm: 哈希算法 ('md5', 'sha1', 'sha256')
    
    Returns:
        文件的哈希值字符串
    """
    hash_func = getattr(hashlib, algorithm)()
    
    try:
        with open(file_path, 'rb') as f:
            # 分块读取文件，避免大文件占用过多内存
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except (IOError, OSError) as e:
        print(f"错误：无法读取文件 {file_path}: {e}")
        return ""


def get_folder_file_hashes(folder_path: str, algorithm: str = 'md5') -> Dict[str, List[str]]:
    """
    获取文件夹中所有文件的哈希值
    
    Args:
        folder_path: 文件夹路径
        algorithm: 哈希算法
    
    Returns:
        字典，键为哈希值，值为具有该哈希值的文件路径列表
    """
    file_hashes = {}
    folder_path = Path(folder_path)
    
    if not folder_path.exists():
        print(f"错误：文件夹 {folder_path} 不存在")
        return {}
    
    print(f"正在扫描文件夹: {folder_path}")
    
    # 递归遍历文件夹中的所有文件
    for file_path in folder_path.rglob('*'):
        if file_path.is_file():
            try:
                file_hash = calculate_file_hash(str(file_path), algorithm)
                if file_hash:
                    if file_hash not in file_hashes:
                        file_hashes[file_hash] = []
                    file_hashes[file_hash].append(str(file_path))
                    print(f"已处理: {file_path.name}")
            except Exception as e:
                print(f"处理文件 {file_path} 时出错: {e}")
    
    return file_hashes


def find_and_delete_duplicates(source_folder: str, target_folder: str, 
                             algorithm: str = 'md5', dry_run: bool = True) -> Tuple[int, int]:
    """
    查找并删除重复文件
    
    Args:
        source_folder: 源文件夹（参考文件夹）
        target_folder: 目标文件夹（要清理的文件夹）
        algorithm: 哈希算法
        dry_run: 是否为试运行模式（不实际删除文件）
    
    Returns:
        元组：(找到的重复文件数量, 实际删除的文件数量)
    """
    print("=" * 60)
    print("开始文件重复检测...")
    print("=" * 60)
    
    # 获取源文件夹的文件哈希值
    print("\n1. 扫描源文件夹（参考文件夹）...")
    source_hashes = get_folder_file_hashes(source_folder, algorithm)
    source_hash_set = set(source_hashes.keys())
    
    print(f"源文件夹共有 {sum(len(files) for files in source_hashes.values())} 个文件")
    print(f"源文件夹共有 {len(source_hash_set)} 个唯一哈希值")
    
    # 获取目标文件夹的文件哈希值
    print("\n2. 扫描目标文件夹（要清理的文件夹）...")
    target_hashes = get_folder_file_hashes(target_folder, algorithm)
    
    print(f"目标文件夹共有 {sum(len(files) for files in target_hashes.values())} 个文件")
    print(f"目标文件夹共有 {len(target_hashes)} 个唯一哈希值")
    
    # 查找重复文件
    print("\n3. 查找重复文件...")
    duplicate_files = []
    
    for file_hash, file_paths in target_hashes.items():
        if file_hash in source_hash_set:
            duplicate_files.extend(file_paths)
    
    print(f"\n找到 {len(duplicate_files)} 个重复文件:")
    for file_path in duplicate_files:
        print(f"  - {file_path}")
    
    # 删除重复文件
    deleted_count = 0
    if duplicate_files:
        if dry_run:
            print(f"\n[试运行模式] 将删除 {len(duplicate_files)} 个重复文件")
            print("如要实际删除，请使用 --execute 参数")
        else:
            print(f"\n开始删除 {len(duplicate_files)} 个重复文件...")
            for file_path in duplicate_files:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                    print(f"已删除: {file_path}")
                except Exception as e:
                    print(f"删除文件 {file_path} 失败: {e}")
    
    return len(duplicate_files), deleted_count


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="比较两个文件夹中文件的哈希值，删除第二个文件夹中的重复文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python compare_and_delete_duplicates.py source_folder target_folder
  python compare_and_delete_duplicates.py source_folder target_folder --execute
  python compare_and_delete_duplicates.py source_folder target_folder --algorithm sha256 --execute
        """
    )
    
    parser.add_argument('source_folder', help='源文件夹路径（参考文件夹）')
    parser.add_argument('target_folder', help='目标文件夹路径（要清理重复文件的文件夹）')
    parser.add_argument('--algorithm', choices=['md5', 'sha1', 'sha256'], 
                       default='md5', help='哈希算法 (默认: md5)')
    parser.add_argument('--execute', action='store_true', 
                       help='实际执行删除操作（默认为试运行模式）')
    
    args = parser.parse_args()
    
    # 验证文件夹路径
    if not os.path.exists(args.source_folder):
        print(f"错误：源文件夹 '{args.source_folder}' 不存在")
        sys.exit(1)
    
    if not os.path.exists(args.target_folder):
        print(f"错误：目标文件夹 '{args.target_folder}' 不存在")
        sys.exit(1)
    
    if os.path.abspath(args.source_folder) == os.path.abspath(args.target_folder):
        print("错误：源文件夹和目标文件夹不能是同一个文件夹")
        sys.exit(1)
    
    # 显示操作信息
    print("文件夹重复文件清理工具")
    print("=" * 60)
    print(f"源文件夹（参考）: {os.path.abspath(args.source_folder)}")
    print(f"目标文件夹（清理）: {os.path.abspath(args.target_folder)}")
    print(f"哈希算法: {args.algorithm.upper()}")
    print(f"运行模式: {'实际删除' if args.execute else '试运行（不删除文件）'}")
    
    if not args.execute:
        print("\n注意：当前为试运行模式，不会实际删除文件")
        print("如需实际删除，请添加 --execute 参数")
    
    # 执行重复文件检测和删除
    try:
        duplicate_count, deleted_count = find_and_delete_duplicates(
            args.source_folder, 
            args.target_folder, 
            args.algorithm, 
            not args.execute
        )
        
        print("\n" + "=" * 60)
        print("操作完成!")
        print(f"找到重复文件: {duplicate_count} 个")
        if args.execute:
            print(f"成功删除: {deleted_count} 个")
            if deleted_count < duplicate_count:
                print(f"删除失败: {duplicate_count - deleted_count} 个")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()