"""
工厂模块 - 用于创建和管理爬虫实例
"""

from .core import ConfigManager, CacheManager
from .downloaders import HttpClient, PdfDownloader
from .processors import AnnouncementProcessor, StockCrawler

class CrawlerFactory:
    """爬虫工厂类，负责创建和管理爬虫实例"""
    
    def __init__(self, config_file='config.json', download_dir=None, cache_dir=None):
        self.config_file = config_file
        self.config_manager = ConfigManager(config_file)
        self.download_dir = download_dir or self.config_manager.download_dir
        self.cache_dir = cache_dir or self.config_manager.cache_dir
        self._cache_manager = None
        self._http_client = None
        self._pdf_downloader = None
        self._announcement_processor = None
        self._stock_crawler = None
    
    @property
    def cache_manager(self):
        """获取缓存管理器实例"""
        if self._cache_manager is None:
            self._cache_manager = CacheManager(
                cache_dir=self.cache_dir,
                stock_code=self.config_manager.stock_code,
                expire_days=self.config_manager.cache_expire_days
            )
        return self._cache_manager
    
    @property
    def http_client(self):
        """获取HTTP客户端实例"""
        if self._http_client is None:
            self._http_client = HttpClient(self.cache_manager)
        return self._http_client
    
    @property
    def pdf_downloader(self):
        """获取PDF下载器实例"""
        if self._pdf_downloader is None:
            self._pdf_downloader = PdfDownloader()
        return self._pdf_downloader
    
    @property
    def announcement_processor(self):
        """获取公告处理器实例"""
        if self._announcement_processor is None:
            self._announcement_processor = AnnouncementProcessor(
                self.http_client, 
                self.pdf_downloader,
                download_dir=self.download_dir
            )
        return self._announcement_processor
    
    @property
    def stock_crawler(self):
        """获取股票爬虫实例"""
        if self._stock_crawler is None:
            self._stock_crawler = StockCrawler(
                config_manager=self.config_manager,
                cache_manager=self.cache_manager,
                http_client=self.http_client,
                announcement_processor=self.announcement_processor
            )
        return self._stock_crawler
    
    def create_crawler(self):
        """创建完整的爬虫实例"""
        return self.stock_crawler
    
    def reset(self):
        """重置所有实例，用于重新初始化"""
        self._cache_manager = None
        self._http_client = None
        self._pdf_downloader = None
        self._announcement_processor = None
        self._stock_crawler = None 