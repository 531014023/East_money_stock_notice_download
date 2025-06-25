import time

class StockCrawler:
    """爬虫主类，负责协调各个组件完成爬虫任务"""
    
    def __init__(self, config_manager, cache_manager, http_client, announcement_processor):
        self.config_manager = config_manager
        self.cache_manager = cache_manager
        self.http_client = http_client
        self.announcement_processor = announcement_processor
    
    def run(self):
        """运行爬虫"""
        # 程序启动时清理过期缓存
        print(f"缓存过期天数设置: {self.config_manager.cache_expire_days}天")
        self.cache_manager.clean_expired_cache()
        
        base_url = "https://np-anotice-stock.eastmoney.com/api/security/ann"
        stock_code = self.config_manager.stock_code
        page_size = 50
        page_index = 1
        total_hits = 0
        f_node = self.config_manager.f_node
        s_node = self.config_manager.s_node
        
        while True:
            timestamp = self.http_client.generate_timestamp()
            cb_param = f"jQuery1123{timestamp[:10]}_{timestamp}"
            
            params = {
                'cb': cb_param,
                'sr': '-1',
                'page_size': page_size,
                'page_index': page_index,
                'ann_type': 'A',
                'client_source': 'web',
                'stock_list': stock_code,
                'f_node': f_node,
                's_node': s_node,
                '_': timestamp
            }
            
            url = f"{base_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
            print(f"Fetching page {page_index}...")
            
            data = self.http_client.get_jsonp_response(url)
            if not data or data.get('success') != 1:
                print("Failed to get announcement list")
                break
                
            total_hits = data.get('data', {}).get('total_hits', 0)
            announcements = data.get('data', {}).get('list', [])
            
            if not announcements:
                print("No more announcements")
                break
                
            for item in announcements:
                self.announcement_processor.process_announcement(item)
                time.sleep(1) # 添加延迟避免被封 
            
            # 检查是否还有下一页
            if page_index * page_size >= total_hits:
                break
                
            page_index += 1