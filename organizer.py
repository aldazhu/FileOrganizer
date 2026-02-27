#!/usr/bin/env python3
"""
文件夹整理工具
自动扫描指定文件夹并根据文件扩展名分类移动文件
"""

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class FileOrganizer:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.target_folder = Path(self.config["target_folder"])
        self.file_categories = self.config["file_categories"]
        self.log_file = Path(self.config.get("log_file", "organizer_log.json"))
        self.enable_undo = self.config.get("enable_undo", True)
        self.conflict_resolution = self.config.get("conflict_resolution", "rename")
        self.dry_run = self.config.get("dry_run", False)
        self.recursive = self.config.get("recursive", False)
        
        self.operations_log = []
        self.stats = {
            "total_files": 0,
            "moved_files": 0,
            "skipped_files": 0,
            "created_folders": 0,
            "errors": 0
        }

    def load_config(self) -> Dict:
        default_config = self.get_default_config()
        
        if not self.config_path.exists():
            print(f"配置文件 {self.config_path} 不存在，使用默认配置")
            return default_config
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            
            # 合并配置：用户配置覆盖默认配置，但保留用户未指定的默认值
            merged_config = default_config.copy()
            merged_config.update(user_config)
            return merged_config
            
        except json.JSONDecodeError as e:
            print(f"配置文件格式错误: {e}")
            return default_config
        except Exception as e:
            print(f"读取配置文件失败: {e}")
            return default_config

    def get_default_config(self) -> Dict:
        return {
            "target_folder": str(Path.home() / "Downloads"),
            "file_categories": {
                "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
                "Documents": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".md"],
                "Installers": [".exe", ".msi", ".dmg", ".app", ".deb", ".rpm", ".pkg"],
                "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
                "Media": [".mp3", ".mp4", ".avi", ".mkv", ".mov", ".wav"],
                "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".json", ".xml"],
                "Others": []
            },
            "log_file": "organizer_log.json",
            "enable_undo": True,
            "conflict_resolution": "rename",
            "dry_run": True,  # 默认模拟运行
            "recursive": False  # 默认不递归处理
        }

    def get_file_category(self, file_path: Path) -> str:
        suffix = file_path.suffix.lower()
        
        for category, extensions in self.file_categories.items():
            if suffix in extensions:
                return category
        
        return "Others"

    def resolve_conflict(self, target_path: Path) -> Path:
        if not target_path.exists():
            return target_path
        
        if self.conflict_resolution == "skip":
            return None
        
        if self.conflict_resolution == "overwrite":
            return target_path
        
        if self.conflict_resolution == "rename":
            counter = 1
            while True:
                new_name = f"{target_path.stem}_{counter}{target_path.suffix}"
                new_path = target_path.parent / new_name
                if not new_path.exists():
                    return new_path
                counter += 1
        
        return None

    def create_folder_if_not_exists(self, folder_path: Path) -> bool:
        if not folder_path.exists():
            if not self.dry_run:
                folder_path.mkdir(parents=True, exist_ok=True)
                self.stats["created_folders"] += 1
            print(f"创建文件夹: {folder_path}")
            
            return True
        return False

    def move_file(self, source_path: Path, target_path: Path) -> bool:
        try:
            if self.dry_run:
                print(f"[模拟] 移动: {source_path} -> {target_path}")
                return True
            
            shutil.move(str(source_path), str(target_path))
            print(f"移动: {source_path.name} -> {target_path.parent.name}/")
            
            if self.enable_undo:
                self.operations_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "operation": "move",
                    "source": str(source_path),
                    "destination": str(target_path),
                    "original_name": source_path.name
                })
            
            self.stats["moved_files"] += 1
            return True
            
        except Exception as e:
            print(f"移动文件失败 {source_path}: {e}")
            self.stats["errors"] += 1
            return False

    def scan_and_organize(self):
        if not self.target_folder.exists():
            print(f"目标文件夹不存在: {self.target_folder}")
            return
        
        print(f"开始扫描文件夹: {self.target_folder}")
        print(f"模式: {'模拟运行' if self.dry_run else '实际运行'}")
        print(f"递归处理: {'是' if self.recursive else '否'}")
        print("-" * 50)
        
        if self.recursive:
            files = list(self.target_folder.rglob("*"))
        else:
            files = list(self.target_folder.iterdir())
        
        self.stats["total_files"] = len(files)
        
        for file_path in files:
            if file_path.is_dir():
                continue
            
            # 如果非递归模式，跳过子文件夹中的文件
            if not self.recursive and file_path.parent != self.target_folder:
                continue
            
            category = self.get_file_category(file_path)
            target_folder = self.target_folder / category
            
            self.create_folder_if_not_exists(target_folder)
            
            target_path = target_folder / file_path.name
            target_path = self.resolve_conflict(target_path)
            
            if target_path is None:
                print(f"跳过: {file_path.name} (冲突解决策略)")
                self.stats["skipped_files"] += 1
                continue
            
            if self.move_file(file_path, target_path):
                pass
            else:
                self.stats["skipped_files"] += 1
        
        self.save_log()
        self.print_summary()

    def save_log(self):
        if not self.enable_undo or self.dry_run:
            return
        
        try:
            log_data = {
                "timestamp": datetime.now().isoformat(),
                "config": self.config_path.name,
                "target_folder": str(self.target_folder),
                "operations": self.operations_log,
                "stats": self.stats
            }
            
            if self.log_file.exists():
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    existing_logs = json.load(f)
                if not isinstance(existing_logs, list):
                    existing_logs = [existing_logs]
                existing_logs.append(log_data)
            else:
                existing_logs = [log_data]
            
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(existing_logs, f, indent=2, ensure_ascii=False)
            
            print(f"操作日志已保存到: {self.log_file}")
            
        except Exception as e:
            print(f"保存日志失败: {e}")

    def print_summary(self):
        print("-" * 50)
        print("整理完成！")
        print(f"总文件数: {self.stats['total_files']}")
        print(f"移动文件: {self.stats['moved_files']}")
        print(f"跳过文件: {self.stats['skipped_files']}")
        print(f"创建文件夹: {self.stats['created_folders']}")
        print(f"错误数: {self.stats['errors']}")
        
        if self.dry_run:
            print("\n注意：本次为模拟运行，未实际移动文件")
            print("如需实际移动，请在命令行上加上--run")

    def undo_last_operation(self):
        if not self.log_file.exists():
            print("没有找到操作日志")
            return
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            if not logs:
                print("操作日志为空")
                return
            
            last_log = logs[-1] if isinstance(logs, list) else logs
            
            print(f"准备撤销操作 (时间: {last_log.get('timestamp', '未知')})")
            print(f"目标文件夹: {last_log.get('target_folder', '未知')}")
            
            operations = last_log.get('operations', [])
            if not operations:
                print("没有可撤销的操作")
                return
            
            undo_count = 0
            for op in reversed(operations):
                if op.get('operation') == 'move':
                    source = Path(op.get('destination'))
                    dest = Path(op.get('source'))
                    
                    if source.exists():
                        shutil.move(str(source), str(dest))
                        print(f"撤销移动: {source.name} -> {dest.parent.name}/")
                        undo_count += 1
                    else:
                        print(f"文件不存在，无法撤销: {source}")
            
            print(f"成功撤销 {undo_count} 个文件移动操作")
            
        except Exception as e:
            print(f"撤销操作失败: {e}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="文件夹整理工具")
    parser.add_argument("--config", "-c", default="config.json", help="配置文件路径")
    parser.add_argument("--dry-run", "-d", action="store_true", help="模拟运行，不实际移动文件（默认模式）")
    parser.add_argument("--run", "-R", action="store_true", help="实际运行，移动文件（覆盖配置文件的dry_run设置）")
    parser.add_argument("--undo", "-u", action="store_true", help="撤销上一次操作")
    parser.add_argument("--target", "-t", help="目标文件夹路径（覆盖配置文件）")
    parser.add_argument("--recursive", "-r", action="store_true", help="递归处理子文件夹中的文件")
    parser.add_argument("--no-recursive", "-nr", action="store_true", help="不递归处理子文件夹（仅处理根目录文件，默认模式）")
    
    args = parser.parse_args()
    
    organizer = FileOrganizer(args.config)
    
    # 处理运行模式选项（命令行参数优先级高于配置文件）
    if args.run:
        organizer.dry_run = False  # 强制实际运行
    elif args.dry_run:
        organizer.dry_run = True   # 显式指定模拟运行
    
    if args.target:
        organizer.target_folder = Path(args.target)
    
    # 处理递归选项（命令行参数优先级高于配置文件）
    if args.recursive:
        organizer.recursive = True
    elif args.no_recursive:
        organizer.recursive = False
    
    if args.undo:
        organizer.undo_last_operation()
    else:
        organizer.scan_and_organize()


if __name__ == "__main__":
    main()