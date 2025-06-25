#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令行接口模块
"""

import argparse
import sys
from .factory import CrawlerFactory

def main():
    """命令行主函数"""
    parser = argparse.ArgumentParser(
        description="东方财富股票公告下载器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s                    # 使用默认配置文件
  %(prog)s -c custom.json     # 使用自定义配置文件
  %(prog)s -d custom_downloads # 使用自定义下载目录
  %(prog)s --cache-dir custom_cache # 使用自定义缓存目录
  %(prog)s --version          # 显示版本信息
        """
    )
    
    parser.add_argument(
        '-c', '--config',
        default='config.json',
        help='配置文件路径 (默认: config.json)'
    )
    
    parser.add_argument(
        '-d', '--download-dir',
        help='下载目录路径 (默认从配置文件读取)'
    )
    
    parser.add_argument(
        '--cache-dir',
        help='缓存目录路径 (默认从配置文件读取)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 2.0.0'
    )
    
    parser.add_argument(
        '--clean-cache',
        action='store_true',
        help='清理过期缓存'
    )
    
    parser.add_argument(
        '--list-cache',
        action='store_true',
        help='列出缓存文件'
    )
    
    args = parser.parse_args()
    
    try:
        # 创建工厂实例，支持命令行参数覆盖配置文件
        factory = CrawlerFactory(
            config_file=args.config,
            download_dir=args.download_dir,
            cache_dir=args.cache_dir
        )
        
        # 处理特殊命令
        if args.clean_cache:
            print("清理过期缓存...")
            factory.cache_manager.clean_expired_cache()
            print("缓存清理完成！")
            return
        
        if args.list_cache:
            print("列出缓存文件...")
            cache_files = factory.cache_manager.list_cache_files()
            if cache_files:
                for cache_file in cache_files:
                    print(f"股票代码: {cache_file['stock_code']}")
                    print(f"文件名: {cache_file['filename']}")
                    print(f"路径: {cache_file['full_path']}")
                    if cache_file['metadata']:
                        print(f"缓存时间: {cache_file['metadata'].get('cache_time', '未知')}")
                    print("-" * 50)
            else:
                print("没有找到缓存文件")
            return
        
        # 正常运行爬虫
        crawler = factory.create_crawler()
        print(f"开始爬取股票 {factory.config_manager.stock_code} 的公告...")
        print(f"PDF文件将保存到: {factory.download_dir}/")
        print(f"缓存文件将保存到: {factory.cache_dir}/")
        crawler.run()
        print("爬取完成！")
        
    except FileNotFoundError:
        print(f"错误: 配置文件 '{args.config}' 不存在")
        sys.exit(1)
    except Exception as e:
        print(f"程序运行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 