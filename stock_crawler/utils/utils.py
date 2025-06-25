import os
import json
from datetime import datetime

class Utils:
    """工具类，提供一些通用的辅助功能"""
    
    @staticmethod
    def ensure_directory(directory):
        """确保目录存在，如果不存在则创建"""
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"创建目录: {directory}")
    
    @staticmethod
    def format_file_size(size_bytes):
        """格式化文件大小显示"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f}{size_names[i]}"
    
    @staticmethod
    def get_file_info(filepath):
        """获取文件信息"""
        try:
            if not os.path.exists(filepath):
                return None
            
            stat = os.stat(filepath)
            return {
                'size': stat.st_size,
                'size_formatted': Utils.format_file_size(stat.st_size),
                'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'filename': os.path.basename(filepath)
            }
        except Exception as e:
            print(f"获取文件信息失败: {e}")
            return None
    
    @staticmethod
    def safe_filename(filename):
        """生成安全的文件名，去除特殊字符"""
        import re
        # 去除或替换不安全的字符
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # 去除首尾空格和点
        safe_name = safe_name.strip('. ')
        return safe_name
    
    @staticmethod
    def print_progress(current, total, prefix="进度"):
        """打印进度信息"""
        percentage = (current / total) * 100 if total > 0 else 0
        print(f"{prefix}: {current}/{total} ({percentage:.1f}%)")
    
    @staticmethod
    def load_json_file(filepath):
        """安全地加载JSON文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载JSON文件失败 {filepath}: {e}")
            return None
    
    @staticmethod
    def save_json_file(filepath, data):
        """安全地保存JSON文件"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存JSON文件失败 {filepath}: {e}")
            return False 