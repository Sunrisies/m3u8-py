import requests
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import warnings
from urllib.parse import urljoin
from tqdm import tqdm
import multiprocessing
import signal
import sys
import threading

class M3U8Downloader:
    def __init__(self, url, num_threads=None):
        self.url = url
        self.num_threads = num_threads if num_threads is not None else multiprocessing.cpu_count() * 2
        self.session = requests.Session()
        self.session.verify = False
        warnings.filterwarnings('ignore', category=InsecureRequestWarning)
        self.stop_flag = False
        self.lock = threading.Lock()
        
        # 设置请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://europe.olemovienews.com/'
        })

        # 注册信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        """处理中断信号"""
        print("\n收到中断信号，正在停止下载...")
        self.stop_flag = True

    def parse_m3u8(self):
        """解析m3u8文件内容"""
        try:
            response = self.session.get(self.url)
            response.raise_for_status()
            
            # 获取基础URL
            base_url = self.url.rsplit('/', 1)[0] + '/'
            
            # 提取所有ts文件名
            ts_files = []
            for line in response.text.split('\n'):
                if line.endswith('.ts'):
                    ts_files.append(urljoin(base_url, line))
            
            return ts_files
        except Exception as e:
            print(f"解析m3u8文件失败: {e}")
            raise

    def download_ts(self, ts_url, save_path, progress_callback):
        """下载单个ts文件"""
        if self.stop_flag:
            return False
            
        try:
            # 检查文件是否已存在
            filename = os.path.basename(ts_url)
            filepath = os.path.join(save_path, filename)
            if os.path.exists(filepath):
                progress_callback()
                return True
                
            response = self.session.get(ts_url, timeout=30)
            response.raise_for_status()
            
            # 保存文件
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            progress_callback()
            return True
        except Exception as e:
            if not self.stop_flag:
                print(f"下载 {ts_url} 失败: {e}")
            return False

    def merge_ts_files(self, ts_files, output_file):
        """合并ts文件"""
        print("\n开始合并文件...")
        try:
            with open(output_file, 'wb') as outfile:
                for ts_file in tqdm(sorted(ts_files), desc="合并进度"):
                    if self.stop_flag:
                        break
                    filepath = os.path.join('temp', os.path.basename(ts_file))
                    if os.path.exists(filepath):
                        with open(filepath, 'rb') as infile:
                            outfile.write(infile.read())
                        os.remove(filepath)  # 删除已合并的ts文件
        except Exception as e:
            print(f"合并文件失败: {e}")
            raise

    def download(self, output_file='output.mp4'):
        """主下载函数"""
        try:
            # 打印系统信息
            print(f"系统CPU核心数: {multiprocessing.cpu_count()}")
            print(f"使用线程数: {self.num_threads}")
            print("按 Ctrl+C 可以停止下载")
            
            # 创建临时目录
            os.makedirs('temp', exist_ok=True)
            
            # 解析m3u8获取ts文件列表
            print("\n解析m3u8文件...")
            ts_files = self.parse_m3u8()
            total_files = len(ts_files)
            print(f"找到 {total_files} 个ts文件")
            
            # 检查已下载的文件
            downloaded_files = set()
            for ts_file in ts_files:
                if os.path.exists(os.path.join('temp', os.path.basename(ts_file))):
                    downloaded_files.add(ts_file)
            
            if downloaded_files:
                print(f"发现 {len(downloaded_files)} 个已下载的文件")
            
            # 创建进度条
            progress_bar = tqdm(total=total_files, desc="下载进度")
            progress_bar.update(len(downloaded_files))
            
            # 定义进度更新回调函数
            def update_progress():
                with self.lock:
                    progress_bar.update(1)
            
            # 多线程下载
            print("\n开始下载ts文件...")
            with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
                # 提交所有下载任务
                futures = {
                    executor.submit(self.download_ts, ts_url, 'temp', update_progress): ts_url 
                    for ts_url in ts_files 
                    if ts_url not in downloaded_files
                }
                
                # 等待所有任务完成
                for future in as_completed(futures):
                    if self.stop_flag:
                        break
            
            progress_bar.close()
            
            if not self.stop_flag:
                # 合并文件
                self.merge_ts_files(ts_files, output_file)
                
                # 清理临时目录
                if os.path.exists('temp'):
                    os.rmdir('temp')
                
                print(f"\n下载完成！文件保存为: {output_file}")
            else:
                print("\n下载已停止，可以稍后继续下载")
                
        except Exception as e:
            print(f"下载过程出错: {e}")
            raise

if __name__ == "__main__":
    url = "https://europe.olemovienews.com/ts4/20260110/818a2vxr/mp4/818a2vxr.mp4/index-v1-a1.m3u8"
    downloader = M3U8Downloader(url)
    try:
        downloader.download()
    except KeyboardInterrupt:
        print("\n下载被用户中断")
    except Exception as e:
        print(f"\n下载出错: {e}")
