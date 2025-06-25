#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
东方财富股票公告下载器 - 安装配置
"""

from setuptools import setup, find_packages

with open("readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="stock-crawler",
    version="2.0.0",
    author="Stock Crawler Team",
    author_email="example@example.com",
    description="一个用于爬取东方财富网站股票公告的Python爬虫工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/stock-crawler",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "stock-crawler=stock_crawler.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 