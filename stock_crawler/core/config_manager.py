import json
import os

class ConfigManager:
    """配置文件管理类，负责读取和管理配置信息"""
    
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self._load_config()
        
    def _load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return {}
    
    def get(self, key, default=None):
        """获取配置项"""
        return self.config.get(key, default)
    
    @property
    def stock_code(self):
        """获取股票代码"""
        return self.get('stock_code', 'unknown')
    
    @property
    def f_node(self):
        """获取公告大类"""
        return self.get('f_node', '0')
    
    @property
    def s_node(self):
        """获取公告小类"""
        return self.get('s_node', '0')
    
    @property
    def cache_expire_days(self):
        """获取缓存过期天数"""
        return self.get('cache_expire_days', 7)
    
    @property
    def download_dir(self):
        """获取下载目录"""
        return self.get('download_dir', 'downloads')
    
    @property
    def cache_dir(self):
        """获取缓存目录"""
        return self.get('cache_dir', 'cache')
    
    @property
    def notice_title_keywords(self):
        """获取公告标题关键词，支持字符串或字符串列表"""
        value = self.get('notice_title_keywords', None)
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        if isinstance(value, list):
            return value
        return [] 