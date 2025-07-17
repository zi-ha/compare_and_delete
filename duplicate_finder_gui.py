#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件夹重复文件清理工具 - GUI版本
提供图形界面来查看和选择性删除重复文件
"""

import os
import hashlib
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
# tkinter.dnd没有DND_FILES，这是tkinterdnd2的特性
from pathlib import Path
import threading
from typing import Dict, List, Tuple
import json
from datetime import datetime
import tkinterdnd2 as tkdnd


class DuplicateFileFinderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("重复文件清理工具")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # 设置样式
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # 数据存储
        self.source_folder = tk.StringVar()
        self.target_folder = tk.StringVar()
        self.algorithm = tk.StringVar(value="md5")
        self.duplicate_files = []
        self.is_scanning = False
        
        # 设置拖放支持
        self.root.drop_target_register(tkdnd.DND_FILES)
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="重复文件清理工具", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 文件夹选择区域
        self.setup_folder_selection(main_frame)
        
        # 算法选择和控制按钮
        self.setup_controls(main_frame)
        
        # 进度条
        self.setup_progress(main_frame)
        
        # 结果显示区域
        self.setup_results_area(main_frame)
        
        # 状态栏
        self.setup_status_bar(main_frame)
        
    def setup_folder_selection(self, parent):
        """设置文件夹选择区域"""
        # 源文件夹
        ttk.Label(parent, text="源文件夹（参考）:").grid(row=1, column=0, sticky=tk.W, pady=5)
        source_frame = ttk.Frame(parent)
        source_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        source_frame.columnconfigure(0, weight=1)
        
        self.source_entry = ttk.Entry(source_frame, textvariable=self.source_folder, width=50)
        self.source_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # 设置源文件夹拖放
        self.source_entry.drop_target_register(tkdnd.DND_FILES)
        self.source_entry.dnd_bind('<<Drop>>', lambda e: self.on_drop_source(e))
        
        source_browse_btn = ttk.Button(source_frame, text="浏览", 
                                     command=self.browse_source_folder)
        source_browse_btn.grid(row=0, column=1)
        
        # 添加拖放提示
        source_tip = ttk.Label(source_frame, text="(支持拖放文件夹)", 
                              font=('Arial', 8), foreground='gray')
        source_tip.grid(row=1, column=0, sticky=tk.W, pady=(2, 0))
        
        # 目标文件夹
        ttk.Label(parent, text="目标文件夹（清理）:").grid(row=2, column=0, sticky=tk.W, pady=5)
        target_frame = ttk.Frame(parent)
        target_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        target_frame.columnconfigure(0, weight=1)
        
        self.target_entry = ttk.Entry(target_frame, textvariable=self.target_folder, width=50)
        self.target_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # 设置目标文件夹拖放
        self.target_entry.drop_target_register(tkdnd.DND_FILES)
        self.target_entry.dnd_bind('<<Drop>>', lambda e: self.on_drop_target(e))
        
        target_browse_btn = ttk.Button(target_frame, text="浏览", 
                                     command=self.browse_target_folder)
        target_browse_btn.grid(row=0, column=1)
        
        # 添加拖放提示
        target_tip = ttk.Label(target_frame, text="(支持拖放文件夹)", 
                              font=('Arial', 8), foreground='gray')
        target_tip.grid(row=1, column=0, sticky=tk.W, pady=(2, 0))
        
    def setup_controls(self, parent):
        """设置控制区域"""
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # 算法选择
        ttk.Label(control_frame, text="哈希算法:").grid(row=0, column=0, padx=(0, 5))
        algorithm_combo = ttk.Combobox(control_frame, textvariable=self.algorithm,
                                     values=["md5", "sha1", "sha256"], state="readonly", width=10)
        algorithm_combo.grid(row=0, column=1, padx=(0, 20))
        
        # 按钮
        self.scan_button = ttk.Button(control_frame, text="开始扫描", 
                                     command=self.start_scan)
        self.scan_button.grid(row=0, column=2, padx=5)
        
        self.delete_button = ttk.Button(control_frame, text="删除选中文件", 
                                       command=self.delete_selected_files, state="disabled")
        self.delete_button.grid(row=0, column=3, padx=5)
        
        self.export_button = ttk.Button(control_frame, text="导出列表", 
                                       command=self.export_results, state="disabled")
        self.export_button.grid(row=0, column=4, padx=5)
        
        self.clear_button = ttk.Button(control_frame, text="清空结果", 
                                      command=self.clear_results)
        self.clear_button.grid(row=0, column=5, padx=5)
        
    def setup_progress(self, parent):
        """设置进度条"""
        self.progress_var = tk.StringVar(value="就绪")
        self.progress_label = ttk.Label(parent, textvariable=self.progress_var)
        self.progress_label.grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(parent, mode='indeterminate')
        self.progress_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
    def setup_results_area(self, parent):
        """设置结果显示区域"""
        # 结果框架
        results_frame = ttk.LabelFrame(parent, text="重复文件列表", padding="5")
        results_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # 创建Treeview
        columns = ("选择", "文件名", "路径", "大小", "哈希值", "修改时间")
        self.tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=15)
        
        # 设置列标题和宽度
        self.tree.heading("选择", text="选择")
        self.tree.heading("文件名", text="文件名")
        self.tree.heading("路径", text="路径")
        self.tree.heading("大小", text="大小")
        self.tree.heading("哈希值", text="哈希值")
        self.tree.heading("修改时间", text="修改时间")
        
        self.tree.column("选择", width=60, minwidth=60)
        self.tree.column("文件名", width=200, minwidth=150)
        self.tree.column("路径", width=300, minwidth=200)
        self.tree.column("大小", width=100, minwidth=80)
        self.tree.column("哈希值", width=200, minwidth=150)
        self.tree.column("修改时间", width=150, minwidth=120)
        
        # 滚动条
        v_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(results_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # 布局
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # 绑定事件
        self.tree.bind("<Button-1>", self.on_tree_click)
        self.tree.bind("<Double-1>", self.on_tree_double_click)
        self.tree.bind("<Return>", self.on_tree_enter)  # 回车键切换选择
        
        # 右键菜单
        self.setup_context_menu()
        
        # 批量选择按钮
        select_frame = ttk.Frame(results_frame)
        select_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(select_frame, text="全选", command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(select_frame, text="全不选", command=self.deselect_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(select_frame, text="反选", command=self.invert_selection).pack(side=tk.LEFT, padx=5)
        
        # 统计信息
        self.stats_var = tk.StringVar(value="统计: 0 个重复文件")
        ttk.Label(select_frame, textvariable=self.stats_var).pack(side=tk.RIGHT, padx=5)
        
    def setup_context_menu(self):
        """设置右键菜单"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="切换选择", command=self.toggle_current_selection)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="打开文件", command=self.open_selected_file)
        self.context_menu.add_command(label="打开文件夹", command=self.open_file_folder)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="复制路径", command=self.copy_file_path)
        self.context_menu.add_command(label="查看属性", command=self.show_file_properties)
        
        self.tree.bind("<Button-3>", self.show_context_menu)
        
    def setup_status_bar(self, parent):
        """设置状态栏"""
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(parent, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def browse_source_folder(self):
        """浏览源文件夹"""
        folder = filedialog.askdirectory(title="选择源文件夹（参考文件夹）")
        if folder:
            self.source_folder.set(folder)
            
    def browse_target_folder(self):
        """浏览目标文件夹"""
        folder = filedialog.askdirectory(title="选择目标文件夹（要清理的文件夹）")
        if folder:
            self.target_folder.set(folder)
    
    def on_drop_source(self, event):
        """处理源文件夹拖放事件"""
        files = self.root.tk.splitlist(event.data)
        if files:
            folder_path = files[0]
            if os.path.isdir(folder_path):
                self.source_folder.set(folder_path)
                self.status_var.set(f"已设置源文件夹: {os.path.basename(folder_path)}")
            else:
                messagebox.showwarning("警告", "请拖放文件夹，不是文件")
    
    def on_drop_target(self, event):
        """处理目标文件夹拖放事件"""
        files = self.root.tk.splitlist(event.data)
        if files:
            folder_path = files[0]
            if os.path.isdir(folder_path):
                self.target_folder.set(folder_path)
                self.status_var.set(f"已设置目标文件夹: {os.path.basename(folder_path)}")
            else:
                messagebox.showwarning("警告", "请拖放文件夹，不是文件")
            
    def start_scan(self):
        """开始扫描重复文件"""
        if not self.source_folder.get() or not self.target_folder.get():
            messagebox.showerror("错误", "请选择源文件夹和目标文件夹")
            return
            
        if not os.path.exists(self.source_folder.get()):
            messagebox.showerror("错误", "源文件夹不存在")
            return
            
        if not os.path.exists(self.target_folder.get()):
            messagebox.showerror("错误", "目标文件夹不存在")
            return
            
        if os.path.abspath(self.source_folder.get()) == os.path.abspath(self.target_folder.get()):
            messagebox.showerror("错误", "源文件夹和目标文件夹不能是同一个")
            return
            
        # 清空之前的结果
        self.clear_results()
        
        # 开始扫描
        self.is_scanning = True
        self.scan_button.config(state="disabled")
        self.progress_bar.start()
        
        # 在新线程中执行扫描
        scan_thread = threading.Thread(target=self.scan_duplicates)
        scan_thread.daemon = True
        scan_thread.start()
        
    def scan_duplicates(self):
        """扫描重复文件（在后台线程中执行）"""
        try:
            self.update_progress("正在扫描源文件夹...")
            source_hashes = self.get_folder_file_hashes(self.source_folder.get())
            
            self.update_progress("正在扫描目标文件夹...")
            target_hashes = self.get_folder_file_hashes(self.target_folder.get())
            
            self.update_progress("正在查找重复文件...")
            duplicates = []
            
            for file_hash, file_paths in target_hashes.items():
                if file_hash in source_hashes:
                    for file_path in file_paths:
                        file_info = self.get_file_info(file_path, file_hash)
                        duplicates.append(file_info)
            
            # 在主线程中更新UI
            self.root.after(0, self.scan_completed, duplicates)
            
        except Exception as e:
            self.root.after(0, self.scan_error, str(e))
            
    def get_folder_file_hashes(self, folder_path):
        """获取文件夹中所有文件的哈希值"""
        file_hashes = {}
        folder_path = Path(folder_path)
        
        for file_path in folder_path.rglob('*'):
            if file_path.is_file():
                try:
                    file_hash = self.calculate_file_hash(str(file_path))
                    if file_hash:
                        if file_hash not in file_hashes:
                            file_hashes[file_hash] = []
                        file_hashes[file_hash].append(str(file_path))
                        
                        # 更新进度
                        self.update_progress(f"正在处理: {file_path.name}")
                except Exception as e:
                    print(f"处理文件 {file_path} 时出错: {e}")
                    
        return file_hashes
        
    def calculate_file_hash(self, file_path):
        """计算文件哈希值"""
        algorithm = self.algorithm.get()
        hash_func = getattr(hashlib, algorithm)()
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception:
            return ""
            
    def get_file_info(self, file_path, file_hash):
        """获取文件信息"""
        path_obj = Path(file_path)
        stat = path_obj.stat()
        
        return {
            'path': file_path,
            'name': path_obj.name,
            'size': stat.st_size,
            'hash': file_hash,
            'mtime': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            'selected': False
        }
        
    def format_file_size(self, size_bytes):
        """格式化文件大小"""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f} {size_names[i]}"
        
    def update_progress(self, message):
        """更新进度信息"""
        self.root.after(0, lambda: self.progress_var.set(message))
        
    def scan_completed(self, duplicates):
        """扫描完成"""
        self.is_scanning = False
        self.progress_bar.stop()
        self.scan_button.config(state="normal")
        
        self.duplicate_files = duplicates
        self.populate_tree()
        
        if duplicates:
            self.delete_button.config(state="normal")
            self.export_button.config(state="normal")
            self.progress_var.set(f"扫描完成，找到 {len(duplicates)} 个重复文件")
            self.status_var.set(f"找到 {len(duplicates)} 个重复文件")
        else:
            self.progress_var.set("扫描完成，未找到重复文件")
            self.status_var.set("未找到重复文件")
            
    def scan_error(self, error_message):
        """扫描出错"""
        self.is_scanning = False
        self.progress_bar.stop()
        self.scan_button.config(state="normal")
        self.progress_var.set("扫描出错")
        messagebox.showerror("扫描错误", f"扫描过程中出现错误:\n{error_message}")
        
    def populate_tree(self):
        """填充树形控件"""
        # 清空现有项目
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 添加重复文件
        for file_info in self.duplicate_files:
            checkbox = "☐"  # 未选中的复选框
            values = (
                checkbox,
                file_info['name'],
                file_info['path'],
                self.format_file_size(file_info['size']),
                file_info['hash'][:16] + "...",  # 只显示哈希值的前16位
                file_info['mtime']
            )
            self.tree.insert("", "end", values=values)
            
        self.update_stats()
        
    def update_stats(self):
        """更新统计信息"""
        total = len(self.duplicate_files)
        selected = sum(1 for f in self.duplicate_files if f['selected'])
        total_size = sum(f['size'] for f in self.duplicate_files if f['selected'])
        
        stats_text = f"统计: {total} 个重复文件, {selected} 个已选中"
        if selected > 0:
            stats_text += f", 将释放 {self.format_file_size(total_size)}"
            
        self.stats_var.set(stats_text)
        
    def on_tree_click(self, event):
        """处理树形控件点击事件"""
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x, event.y)
            if column == "#1":  # 选择列
                item = self.tree.identify_row(event.y)
                if item:
                    self.toggle_selection(item)
                    return "break"  # 阻止默认选择行为
                    
    def on_tree_double_click(self, event):
        """处理双击事件 - 切换选择状态而不是打开文件"""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item:
            self.toggle_selection(item)
            return "break"  # 阻止默认行为
    
    def on_tree_enter(self, event):
        """处理回车键事件"""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item:
            self.toggle_selection(item)
            
    def toggle_current_selection(self):
        """切换当前选中行的选择状态"""
        selection = self.tree.selection()
        if selection:
            self.toggle_selection(selection[0])
        else:
            messagebox.showinfo("提示", "请先选择一行")
            
    def toggle_selection(self, item):
        """切换选择状态"""
        try:
            index = self.tree.index(item)
            file_info = self.duplicate_files[index]
            file_info['selected'] = not file_info['selected']
            
            # 更新显示
            checkbox = "☑" if file_info['selected'] else "☐"
            values = list(self.tree.item(item, "values"))
            values[0] = checkbox
            self.tree.item(item, values=values)
            
            self.update_stats()
        except (IndexError, tk.TclError):
            pass
            
    def select_all(self):
        """全选"""
        for i, file_info in enumerate(self.duplicate_files):
            file_info['selected'] = True
            item = self.tree.get_children()[i]
            values = list(self.tree.item(item, "values"))
            values[0] = "☑"
            self.tree.item(item, values=values)
        self.update_stats()
        
    def deselect_all(self):
        """全不选"""
        for i, file_info in enumerate(self.duplicate_files):
            file_info['selected'] = False
            item = self.tree.get_children()[i]
            values = list(self.tree.item(item, "values"))
            values[0] = "☐"
            self.tree.item(item, values=values)
        self.update_stats()
        
    def invert_selection(self):
        """反选"""
        for i, file_info in enumerate(self.duplicate_files):
            file_info['selected'] = not file_info['selected']
            item = self.tree.get_children()[i]
            values = list(self.tree.item(item, "values"))
            values[0] = "☑" if file_info['selected'] else "☐"
            self.tree.item(item, values=values)
        self.update_stats()
        
    def delete_selected_files(self):
        """删除选中的文件"""
        selected_files = [f for f in self.duplicate_files if f['selected']]
        
        if not selected_files:
            messagebox.showwarning("警告", "请先选择要删除的文件")
            return
            
        # 确认删除
        total_size = sum(f['size'] for f in selected_files)
        message = f"确定要删除 {len(selected_files)} 个文件吗？\n"
        message += f"将释放 {self.format_file_size(total_size)} 的空间。\n\n"
        message += "此操作不可撤销！"
        
        if not messagebox.askyesno("确认删除", message):
            return
            
        # 执行删除
        deleted_count = 0
        failed_files = []
        
        for file_info in selected_files:
            try:
                os.remove(file_info['path'])
                deleted_count += 1
            except Exception as e:
                failed_files.append(f"{file_info['name']}: {str(e)}")
                
        # 更新结果
        self.duplicate_files = [f for f in self.duplicate_files if not f['selected']]
        self.populate_tree()
        
        # 显示结果
        if failed_files:
            message = f"成功删除 {deleted_count} 个文件\n"
            message += f"删除失败 {len(failed_files)} 个文件:\n"
            message += "\n".join(failed_files[:5])  # 只显示前5个失败的文件
            if len(failed_files) > 5:
                message += f"\n... 还有 {len(failed_files) - 5} 个文件删除失败"
            messagebox.showwarning("删除完成", message)
        else:
            messagebox.showinfo("删除完成", f"成功删除 {deleted_count} 个文件")
            
        if not self.duplicate_files:
            self.delete_button.config(state="disabled")
            self.export_button.config(state="disabled")
            
    def export_results(self):
        """导出结果到文件"""
        if not self.duplicate_files:
            messagebox.showwarning("警告", "没有可导出的数据")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="导出重复文件列表",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.duplicate_files, f, ensure_ascii=False, indent=2)
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("重复文件列表\n")
                    f.write("=" * 50 + "\n")
                    f.write(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"源文件夹: {self.source_folder.get()}\n")
                    f.write(f"目标文件夹: {self.target_folder.get()}\n")
                    f.write(f"哈希算法: {self.algorithm.get().upper()}\n")
                    f.write(f"重复文件数量: {len(self.duplicate_files)}\n\n")
                    
                    for i, file_info in enumerate(self.duplicate_files, 1):
                        f.write(f"{i}. {file_info['name']}\n")
                        f.write(f"   路径: {file_info['path']}\n")
                        f.write(f"   大小: {self.format_file_size(file_info['size'])}\n")
                        f.write(f"   哈希: {file_info['hash']}\n")
                        f.write(f"   修改时间: {file_info['mtime']}\n")
                        f.write(f"   已选中: {'是' if file_info['selected'] else '否'}\n\n")
                        
            messagebox.showinfo("导出成功", f"结果已导出到:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("导出失败", f"导出过程中出现错误:\n{str(e)}")
            
    def clear_results(self):
        """清空结果"""
        self.duplicate_files = []
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.delete_button.config(state="disabled")
        self.export_button.config(state="disabled")
        self.stats_var.set("统计: 0 个重复文件")
        self.status_var.set("就绪")
        self.progress_var.set("就绪")
        
    def show_context_menu(self, event):
        """显示右键菜单"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
            
    def open_selected_file(self):
        """打开选中的文件"""
        selection = self.tree.selection()
        if selection:
            try:
                index = self.tree.index(selection[0])
                file_path = self.duplicate_files[index]['path']
                os.startfile(file_path)
            except Exception as e:
                messagebox.showerror("错误", f"无法打开文件:\n{str(e)}")
                
    def open_file_folder(self):
        """打开文件所在文件夹"""
        selection = self.tree.selection()
        if selection:
            try:
                index = self.tree.index(selection[0])
                file_path = self.duplicate_files[index]['path']
                folder_path = os.path.dirname(file_path)
                os.startfile(folder_path)
            except Exception as e:
                messagebox.showerror("错误", f"无法打开文件夹:\n{str(e)}")
                
    def copy_file_path(self):
        """复制文件路径到剪贴板"""
        selection = self.tree.selection()
        if selection:
            try:
                index = self.tree.index(selection[0])
                file_path = self.duplicate_files[index]['path']
                self.root.clipboard_clear()
                self.root.clipboard_append(file_path)
                self.status_var.set("文件路径已复制到剪贴板")
            except Exception as e:
                messagebox.showerror("错误", f"无法复制路径:\n{str(e)}")
                
    def show_file_properties(self):
        """显示文件属性"""
        selection = self.tree.selection()
        if selection:
            try:
                index = self.tree.index(selection[0])
                file_info = self.duplicate_files[index]
                
                # 创建属性窗口
                prop_window = tk.Toplevel(self.root)
                prop_window.title("文件属性")
                prop_window.geometry("500x300")
                prop_window.resizable(False, False)
                
                # 属性信息
                info_text = f"""文件名: {file_info['name']}
路径: {file_info['path']}
大小: {self.format_file_size(file_info['size'])} ({file_info['size']:,} 字节)
修改时间: {file_info['mtime']}
哈希值 ({self.algorithm.get().upper()}): {file_info['hash']}
选中状态: {'是' if file_info['selected'] else '否'}"""
                
                text_widget = scrolledtext.ScrolledText(prop_window, wrap=tk.WORD, 
                                                       width=60, height=15)
                text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                text_widget.insert(tk.END, info_text)
                text_widget.config(state=tk.DISABLED)
                
            except Exception as e:
                messagebox.showerror("错误", f"无法显示文件属性:\n{str(e)}")


def main():
    """主函数"""
    root = tkdnd.Tk()  # 使用tkinterdnd2.Tk支持拖放
    app = DuplicateFileFinderGUI(root)
    
    # 设置窗口图标（如果有的话）
    try:
        root.iconbitmap(default="icon.ico")
    except:
        pass
        
    root.mainloop()


if __name__ == "__main__":
    main()