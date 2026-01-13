"""
高级命令行接口
支持JSON配置文件、流式下载、多任务管理
"""

import argparse
import sys
import os
import json

from .config import DownloadConfig, ConfigTemplates
from .advanced_downloader import AdvancedM3U8Downloader, DownloadTask, JSONTaskLoader
from .utils import print_banner, safe_input, confirm_action, FileValidator, URLProcessor


class AdvancedM3U8CLI:
    """高级M3U8命令行界面"""
    
    def __init__(self):
        self.downloader = None
    
    def parse_arguments(self):
        """解析命令行参数"""
        parser = argparse.ArgumentParser(
            description="M3U8 Downloader Pro - 高级版 (支持JSON配置和流式下载)",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
使用示例:
  # 单个下载
  python -m m3u8.advanced_cli https://example.com/video.m3u8 -o output.mp4
  
  # JSON批量下载
  python -m m3u8.advanced_cli --json tasks.json
  
  # 交互模式
  python -m m3u8.advanced_cli -i
  
  # 自定义配置
  python -m m3u8.advanced_cli https://example.com/video.m3u8 --profile fast --threads 16
            """
        )
        
        # 基本参数
        parser.add_argument('url', nargs='?', help='M3U8文件URL')
        parser.add_argument('-o', '--output', help='输出文件路径')
        parser.add_argument('-t', '--threads', type=int, help='下载线程数')
        
        # JSON配置
        parser.add_argument('--json', help='JSON配置文件路径')
        parser.add_argument('--output-dir', default='./output', help='批量下载输出目录')
        parser.add_argument('--max-concurrent', type=int, default=3, help='最大并发任务数 (默认3)')
        
        # 配置模板
        parser.add_argument('--profile', choices=['fast', 'stable', 'low_bandwidth'], 
                          help='下载配置模板')
        
        # 高级参数
        parser.add_argument('--max-retries', type=int, help='最大重试次数')
        parser.add_argument('--retry-delay', type=float, help='重试延迟(秒)')
        parser.add_argument('--connect-timeout', type=int, help='连接超时(秒)')
        parser.add_argument('--read-timeout', type=int, help='读取超时(秒)')
        
        # 功能参数
        parser.add_argument('--no-ssl-verify', action='store_true', help='禁用SSL验证')
        parser.add_argument('--no-progress', action='store_true', help='禁用进度条')
        parser.add_argument('--no-logging', action='store_true', help='禁用日志')
        
        # 交互参数
        parser.add_argument('-i', '--interactive', action='store_true', help='交互模式')
        
        return parser.parse_args()
    
    def create_config_from_args(self, args) -> DownloadConfig:
        """从参数创建配置"""
        # 选择配置模板
        if args.profile == 'fast':
            config = ConfigTemplates.fast()
        elif args.profile == 'stable':
            config = ConfigTemplates.stable()
        elif args.profile == 'low_bandwidth':
            config = ConfigTemplates.low_bandwidth()
        else:
            config = DownloadConfig()
        
        # 应用命令行参数
        if args.threads:
            config.num_threads = args.threads
        if args.max_retries:
            config.max_retries = args.max_retries
        if args.retry_delay:
            config.retry_delay = args.retry_delay
        if args.connect_timeout:
            config.connect_timeout = args.connect_timeout
        if args.read_timeout:
            config.read_timeout = args.read_timeout
        if args.no_ssl_verify:
            config.verify_ssl = False
        if args.no_progress:
            config.show_progress = False
        if args.no_logging:
            config.enable_logging = False
        
        return config
    
    def interactive_mode(self):
        """交互模式"""
        print_banner()
        print("🚀 欢迎使用 M3U8 Downloader Pro 高级版\n")
        
        # 选择模式
        print("请选择操作模式:")
        print("1. 单个视频下载")
        print("2. JSON批量下载")
        print("3. 创建JSON配置文件")
        
        mode = safe_input("选择 (1-3) [1]: ", "1")
        
        if mode == "1":
            return self.single_download_interactive()
        elif mode == "2":
            return self.batch_download_interactive()
        elif mode == "3":
            return self.create_json_interactive()
        else:
            print("无效选择")
            return False
    
    def single_download_interactive(self):
        """单个下载交互"""
        url = safe_input("\n请输入M3U8文件URL: ")
        if not url:
            print("未输入URL")
            return False
        
        if not FileValidator.validate_url(url):
            print("URL格式无效")
            return False
        
        url = URLProcessor.normalize_url(url)
        
        # 配置选项
        print("\n下载配置:")
        print("1. 快速模式 (高并发)")
        print("2. 稳定模式 (推荐)")
        print("3. 低带宽模式")
        print("4. 自定义")
        
        choice = safe_input("选择 (1-4) [2]: ", "2")
        
        if choice == "1":
            config = ConfigTemplates.fast()
        elif choice == "2":
            config = ConfigTemplates.stable()
        elif choice == "3":
            config = ConfigTemplates.low_bandwidth()
        else:
            config = self.custom_config_interactive()
        
        output = safe_input("\n输出文件名 [output.mp4]: ", "output.mp4")
        
        # 确认
        print(f"\n准备下载:")
        print(f"  URL: {url}")
        print(f"  输出: {output}")
        print(f"  线程数: {config.num_threads}")
        
        if not confirm_action("\n是否开始下载"):
            return False
        
        # 执行下载
        self.downloader = AdvancedM3U8Downloader(config)
        return self.downloader.download_single("single_task", url, os.path.dirname(output) or ".", {"output_file": output})
    
    def batch_download_interactive(self):
        """批量下载交互"""
        json_file = safe_input("\n请输入JSON配置文件路径: ")
        if not os.path.exists(json_file):
            print(f"文件不存在: {json_file}")
            return False
        
        output_dir = safe_input("输出目录 [./output]: ", "./output")
        
        # 配置选项
        print("\n下载配置:")
        print("1. 快速模式")
        print("2. 稳定模式")
        print("3. 低带宽模式")
        
        choice = safe_input("选择 (1-3) [2]: ", "2")
        
        if choice == "1":
            config = ConfigTemplates.fast()
        elif choice == "2":
            config = ConfigTemplates.stable()
        else:
            config = ConfigTemplates.low_bandwidth()
        
        # 并发数设置
        max_concurrent = safe_input("\n最大并发任务数 (默认3): ", "3")
        if not max_concurrent.isdigit():
            max_concurrent = 3
        else:
            max_concurrent = int(max_concurrent)
        
        # 确认
        print(f"\n准备批量下载:")
        print(f"  配置文件: {json_file}")
        print(f"  输出目录: {output_dir}")
        print(f"  并发任务数: {max_concurrent}")
        print(f"  每任务线程数: {config.num_threads}")
        
        if not confirm_action("\n是否开始批量下载"):
            return False
        
        # 执行批量下载
        self.downloader = AdvancedM3U8Downloader(config)
        
        # 加载任务并执行
        from .advanced_downloader import JSONTaskLoader
        tasks = JSONTaskLoader.load_from_file(json_file, output_dir)
        results = self.downloader.manager.download_batch_tasks(tasks, max_concurrent)
        
        success_count = sum(1 for v in results.values() if v)
        return success_count == len(tasks)
    
    def create_json_interactive(self):
        """创建JSON配置文件交互"""
        print("\n创建JSON配置文件")
        print("=" * 50)
        
        tasks = []
        
        while True:
            print(f"\n已添加 {len(tasks)} 个任务")
            
            name = safe_input("任务名称 (留空结束): ")
            if not name:
                break
            
            url = safe_input("M3U8 URL: ")
            if not FileValidator.validate_url(url):
                print("❌ URL无效")
                continue
            
            output_dir = safe_input("输出目录 (留空使用默认): ")
            if not output_dir:
                output_dir = f"./output/{name}"
            
            # 额外参数
            quality = safe_input("质量 (如1080p, 留空跳过): ")
            language = safe_input("语言 (如chinese, 留空跳过): ")
            
            params = {}
            if quality:
                params['quality'] = quality
            if language:
                params['language'] = language
            
            task = {
                "name": name,
                "url": URLProcessor.normalize_url(url),
                "output_dir": output_dir,
                "params": params
            }
            
            tasks.append(task)
            print(f"✅ 已添加任务: {name}")
            
            if not confirm_action("继续添加任务"):
                break
        
        if not tasks:
            print("未添加任何任务")
            return False
        
        # 保存文件
        filename = safe_input("\n保存为文件 [tasks.json]: ", "tasks.json")
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, ensure_ascii=False, indent=2)
            print(f"✅ 配置文件已保存: {filename}")
            print("\n使用以下命令开始下载:")
            print(f"python -m m3u8.advanced_cli --json {filename}")
            return True
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            return False
    
    def custom_config_interactive(self):
        """自定义配置交互"""
        print("\n自定义配置:")
        
        threads = safe_input("线程数 (回车使用默认): ")
        retries = safe_input("最大重试次数 (回车使用默认): ")
        timeout = safe_input("超时时间(秒) (回车使用默认): ")
        
        config = DownloadConfig()
        
        if threads.isdigit():
            config.num_threads = int(threads)
        if retries.isdigit():
            config.max_retries = int(retries)
        if timeout.isdigit():
            config.connect_timeout = int(timeout)
            config.read_timeout = int(timeout) * 2
        
        return config
    
    def run(self):
        """主运行函数"""
        args = self.parse_arguments()
        
        # 交互模式
        if args.interactive or (not args.url and not args.json):
            return self.interactive_mode()
        
        # JSON批量下载
        if args.json:
            if not os.path.exists(args.json):
                print(f"❌ JSON文件不存在: {args.json}")
                return False
            
            config = self.create_config_from_args(args)
            self.downloader = AdvancedM3U8Downloader(config)
            
            print_banner()
            print(f"📋 JSON模式: {args.json}")
            print(f"📁 输出目录: {args.output_dir}")
            
            return self.downloader.download_from_json(args.json, args.output_dir)
        
        # 单个下载
        if args.url:
            if not FileValidator.validate_url(args.url):
                print(f"❌ URL无效: {args.url}")
                return False
            
            config = self.create_config_from_args(args)
            self.downloader = AdvancedM3U8Downloader(config)
            
            # 确定输出文件
            output = args.output
            if not output:
                filename = args.url.split('/')[-1].split('?')[0]
                if filename.endswith('.m3u8'):
                    output = filename.replace('.m3u8', '.mp4')
                else:
                    output = f"{filename}.mp4"
            
            output_dir = os.path.dirname(output) or "."
            task_name = os.path.basename(output).replace('.mp4', '')
            
            print_banner()
            print(f"📥 单个下载模式")
            print(f"🔗 URL: {args.url}")
            print(f"📁 输出: {output}")
            
            return self.downloader.download_single(task_name, args.url, output_dir, {"output_file": output})
        
        return False


def main():
    """主入口"""
    cli = AdvancedM3U8CLI()
    success = cli.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
