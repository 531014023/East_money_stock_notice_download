import os
import time

class AnnouncementProcessor:
    """公告处理类，负责处理单个公告的下载逻辑"""
    
    def __init__(self, http_client, pdf_downloader, download_dir='downloads', config_manager=None):
        self.http_client = http_client
        self.pdf_downloader = pdf_downloader
        self.download_dir = download_dir
        self.config_manager = config_manager
    
    def process_announcement(self, item):
        """处理单个公告"""
        art_code = item.get('art_code')
        if not art_code:
            print(f"没有获取到art_code，无法进入下一步")
            return
        
        timestamp = self.http_client.generate_timestamp()
        cb_param = f"jQuery1123{timestamp[:10]}_{timestamp}"
        
        url = f"https://np-cnotice-stock.eastmoney.com/api/content/ann?cb={cb_param}&art_code={art_code}&client_source=web&page_index=1&_={timestamp}"
        
        data = self.http_client.get_jsonp_response(url)
        if not data or data.get('success') != 1:
            print(f"Failed to get content for art_code: {art_code}")
            return
        
        attach_url = data.get('data', {}).get('attach_url')
        if not attach_url:
            print(f"No PDF attachment found for art_code: {art_code}")
            return
        
        # 构建文件名
        security = data.get('data', {}).get('security', {})[0]
        stock_code = security.get('stock', '')
        short_name = security.get('short_name', '')
        attach_size = int(data.get('data', {}).get('attach_size', ''))
        notice_title = data.get('data', {}).get('notice_title', '')
        notice_date = data.get('data', {}).get('notice_date', '')
        
        # 新增：根据关键词过滤公告标题
        if self.config_manager:
            # 排除关键词优先
            exclude_keywords = self.config_manager.notice_title_exclude_keywords
            if exclude_keywords:
                if any(kw in notice_title for kw in exclude_keywords):
                    print(f"公告标题命中排除关键词，跳过: {notice_title}")
                    return
            # 包含关键词
            keywords = self.config_manager.notice_title_keywords
            if keywords:
                if not any(kw in notice_title for kw in keywords):
                    print(f"公告标题未匹配关键词，跳过: {notice_title}")
                    return
        
        # 创建统一的下载文件夹结构
        column_name = item.get('columns')[0].get('column_name')
        pdf_folder = os.path.join(self.download_dir, short_name, column_name)
        if not os.path.exists(pdf_folder):
            os.makedirs(pdf_folder)
        
        # 构建PDF文件名
        raw_filename = self.pdf_downloader.build_pdf_filename(
            stock_code, short_name, notice_title, notice_date
        )
        filename = os.path.join(pdf_folder, raw_filename)
        
        # 检查是否需要下载PDF
        if self.pdf_downloader.should_download_pdf(filename, attach_size):
            print(f"开始下载PDF: {os.path.basename(filename)}")
            self.pdf_downloader.download_pdf(attach_url, filename, attach_size) 
            time.sleep(1)