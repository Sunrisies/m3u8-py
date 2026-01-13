# M3U8 Downloader Pro

一个模块化的高性能M3U8视频下载器，支持多线程下载、断点续传、错误重试等功能。

## ✨ 特性

- **模块化设计**: 清晰的代码结构，易于维护和扩展
- **多线程下载**: 支持并发下载，提高下载速度
- **断点续传**: 支持断点续传，网络中断后可继续下载
- **错误重试**: 自动重试机制，提高下载成功率
- **智能解析**: 自动解析M3U8文件，提取TS片段
- **进度显示**: 实时进度条和统计信息
- **日志记录**: 详细的日志记录，便于调试
- **配置模板**: 提供多种预设配置模板
- **命令行工具**: 友好的CLI交互界面

## 📁 项目结构

```
m3u8/
├── __init__.py          # 包初始化文件
├── config.py            # 配置模块
├── parser.py            # M3U8解析器
├── downloader.py        # 下载器核心
├── utils.py             # 工具函数
├── cli.py               # 命令行接口
├── example_usage.py     # 使用示例
└── README.md            # 说明文档
```

## 🚀 快速开始

### 安装依赖

```bash
pip install requests tqdm
```

### 命令行使用

#### 交互模式
```bash
python -m m3u8.cli -i
```

#### 基本下载
```bash
python -m m3u8.cli https://example.com/video.m3u8
```

#### 自定义参数
```bash
python -m m3u8.cli https://example.com/video.m3u8 -o myvideo.mp4 -t 8 --profile fast
```

#### 使用配置模板
```bash
# 快速模式
python -m m3u8.cli https://example.com/video.m3u8 --profile fast

# 稳定模式（推荐）
python -m m3u8.cli https://example.com/video.m3u8 --profile stable

# 低带宽模式
python -m m3u8.cli https://example.com/video.m3u8 --profile low_bandwidth
```

#### 自定义请求头
```bash
python -m m3u8.cli https://example.com/video.m3u8 --headers "Referer=https://example.com,User-Agent=Custom"
```

### 编程使用

#### 基础使用
```python
from m3u8.downloader import M3U8Downloader

url = "https://example.com/video.m3u8"
downloader = M3U8Downloader(url)
success = downloader.download("output.mp4")
```

#### 自定义配置
```python
from m3u8.config import DownloadConfig
from m3u8.downloader import M3U8Downloader

config = DownloadConfig(
    num_threads=8,
    max_retries=5,
    retry_delay=2.0,
    connect_timeout=15,
    read_timeout=60,
)

downloader = M3U8Downloader(url, config)
downloader.download("output.mp4")
```

#### 使用配置模板
```python
from m3u8.config import ConfigTemplates
from m3u8.downloader import M3U8Downloader

# 快速模式
config = ConfigTemplates.fast()

# 稳定模式
config = ConfigTemplates.stable()

downloader = M3U8Downloader(url, config)
downloader.download("output.mp4")
```

#### 仅解析M3U8
```python
from m3u8.parser import M3U8Parser

parser = M3U8Parser(verify_ssl=False)
ts_files, info = parser.parse_m3u8(url)

print(f"找到 {len(ts_files)} 个TS文件")
print(f"分辨率: {info['resolution']}")
```

## ⚙️ 配置参数

### DownloadConfig

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `num_threads` | int | CPU核心数*2 | 下载线程数 |
| `connect_timeout` | int | 10 | 连接超时(秒) |
| `read_timeout` | int | 30 | 读取超时(秒) |
| `max_retries` | int | 3 | 最大重试次数 |
| `retry_delay` | float | 1.0 | 重试延迟(秒) |
| `chunk_size` | int | 8192 | 下载块大小(字节) |
| `buffer_size` | int | 1048576 | 文件缓冲区大小(字节) |
| `temp_dir` | str | "temp" | 临时目录 |
| `output_dir` | str | "." | 输出目录 |
| `headers` | dict | 标准请求头 | 自定义请求头 |
| `verify_ssl` | bool | False | SSL验证 |
| `show_progress` | bool | True | 显示进度条 |
| `enable_logging` | bool | True | 启用日志 |

### 配置模板

- **快速模式**: 高并发，适合带宽充足的环境
- **稳定模式**: 平衡配置，推荐使用
- **低带宽模式**: 低并发，适合网络环境较差的情况

## 🔧 高级功能

### 断点续传
下载器会自动检查已下载的文件，跳过已完成的片段。

### 错误处理
- 自动重试失败的下载
- 指数退避策略
- 详细的错误日志

### 信号处理
支持 `Ctrl+C` 中断下载，会保存已下载的内容。

### 日志记录
所有操作都会记录到 `download.log` 文件中。

## 📖 使用示例

运行示例代码：
```bash
python -m m3u8.example_usage
```

## 🎯 命令行参数详解

```
usage: python -m m3u8.cli [OPTIONS] [URL]

M3U8 Downloader Pro - 高性能M3U8视频下载器

位置参数:
  url                  M3U8文件URL

可选参数:
  -h, --help           显示帮助信息
  -o, --output         输出文件路径
  -t, --threads        下载线程数
  --profile            配置模板 (fast|stable|low_bandwidth)
  --max-retries        最大重试次数
  --retry-delay        重试延迟(秒)
  --connect-timeout    连接超时(秒)
  --read-timeout       读取超时(秒)
  --temp-dir           临时目录路径
  --output-dir         输出目录路径
  --headers            自定义请求头
  --user-agent         自定义User-Agent
  --referer            设置Referer
  --no-ssl-verify      禁用SSL验证
  --no-progress        禁用进度条
  --no-logging         禁用日志
  --dry-run            试运行
  -i, --interactive    交互模式
```

## 🛠️ 开发说明

### 模块设计原则

1. **单一职责**: 每个模块只负责一个功能
2. **接口清晰**: 模块间通过明确定义的接口通信
3. **易于测试**: 模块独立，便于单元测试
4. **可扩展**: 支持未来功能扩展

### 错误处理策略

1. **网络错误**: 自动重试 + 指数退避
2. **文件错误**: 详细的错误信息 + 回滚机制
3. **用户中断**: 优雅退出 + 保存进度

### 性能优化

1. **连接复用**: 使用Session复用HTTP连接
2. **内存管理**: 流式下载，避免大文件内存溢出
3. **并发控制**: 合理的线程池大小

## 🐛 常见问题

### Q: 下载速度慢？
A: 尝试增加线程数，或使用 `--profile fast`

### Q: 下载中断后如何继续？
A: 下载器会自动断点续传，重新运行即可

### Q: 如何设置代理？
A: 可以通过环境变量设置HTTP_PROXY/HTTPS_PROXY

### Q: SSL证书错误？
A: 使用 `--no-ssl-verify` 参数

## 📝 更新日志

### v2.0.0
- 完全重构为模块化架构
- 新增配置模板系统
- 改进错误处理和重试机制
- 优化下载性能
- 新增CLI交互模式

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！
