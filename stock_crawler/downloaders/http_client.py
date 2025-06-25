import os
import re
import json
import time
import requests

class HttpClient:
    """网络请求管理类，负责HTTP请求和JSONP响应处理"""
    
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0'
        }
    
    def generate_timestamp(self):
        """生成时间戳"""
        return str(int(time.time() * 1000))
    
    def get_jsonp_response(self, url):
        """获取JSONP响应并解析为JSON，支持缓存"""
        # 生成缓存文件名
        cache_file = self.cache_manager.generate_cache_filename(url)
        
        # 检查缓存是否存在
        cached_data = self.cache_manager.load_cache(cache_file)
        if cached_data:
            print(f"使用缓存数据: {os.path.basename(cache_file)}")
            return cached_data
        
        # 缓存不存在，发起网络请求
        print(f"发起网络请求: {os.path.basename(cache_file)}")
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # 使用正则表达式提取JSON部分
            json_str = re.search(r'jQuery\d+_\d+\((.*)\)', response.text).group(1)
            data = json.loads(json_str)
            
            # 保存到缓存，传递原始URL
            self.cache_manager.save_cache(cache_file, data, original_url=url)
            
            return data
        except Exception as e:
            print(f"Error fetching or parsing JSONP response: {e}")
            return None 