import os
import re
import json
import time
import requests
from urllib.parse import quote
import sys
import subprocess

# 新增：读取配置文件
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

def generate_timestamp():
    """生成时间戳"""
    return str(int(time.time() * 1000))

def get_jsonp_response(url):
    """获取JSONP响应并解析为JSON"""
    try:
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0'
        })
        response.raise_for_status()
        
        # 使用正则表达式提取JSON部分
        json_str = re.search(r'jQuery\d+_\d+\((.*)\)', response.text).group(1)
        return json.loads(json_str)
    except Exception as e:
        print(f"Error fetching or parsing JSONP response: {e}")
        return None

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
                if os.path.exists(filename):
                    file_size = os.path.getsize(filename)
                    file_size_kb = round(file_size / 1000)
                    print(f"实际文件大小({file_size_kb}KB)与attach_size({attach_size}KB)")
                    # 两者相差超过10kb并且实际大小比attach_size小的时候就是文件大小不符
                    if abs(file_size_kb - attach_size) > 10 and file_size_kb < attach_size:
                        print(f"实际文件大小({file_size_kb}KB)与attach_size({attach_size}KB)不符，准备重试({attempt}/{max_retries})：{filename}")
                        time.sleep(1)
                        continue
                print(f"Successfully downloaded: {filename}")
                break
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
    raw_filename = f"{filename_prefix}{notice_title}{notice_date}.pdf"
    filename = f"{pdf_folder}/{raw_filename}"
    
    download_pdf(attach_url, filename, attach_size)

def main():
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