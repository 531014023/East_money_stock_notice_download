import os
import re
import time
import subprocess

class PdfDownloader:
    """PDF下载管理类，负责PDF文件的下载和完整性检查"""
    
    def __init__(self):
        self.headers = [
            '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        ]
    
    def check_pdf_integrity(self, filename, expected_size_kb):
        """检查PDF文件完整性，比较实际文件大小与期望大小"""
        try:
            if not os.path.exists(filename):
                return False, "文件不存在"
            if expected_size_kb == 0:
                return True, "未提供期望大小，默认完整"
            file_size = os.path.getsize(filename)
            file_size_kb = round(file_size / 1000)
            
            # 两者相差超过10kb并且实际大小比期望大小小的时候就是文件大小不符
            if abs(file_size_kb - expected_size_kb) > 10 and file_size_kb < expected_size_kb:
                return False, f"文件大小不符 (实际:{file_size_kb}KB, 期望:{expected_size_kb}KB)"
            
            return True, f"文件完整 (大小:{file_size_kb}KB)"
        except Exception as e:
            return False, f"检查文件完整性失败: {e}"
    
    def download_pdf(self, url, filename, attach_size, max_retries=3):
        """使用curl命令下载PDF文件，下载后用文件大小和attach_size对比判断是否完整"""
        curl_cmd = [
            'curl',
            '-L',  # 跟随重定向
            '-o', filename,
        ] + self.headers + [url]
        
        for attempt in range(1, max_retries + 1):
            try:
                result = subprocess.run(curl_cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    # 使用完整性检查函数
                    is_complete, message = self.check_pdf_integrity(filename, attach_size)
                    if is_complete:
                        print(f"Successfully downloaded: {filename} ({message})")
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
    
    def build_pdf_filename(self, stock_code, short_name, notice_title, notice_date):
        """构建PDF文件名"""
        # 去除特殊字符，只保留中文、数字、字母
        notice_title = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', notice_title)
        
        # 提取年月日数字，格式：2018-01-18 00:00:00 -> 20180118
        date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', notice_date)
        if date_match:
            notice_date = date_match.group(1) + date_match.group(2) + date_match.group(3)
        else:
            notice_date = ''
        
        filename_prefix = ''
        if stock_code and stock_code not in notice_title:
            filename_prefix += stock_code
        if short_name and short_name not in notice_title:
            filename_prefix += short_name
        
        return f"{notice_date}_{filename_prefix}{notice_title}.pdf"
    
    def should_download_pdf(self, filename, attach_size):
        """检查是否需要下载PDF文件"""
        if os.path.exists(filename):
            is_complete, message = self.check_pdf_integrity(filename, attach_size)
            if is_complete:
                print(f"PDF文件已存在且完整，跳过下载: {os.path.basename(filename)} ({message})")
                return False
            else:
                print(f"PDF文件存在但不完整: {os.path.basename(filename)} ({message})，将重新下载")
                return True
        
        return True 