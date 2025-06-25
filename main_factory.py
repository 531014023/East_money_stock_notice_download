#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
东方财富股票公告下载器 - 工厂模式版本
"""

from stock_crawler import CrawlerFactory

def main():
    """主函数 - 使用工厂模式"""
    try:
        # 使用工厂创建爬虫实例，从配置文件读取目录设置
        factory = CrawlerFactory('config.json')
        crawler = factory.create_crawler()
        
        # 运行爬虫
        print(f"开始爬取股票 {factory.config_manager.stock_code} 的公告...")
        print(f"PDF文件将保存到: {factory.download_dir}/")
        print(f"缓存文件将保存到: {factory.cache_dir}/")
        crawler.run()
        print("爬取完成！")
        
    except Exception as e:
        print(f"程序运行出错: {e}")
        raise

if __name__ == "__main__":
    main() 