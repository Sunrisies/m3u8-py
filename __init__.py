"""
M3U8 Downloader Package
一个模块化的M3U8视频下载器，支持多线程下载、断点续传、错误重试等功能
"""

from .downloader import M3U8Downloader
from .parser import M3U8Parser
from .downloader import DownloadManager
from .config import DownloadConfig

__version__ = "2.0.0"
__all__ = ["M3U8Downloader", "M3U8Parser", "DownloadManager", "DownloadConfig"]
