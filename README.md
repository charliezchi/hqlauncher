# HqLauncher

智多晶（XiST）FPGA 开发工具 **HqFpga** 的版本启动器。

HqFpga 是绿色免安装的，版本迭代快，通常会有多个版本共存。HqLauncher 自动扫描目录下的所有版本，让你快速启动最新版或任意指定版本。

## 功能特点

- **自动扫描**：自动发现配置根目录下的所有 HqFpga 版本
- **快速启动**：一行命令启动最新版，或通过 build 号精确启动指定版本
- **CLI + GUI**：同时支持 `hqfpga`（前台 CLI，继承终端输出）和 `hqui`（后台 GUI，不阻塞终端）启动
- **零依赖运行**：提供独立 `exe`，无 Python 环境也能开箱即用
- **持久化配置**：扫描根目录等配置自动保存到本地

## 开箱即用

从 [Releases](../../releases) 页面下载最新版 `hqlauncher.exe`，放到任意目录即可。

如果你从源码仓库使用，运行以下命令自动注册到 PATH。`make register` 不会把整个项目目录加到 PATH（避免 `make` 等命令污染），而是只在 `%APPDATA%\hqlauncher\` 下创建一个 `hqlauncher.bat` 代理脚本，优先调用 `hqlauncher.exe`，没有则回退到 `hqlauncher.bat`（Python 开发入口）：

```bat
make register
```

## 使用方式

### 启动 GUI（默认）

无 `-cmd` 参数时，启动 `hqui`（后台 GUI）。`-b` 可选，用于指定 build：

```bat
hqlauncher              # 启动最新版 hqui
hqlauncher -b FT041226  # 启动指定 build 的 hqui
```

### 启动 CLI

带 `-cmd` 参数时，自动启动 `hqfpga`（前台 CLI），`-cmd` 及后续所有参数透传给 `hqfpga.exe`：

```bat
hqlauncher -cmd xx.tcl                    # 启动最新版 hqfpga
hqlauncher -b FT041226 -cmd xx.tcl       # 启动指定 build 的 hqfpga
```

### 其他命令

```bat
hqlauncher -h           # 显示帮助
hqlauncher -v           # 显示版本
hqlauncher -ls          # 列出所有发现的版本
hqlauncher -cfg         # 显示当前配置
hqlauncher -cfg show    # 同上
hqlauncher -cfg set-root "C:\hq"     # 添加扫描根目录
hqlauncher -cfg remove-root "C:\hq"  # 移除扫描根目录
hqlauncher -cfg init    # 恢复默认配置
```

## 参数速查

| 参数 | 说明 |
|------|------|
| `-h` | 显示帮助 |
| `-v` | 显示版本 |
| `-ls` | 列出版本 |
| `-cfg [action]` | 配置管理（默认 show） |
| `-b <build>` | 指定 build 号（如 `FT041226`） |
| `-cmd <file>` | 启动 `hqfpga` 并执行 cmd 文件 |

## 判断逻辑

1. `-h` → 帮助
2. `-v` → 版本
3. `-ls` → 列出版本
4. `-cfg` → 配置管理
5. `-cmd` → 启动 `hqfpga`，`-cmd` 及后续参数全部透传
6. 其他 → 启动 `hqui`

`-b` 在 `hqfpga` 和 `hqui` 两种模式下均可使用。

## 配置

配置文件路径：`%APPDATA%\hqlauncher\config.json`

```json
{
  "scan_roots": [
    "C:\\"
  ]
}
```

- `scan_roots`：扫描根目录列表，默认只扫描 `C:\`
- 可通过 `hqlauncher -cfg` 命令管理，或直接编辑 JSON 文件

## 开发与打包

```bat
:: 克隆仓库
git clone https://github.com/XiST-ZhC/hqlauncher.git
cd hqlauncher

:: 安装依赖（Python 3.10+）
pip install pyinstaller

:: 开发运行（Python 源码）
.\hqlauncher.bat -ls
python -m hqlauncher -ls

:: 打包 exe
make build

:: 清理构建产物
make clean
```

使用 `make.bat` 统一管理：

| 命令              | 说明                                        |
| ----------------- | ------------------------------------------- |
| `make build`    | 打包 `hqlauncher.exe`                     |
| `make clean`    | 清理 exe、log、dump 及 PyInstaller 临时文件 |
| `make register` | 将当前目录注册到用户 PATH                   |
| `make help`     | 显示帮助                                    |

打包时会临时生成入口脚本，完成后自动清理，仓库内无残留。

## 项目结构

```
hqlauncher/
├── hqlauncher/          # Python 源码包
│   ├── __main__.py      # CLI 入口
│   ├── config.py        # 配置管理
│   ├── scanner.py       # 版本扫描
│   ├── launcher.py      # 启动逻辑
│   └── utils.py         # 版本解析
├── hqlauncher.bat       # 开发入口（调用 Python 源码）
├── make.bat             # 构建 / 清理 / 注册 PATH 统一管理
├── .gitignore
├── LICENSE
└── README.md
```

## License

[LICENSE](LICENSE)
