# 东方财富股票公告下载器

一个用于爬取东方财富网站股票公告的Python爬虫工具，支持自动下载公告PDF并分类存储。

## 功能特点

- 🔍 **智能爬取**: 自动爬取指定股票的公告列表
- 📄 **PDF下载**: 自动下载公告PDF文件
- 📁 **分类存储**: 按公告类型自动分类存储
- 💾 **缓存机制**: 支持API请求缓存，避免重复请求
- ⏰ **过期清理**: 自动清理过期缓存文件
- 🔒 **完整性检查**: 下载前检查PDF文件完整性
- 🛡️ **错误处理**: 完善的错误处理和重试机制
- 🏗️ **模块化设计**: 面向对象架构，易于扩展和维护

## 项目结构

### 模块化版本 (推荐)

```
East_money_stock_notice_download/
├── stock_crawler/                    # 主模块
│   ├── __init__.py                   # 模块初始化
│   ├── cli.py                        # 命令行接口
│   ├── factory.py                    # 工厂类
│   ├── core/                         # 核心模块
│   │   ├── __init__.py
│   │   ├── config_manager.py        # 配置管理类
│   │   └── cache_manager.py         # 缓存管理类
│   ├── downloaders/                  # 下载器模块
│   │   ├── __init__.py
│   │   ├── http_client.py           # HTTP请求管理类
│   │   └── pdf_downloader.py        # PDF下载管理类
│   ├── processors/                   # 处理器模块
│   │   ├── __init__.py
│   │   ├── announcement_processor.py # 公告处理类
│   │   └── stock_crawler.py         # 爬虫主类
│   └── utils/                        # 工具模块
│       ├── __init__.py
│       └── utils.py                  # 工具类
├── main_factory.py                   # 工厂模式主程序
├── main_oop.py                       # 面向对象主程序
├── setup.py                          # 安装配置
├── config.json                       # 配置文件
├── cache/                            # 缓存目录
│   └── [股票代码]/                   # 按股票代码分类的缓存
├── [股票名称]pdf/                    # PDF存储目录
│   └── [公告类型]/                   # 按公告类型分类
└── readme.md                         # 说明文档
```

### 面向过程版本

```
East_money_stock_notice_download/
├── main.py                           # 主程序入口 (原始版本)
├── test.py                           # 测试文件
├── config.json                       # 配置文件
├── cache/                            # 缓存目录
├── [股票名称]pdf/                    # PDF存储目录
└── readme.md                         # 说明文档
```

## 安装依赖

```bash
pip install requests
```

## 配置说明

在 `config.json` 文件中配置以下参数：

```json
{
    "stock_code": "600519",
    "f_node": "0",
    "s_node": "0",
    "cache_expire_days": 7
}
```

### 配置参数说明

- `stock_code`: 股票代码 (必填)
- `f_node`: 公告大类 (可选，默认为"0")
- `s_node`: 公告小类 (可选，默认为"0")
- `cache_expire_days`: 缓存过期天数 (可选，默认为7天)

## 使用方法

### 1. 命令行方式 (推荐)

```bash
# 使用默认配置文件运行
python -m stock_crawler.cli

# 使用自定义配置文件
python -m stock_crawler.cli -c custom.json

# 清理过期缓存
python -m stock_crawler.cli --clean-cache

# 列出缓存文件
python -m stock_crawler.cli --list-cache

# 显示帮助信息
python -m stock_crawler.cli --help
```

### 2. 工厂模式

```bash
python main_factory.py
```

### 3. 面向对象模式

```bash
python main_oop.py
```

### 4. 面向过程版本

```bash
python main.py
```

## 模块架构说明

### 核心模块 (core)
- **ConfigManager**: 配置管理，负责读取和管理配置文件
- **CacheManager**: 缓存管理，处理API请求缓存和过期清理

### 下载器模块 (downloaders)
- **HttpClient**: HTTP请求管理，处理JSONP响应和缓存集成
- **PdfDownloader**: PDF下载管理，负责文件下载和完整性检查

### 处理器模块 (processors)
- **AnnouncementProcessor**: 公告处理，协调单个公告的下载逻辑
- **StockCrawler**: 爬虫主控制器，协调各个组件完成爬取任务

### 工具模块 (utils)
- **Utils**: 通用工具函数，提供文件操作和格式化功能

### 工厂模块 (factory)
- **CrawlerFactory**: 工厂类，负责创建和管理爬虫实例，实现依赖注入

### 命令行接口 (cli)
- 提供命令行界面，支持多种操作选项

## 设计模式

### 1. 工厂模式
- 使用 `CrawlerFactory` 统一管理对象创建
- 实现懒加载和单例模式
- 简化对象依赖关系

### 2. 依赖注入
- 通过构造函数注入依赖
- 降低组件间耦合度
- 便于单元测试

### 3. 单一职责原则
- 每个类只负责一个特定功能
- 提高代码可维护性
- 便于功能扩展

## 缓存机制

### 缓存策略
- 基于URL的缓存机制
- 自动去除时间戳参数，避免缓存失效
- 按股票代码分类存储
- 支持配置过期天数

### 缓存文件命名
- 公告列表: `announcement_list_page_[页码].json`
- 公告详情: `announcement_detail_[art_code].json`
- 其他请求: `other_unknown.json`

### 缓存清理
- 启动时自动清理过期缓存
- 基于文件创建时间判断过期
- 支持手动清理功能

## PDF下载

### 文件命名规则
格式: `[日期]_[股票代码][股票简称][公告标题].pdf`

示例: `20240118_600519贵州茅台关于公司治理的公告.pdf`

### 完整性检查
- 下载前检查文件是否存在且完整
- 比较实际文件大小与期望大小
- 支持自动重试下载

### 分类存储
- 按公告类型自动分类
- 目录结构: `[股票简称]pdf/[公告类型]/`

## 错误处理

### 网络错误
- 自动重试机制
- 详细的错误日志
- 优雅的错误处理

### 文件错误
- 文件完整性检查
- 损坏文件自动重新下载
- 文件权限检查

### 配置错误
- 配置文件格式验证
- 默认值回退机制
- 友好的错误提示

## 开发指南

### 扩展新功能
1. 在相应的模块目录中创建新的类文件
2. 在模块的 `__init__.py` 中导出新类
3. 在主模块的 `__init__.py` 中添加导入
4. 在工厂类中添加相应的创建方法

### 添加新的下载器
```python
# 在 downloaders/ 目录中创建新文件
class NewDownloader:
    def __init__(self, dependencies):
        pass
    
    def download(self, url, filename):
        pass

# 在 downloaders/__init__.py 中添加
from .new_downloader import NewDownloader
__all__ = ['HttpClient', 'PdfDownloader', 'NewDownloader']
```

### 添加新的处理器
```python
# 在 processors/ 目录中创建新文件
class NewProcessor:
    def __init__(self, dependencies):
        pass
    
    def process(self, data):
        pass

# 在 processors/__init__.py 中添加
from .new_processor import NewProcessor
__all__ = ['AnnouncementProcessor', 'StockCrawler', 'NewProcessor']
```

## 测试

### 运行测试
```bash
# 安装测试依赖
pip install pytest pytest-cov

# 运行测试
pytest tests/

# 生成覆盖率报告
pytest --cov=stock_crawler tests/
```

## 部署

### 作为Python包安装
```bash
# 开发模式安装
pip install -e .

# 正式安装
pip install .
```

### 创建可执行文件
```bash
# 使用PyInstaller
pip install pyinstaller
pyinstaller --onefile main_factory.py
```

## 技术支持

### 常见问题

1. **下载失败**
   - 检查网络连接
   - 确认股票代码正确
   - 查看错误日志

2. **缓存问题**
   - 清理缓存目录
   - 检查缓存配置
   - 重新运行程序

3. **PDF文件损坏**
   - 程序会自动重试下载
   - 检查磁盘空间
   - 确认文件权限

### 日志说明

程序会输出详细的运行日志，包括：
- 缓存使用情况
- 下载进度
- 错误信息
- 文件操作状态

## 许可证

本项目仅供学习和研究使用，请遵守相关网站的使用条款。

## 更新日志

### v2.0.0 (模块化重构)
- 重构为模块化架构
- 实现工厂模式和依赖注入
- 添加命令行接口
- 支持作为Python包安装
- 增强缓存管理功能
- 优化错误处理机制

### v1.0.0 (原始版本)
- 基础爬虫功能
- PDF下载和分类存储
- 简单的缓存机制
