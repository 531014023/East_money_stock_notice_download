import os
import json
import hashlib
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode

class CacheManager:
    """缓存管理类，负责缓存文件的创建、读取、保存和清理"""
    
    def __init__(self, cache_dir=None, stock_code='unknown', expire_days=7):
        self.cache_dir = cache_dir or 'cache'
        self.stock_code = stock_code
        self.expire_days = expire_days
        self.stock_cache_dir = os.path.join(self.cache_dir, stock_code)
        self._init_cache_dirs()
    
    def _init_cache_dirs(self):
        """初始化缓存目录"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        if not os.path.exists(self.stock_cache_dir):
            os.makedirs(self.stock_cache_dir)
    
    def _clean_url_params(self, url):
        """清理URL中的时间戳参数"""
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        # 移除时间戳相关的参数
        params_to_remove = ['cb', '_']
        for param in params_to_remove:
            if param in query_params:
                del query_params[param]
        
        # 重新构建URL（去除时间戳参数）
        clean_query = urlencode(query_params, doseq=True)
        clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{clean_query}"
        
        return clean_url, query_params
    
    def generate_cache_filename(self, url):
        """根据URL生成缓存文件名"""
        clean_url, query_params = self._clean_url_params(url)
        parsed_url = urlparse(url)
        
        # 判断请求类型
        if 'api/security/ann' in parsed_url.path:
            request_type = 'announcement_list'
            page_index = query_params.get('page_index', ['1'])[0]
            filename = f"{request_type}_page_{page_index}.json"
            return os.path.join(self.stock_cache_dir, filename)
        elif 'api/content/ann' in parsed_url.path:
            request_type = 'announcement_detail'
            art_code = query_params.get('art_code', ['unknown'])[0]
            filename = f"{request_type}_{art_code}.json"
            return os.path.join(self.stock_cache_dir, filename)
        else:
            request_type = 'other'
            filename = f"{request_type}_unknown.json"
            return os.path.join(self.cache_dir, filename)
    
    def is_cache_expired(self, cache_file):
        """检查缓存是否过期"""
        try:
            if not os.path.exists(cache_file):
                return True
            
            file_time = os.path.getctime(cache_file)
            file_datetime = datetime.fromtimestamp(file_time)
            current_datetime = datetime.now()
            
            time_diff = current_datetime - file_datetime
            
            if time_diff.days > self.expire_days:
                print(f"缓存已过期 ({time_diff.days}天 > {self.expire_days}天): {cache_file}")
                return True
            
            return False
        except Exception as e:
            print(f"检查缓存过期状态失败: {e}")
            return True
    
    def load_cache(self, cache_file):
        """从缓存文件加载数据"""
        try:
            if os.path.exists(cache_file):
                if self.is_cache_expired(cache_file):
                    try:
                        os.remove(cache_file)
                        print(f"已删除过期缓存: {cache_file}")
                    except Exception as e:
                        print(f"删除过期缓存失败: {e}")
                    return None
                
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                if isinstance(cache_data, dict) and 'data' in cache_data:
                    return cache_data['data']
                else:
                    return cache_data
        except Exception as e:
            print(f"加载缓存失败: {e}")
        return None
    
    def save_cache(self, cache_file, data, original_url=None):
        """保存数据到缓存文件"""
        try:
            cache_data = {
                'metadata': {
                    'cache_time': datetime.now().isoformat(),
                    'original_url': original_url,
                    'cache_file': cache_file,
                    'cache_expire_days': self.expire_days
                },
                'data': data
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            print(f"数据已缓存到: {cache_file}")
        except Exception as e:
            print(f"保存缓存失败: {e}")
    
    def clean_expired_cache(self):
        """清理过期的缓存文件"""
        try:
            if not os.path.exists(self.cache_dir):
                return
            
            cleaned_count = 0
            
            # 清理股票代码缓存目录
            if os.path.exists(self.stock_cache_dir):
                for filename in os.listdir(self.stock_cache_dir):
                    if filename.endswith('.json'):
                        cache_file = os.path.join(self.stock_cache_dir, filename)
                        if self.is_cache_expired(cache_file):
                            try:
                                os.remove(cache_file)
                                cleaned_count += 1
                                print(f"已清理过期缓存: {self.stock_code}/{filename}")
                            except Exception as e:
                                print(f"清理缓存文件失败 {self.stock_code}/{filename}: {e}")
            
            # 清理根目录下的其他缓存文件
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    cache_file = os.path.join(self.cache_dir, filename)
                    if self.is_cache_expired(cache_file):
                        try:
                            os.remove(cache_file)
                            cleaned_count += 1
                            print(f"已清理过期缓存: {filename}")
                        except Exception as e:
                            print(f"清理缓存文件失败 {filename}: {e}")
            
            if cleaned_count > 0:
                print(f"共清理了 {cleaned_count} 个过期缓存文件")
        except Exception as e:
            print(f"清理过期缓存失败: {e}")
    
    def get_cache_metadata(self, cache_file):
        """获取缓存文件的元数据信息"""
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                if isinstance(cache_data, dict) and 'metadata' in cache_data:
                    return cache_data['metadata']
                else:
                    return {
                        'cache_time': datetime.fromtimestamp(os.path.getctime(cache_file)).isoformat(),
                        'cache_file': cache_file,
                        'format': 'legacy'
                    }
        except Exception as e:
            print(f"获取缓存元数据失败: {e}")
        return None
    
    def list_cache_files(self):
        """列出所有缓存文件及其信息"""
        try:
            if not os.path.exists(self.cache_dir):
                print("缓存目录不存在")
                return []
            
            cache_files = []
            
            # 列出股票代码缓存目录中的文件
            if os.path.exists(self.stock_cache_dir):
                for filename in os.listdir(self.stock_cache_dir):
                    if filename.endswith('.json'):
                        cache_file = os.path.join(self.stock_cache_dir, filename)
                        metadata = self.get_cache_metadata(cache_file)
                        cache_files.append({
                            'stock_code': self.stock_code,
                            'filename': filename,
                            'full_path': cache_file,
                            'metadata': metadata
                        })
            
            # 列出根目录下的其他缓存文件
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    cache_file = os.path.join(self.cache_dir, filename)
                    metadata = self.get_cache_metadata(cache_file)
                    cache_files.append({
                        'stock_code': 'root',
                        'filename': filename,
                        'full_path': cache_file,
                        'metadata': metadata
                    })
            
            return cache_files
        except Exception as e:
            print(f"列出缓存文件失败: {e}")
            return [] 