import os
import time

class AnnouncementProcessor:
    """公告处理类，负责处理单个公告的下载逻辑"""
    
    def __init__(self, http_client, pdf_downloader):
        self.http_client = http_client
        self.pdf_downloader = pdf_downloader
    
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
        
        # 创建PDF文件夹
        column_name = item.get('columns')[0].get('column_name')
        pdf_folder = f'{short_name}pdf/{column_name}'
        if not os.path.exists(pdf_folder):
            os.makedirs(pdf_folder)
        
        # 构建PDF文件名
        raw_filename = self.pdf_downloader.build_pdf_filename(
            stock_code, short_name, notice_title, notice_date
        )
        filename = f"{pdf_folder}/{raw_filename}"
        
        # 检查是否需要下载PDF
        if self.pdf_downloader.should_download_pdf(filename, attach_size):
            print(f"开始下载PDF: {os.path.basename(filename)}")
            self.pdf_downloader.download_pdf(attach_url, filename, attach_size) 