import os
import re
import json
import time
import requests
from urllib.parse import urlparse, parse_qs, urlencode
import subprocess
from datetime import datetime

# 新增：读取配置文件
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 创建缓存目录
CACHE_DIR = 'cache'
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# 获取配置信息
CACHE_EXPIRE_DAYS = config.get('cache_expire_days', 7)
STOCK_CODE = config.get('stock_code', 'unknown')

# 创建股票代码缓存目录
STOCK_CACHE_DIR = os.path.join(CACHE_DIR, STOCK_CODE)
if not os.path.exists(STOCK_CACHE_DIR):
    os.makedirs(STOCK_CACHE_DIR)

def generate_timestamp():
    """生成时间戳"""
    return str(int(time.time() * 1000))

def is_cache_expired(cache_file):
    """检查缓存是否过期"""
    try:
        if not os.path.exists(cache_file):
            return True
        
        # 获取文件创建时间
        file_time = os.path.getctime(cache_file)
        file_datetime = datetime.fromtimestamp(file_time)
        current_datetime = datetime.now()
        
        # 计算时间差
        time_diff = current_datetime - file_datetime
        
        # 检查是否超过配置的过期天数
        if time_diff.days > CACHE_EXPIRE_DAYS:
            print(f"缓存已过期 ({time_diff.days}天 > {CACHE_EXPIRE_DAYS}天): {cache_file}")
            return True
        
        return False
    except Exception as e:
        print(f"检查缓存过期状态失败: {e}")
        return True

def clean_expired_cache():
    """清理过期的缓存文件"""
    try:
        if not os.path.exists(CACHE_DIR):
            return
        
        cleaned_count = 0
        
        # 清理股票代码缓存目录
        if os.path.exists(STOCK_CACHE_DIR):
            for filename in os.listdir(STOCK_CACHE_DIR):
                if filename.endswith('.json'):
                    cache_file = os.path.join(STOCK_CACHE_DIR, filename)
                    if is_cache_expired(cache_file):
                        try:
                            os.remove(cache_file)
                            cleaned_count += 1
                            print(f"已清理过期缓存: {STOCK_CODE}/{filename}")
                        except Exception as e:
                            print(f"清理缓存文件失败 {STOCK_CODE}/{filename}: {e}")
        
        # 清理根目录下的其他缓存文件
        for filename in os.listdir(CACHE_DIR):
            if filename.endswith('.json'):
                cache_file = os.path.join(CACHE_DIR, filename)
                if is_cache_expired(cache_file):
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

def clean_url_params(url):
    """清理URL中的时间戳参数，返回清理后的URL"""
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

def generate_cache_filename(url):
    """根据URL生成人类可识别的缓存文件名"""
    # 清理URL参数
    clean_url, query_params = clean_url_params(url)
    parsed_url = urlparse(url)
    
    # 判断请求类型
    if 'api/security/ann' in parsed_url.path:
        request_type = 'announcement_list'  # 公告列表
        page_index = query_params.get('page_index', ['1'])[0]
        filename = f"{request_type}_page_{page_index}.json"
        return os.path.join(STOCK_CACHE_DIR, filename)
    elif 'api/content/ann' in parsed_url.path:
        request_type = 'announcement_detail'  # 公告详情
        art_code = query_params.get('art_code', ['unknown'])[0]
        filename = f"{request_type}_{art_code}.json"
        return os.path.join(STOCK_CACHE_DIR, filename)
    else:
        request_type = 'other'
        filename = f"{request_type}_unknown.json"
        return os.path.join(CACHE_DIR, filename)

def load_cache(cache_file):
    """从缓存文件加载数据，检查是否过期"""
    try:
        if os.path.exists(cache_file):
            # 检查缓存是否过期
            if is_cache_expired(cache_file):
                # 缓存过期，删除文件
                try:
                    os.remove(cache_file)
                    print(f"已删除过期缓存: {cache_file}")
                except Exception as e:
                    print(f"删除过期缓存失败: {e}")
                return None
            
            # 缓存未过期，加载数据
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                
            # 处理新旧缓存格式
            if isinstance(cache_data, dict) and 'data' in cache_data:
                # 新格式：包含元数据
                return cache_data['data']
            else:
                # 旧格式：直接是数据
                return cache_data
    except Exception as e:
        print(f"加载缓存失败: {e}")
    return None

def save_cache(cache_file, data, original_url=None):
    """保存数据到缓存文件，包含元数据信息"""
    try:
        # 准备缓存数据，包含元数据
        cache_data = {
            'metadata': {
                'cache_time': datetime.now().isoformat(),
                'original_url': original_url,
                'cache_file': cache_file,
                'cache_expire_days': CACHE_EXPIRE_DAYS
            },
            'data': data
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        print(f"数据已缓存到: {cache_file}")
    except Exception as e:
        print(f"保存缓存失败: {e}")

def get_jsonp_response(url):
    """获取JSONP响应并解析为JSON，支持缓存"""
    # 生成缓存文件名
    cache_file = generate_cache_filename(url)
    
    # 检查缓存是否存在
    cached_data = load_cache(cache_file)
    if cached_data:
        print(f"使用缓存数据: {os.path.basename(cache_file)}")
        return cached_data
    
    # 缓存不存在，发起网络请求
    print(f"发起网络请求: {os.path.basename(cache_file)}")
    try:
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0'
        })
        response.raise_for_status()
        
        # 使用正则表达式提取JSON部分
        json_str = re.search(r'jQuery\d+_\d+\((.*)\)', response.text).group(1)
        data = json.loads(json_str)
        
        # 保存到缓存，传递原始URL
        save_cache(cache_file, data, original_url=url)
        
        return data
    except Exception as e:
        print(f"Error fetching or parsing JSONP response: {e}")
        return None

def check_pdf_integrity(filename, expected_size_kb):
    """检查PDF文件完整性，比较实际文件大小与期望大小"""
    try:
        if not os.path.exists(filename):
            return False, "文件不存在"
        
        file_size = os.path.getsize(filename)
        file_size_kb = round(file_size / 1000)
        
        # 两者相差超过10kb并且实际大小比期望大小小的时候就是文件大小不符
        if abs(file_size_kb - expected_size_kb) > 10 and file_size_kb < expected_size_kb:
            return False, f"文件大小不符 (实际:{file_size_kb}KB, 期望:{expected_size_kb}KB)"
        
        return True, f"文件完整 (大小:{file_size_kb}KB)"
    except Exception as e:
        return False, f"检查文件完整性失败: {e}"

def download_pdf(url, filename, attach_size, max_retries=3):
    """使用curl命令下载PDF文件，下载后用文件大小和attach_size对比判断是否完整"""
    headers = [
        '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    ]
    curl_cmd = [
        'curl',
        '-L',  # 跟随重定向
        '-o', filename,
    ] + headers + [url]
    
    for attempt in range(1, max_retries + 1):
        try:
            result = subprocess.run(curl_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                # 使用完整性检查函数
                is_complete, message = check_pdf_integrity(filename, attach_size)
                if is_complete:
                    print(f"Successfully downloaded: {filename}")
                    break
                else:
                    print(f"文件不完整: {message}，准备重试({attempt}/{max_retries})：{filename}")
                    time.sleep(1)
                    continue
            else:
                print(f"下载失败，错误信息：{result.stderr}.url:{url},filename:{filename}，准备重试({attempt}/{max_retries})")
        except Exception as e:
            print(f"Error downloading PDF with curl: {e}，准备重试({attempt}/{max_retries})")
        time.sleep(1)
    else:
        print(f"多次重试后仍未成功下载完整PDF：{filename}")

def process_announcement(item):
    """处理单个公告"""
    art_code = item.get('art_code')
    if not art_code:
        print(f"没有获取到art_code，无法进入下一步")
        return
    timestamp = generate_timestamp()
    cb_param = f"jQuery1123{timestamp[:10]}_{timestamp}"
    
    url = f"https://np-cnotice-stock.eastmoney.com/api/content/ann?cb={cb_param}&art_code={art_code}&client_source=web&page_index=1&_={timestamp}"
    
    data = get_jsonp_response(url)
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
    # 去除特殊字符，只保留中文、数字、字母
    notice_title = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', notice_title)
    notice_date = data.get('data', {}).get('notice_date', '')
    # 提取年月日数字，格式：2018-01-18 00:00:00 -> 20180118
    date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', notice_date)
    if date_match:
        notice_date = date_match.group(1) + date_match.group(2) + date_match.group(3)
    else:
        notice_date = ''

    # 创建PDF文件夹
    column_name = item.get('columns')[0].get('column_name')
    pdf_folder = f'{short_name}pdf/{column_name}'
    if not os.path.exists(pdf_folder):
        os.makedirs(pdf_folder)
    
    filename_prefix = ''
    if stock_code and stock_code not in notice_title:
        filename_prefix += stock_code
    if short_name and short_name not in notice_title:
        filename_prefix += short_name
    raw_filename = f"{notice_date}_{filename_prefix}{notice_title}.pdf"
    filename = f"{pdf_folder}/{raw_filename}"
    
    # 检查PDF文件是否已存在且完整
    if os.path.exists(filename):
        is_complete, message = check_pdf_integrity(filename, attach_size)
        if is_complete:
            print(f"PDF文件已存在且完整，跳过下载: {os.path.basename(filename)} ({message})")
            return
        else:
            print(f"PDF文件存在但不完整: {os.path.basename(filename)} ({message})，将重新下载")
    
    # 文件不存在或不完整，开始下载
    print(f"开始下载PDF: {os.path.basename(filename)}")
    download_pdf(attach_url, filename, attach_size)

def get_cache_metadata(cache_file):
    """获取缓存文件的元数据信息"""
    try:
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                
            if isinstance(cache_data, dict) and 'metadata' in cache_data:
                return cache_data['metadata']
            else:
                # 旧格式缓存，返回基本信息
                return {
                    'cache_time': datetime.fromtimestamp(os.path.getctime(cache_file)).isoformat(),
                    'cache_file': cache_file,
                    'format': 'legacy'
                }
    except Exception as e:
        print(f"获取缓存元数据失败: {e}")
    return None

def list_cache_files():
    """列出所有缓存文件及其信息"""
    try:
        if not os.path.exists(CACHE_DIR):
            print("缓存目录不存在")
            return
        
        cache_files = []
        
        # 列出股票代码缓存目录中的文件
        if os.path.exists(STOCK_CACHE_DIR):
            for filename in os.listdir(STOCK_CACHE_DIR):
                if filename.endswith('.json'):
                    cache_file = os.path.join(STOCK_CACHE_DIR, filename)
                    metadata = get_cache_metadata(cache_file)
                    cache_files.append({
                        'stock_code': STOCK_CODE,
                        'filename': filename,
                        'full_path': cache_file,
                        'metadata': metadata
                    })
        
        # 列出根目录下的其他缓存文件
        for filename in os.listdir(CACHE_DIR):
            if filename.endswith('.json'):
                cache_file = os.path.join(CACHE_DIR, filename)
                metadata = get_cache_metadata(cache_file)
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

def main():
    # 程序启动时清理过期缓存
    print(f"缓存过期天数设置: {CACHE_EXPIRE_DAYS}天")
    clean_expired_cache()
    
    base_url = "https://np-anotice-stock.eastmoney.com/api/security/ann"
    stock_code = config.get('stock_code', '601225')
    page_size = 50
    page_index = 1
    total_hits = 0
    f_node = config.get('f_node', '1')
    s_node = config.get('s_node', '1')
    
    while True:
        timestamp = generate_timestamp()
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
        
        data = get_jsonp_response(url)
        if not data or data.get('success') != 1:
            print("Failed to get announcement list")
            break
            
        total_hits = data.get('data', {}).get('total_hits', 0)
        announcements = data.get('data', {}).get('list', [])
        
        if not announcements:
            print("No more announcements")
            break
            
        for item in announcements:
            process_announcement(item)
            time.sleep(1)
        
        # 检查是否还有下一页
        if page_index * page_size >= total_hits:
            break
            
        page_index += 1
        time.sleep(2)  # 添加延迟避免被封

if __name__ == "__main__":
    main()