#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
东方财富股票公告下载器 - 面向对象版本
"""

from stock_crawler import (
    ConfigManager,
    CacheManager,
    HttpClient,
    PdfDownloader,
    AnnouncementProcessor,
    StockCrawler
)

def main():
    """主函数"""
    try:
        # 初始化配置管理器
        config_manager = ConfigManager('config.json')
        
        # 初始化缓存管理器
        cache_manager = CacheManager(
            cache_dir='cache',
            stock_code=config_manager.stock_code,
            expire_days=config_manager.cache_expire_days
        )
        
        # 初始化HTTP客户端
        http_client = HttpClient(cache_manager)
        
        # 初始化PDF下载器
        pdf_downloader = PdfDownloader()
        
        # 初始化公告处理器
        announcement_processor = AnnouncementProcessor(http_client, pdf_downloader)
        
        # 初始化爬虫
        crawler = StockCrawler(
            config_manager=config_manager,
            cache_manager=cache_manager,
            http_client=http_client,
            announcement_processor=announcement_processor
        )
        
        # 运行爬虫
        print(f"开始爬取股票 {config_manager.stock_code} 的公告...")
        crawler.run()
        print("爬取完成！")
        
    except Exception as e:
        print(f"程序运行出错: {e}")
        raise

if __name__ == "__main__":
    main() 