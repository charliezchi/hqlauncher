# HqLauncher

智多晶（XiST）FPGA 开发工具 **HqFpga** 的版本启动器。

HqFpga 是绿色免安装的，版本迭代快，通常会有多个版本共存。HqLauncher 自动扫描目录下的所有版本，让你快速启动最新版或任意指定版本。

## 功能特点

- **自动扫描**：自动发现配置根目录下的所有 HqFpga 版本
- **快速启动**：一行命令启动最新版，或通过 build 号精确启动指定版本
- **CLI + GUI**：同时支持 `hqfpga`（前台 CLI，继承终端输出）和 `hqui`（后台 GUI，不阻塞终端）启动
- **工程文件打开**：支持将 `.hqprj` 工程文件路径直接传给 hqui 打开（需 build ≥ `FT051426`）
- **零依赖运行**：提供独立 `exe`，无 Python 环境也能开箱即用
- **持久化配置**：扫描根目录等配置自动保存到本地

## 开箱即用

从 [Releases](../../releases) 页面下载最新版 `hqlauncher.exe`，放到任意目录即可。

如果你从源码仓库使用，一行命令完成编译并注册到 PATH。默认（不带参数）会先 `clean` 再 `build`，`build` 成功后会自动将 `hqlauncher.exe` 复制到 `%APPDATA%\hqlauncher\` 并添加到用户 PATH：

```powershell
.\build.ps1        # 先 clean 再 build + 自动注册
.\build.ps1 build  # 仅 build + 自动注册
```

## 使用方式

### 启动 GUI（默认）

无 `-cmd` 参数时，启动 `hqui`（后台 GUI）。`-b` 可选，用于指定 build：

```bat
hqlauncher              # 启动最新版 hqui
hqlauncher -b FT041226  # 启动指定 build 的 hqui
```

**直接打开工程文件**（仅当版本 build ≥ `FT051426` 时支持）：

```bat
hqlauncher "C:\hqws\test30k\test30k.hqprj"                # 直接打开工程文件
hqlauncher -b FT051426 "C:\hqws\test30k\test30k.hqprj"   # 指定版本打开工程
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
hqlauncher -ls -device  # 列出 dv_list.xml 中所有器件（默认 -all）
hqlauncher -ls -device -seal   # 列出 SEAL 系列器件
hqlauncher -ls -device -shark  # 列出 SHARK 系列器件
hqlauncher -ls -device -sealion # 列出 SEALION 系列器件
hqlauncher -ls -device -seal -startwith SA5Z-30  # 前缀过滤
hqlauncher -cfg         # 显示当前配置
hqlauncher -cfg show    # 同上
hqlauncher -cfg set-root "C:\hq"     # 添加扫描根目录
hqlauncher -cfg remove-root "C:\hq"  # 移除扫描根目录
hqlauncher -cfg init    # 恢复默认配置
hqlauncher -dl          # 启动下载器 hqdnload
hqlauncher -cable -h    # 启动 cable.exe 并透传 -h（查看 cable 帮助）
hqlauncher -cable info  # 启动 cable.exe 并透传 info 子命令
hqlauncher -doc         # 打开用户手册
hqlauncher -cd          # 在资源管理器中打开安装目录
hqlauncher -env         # 输出版本安装目录路径
```

## 参数速查

| 参数 | 说明 |
|------|------|
| `-h` | 显示帮助 |
| `-v` | 显示版本 |
| `-ls` | 列出版本 |
| `-ls -device [-all\|-shark\|-seal\|-sealion] [-startwith <prefix>]` | 列出支持的器件（默认 `-all`） |
| `-cfg [action]` | 配置管理（默认 show） |
| `-b <build>` | 指定 build 号（如 `FT041226`） |
| `-cmd <file>` | 启动 `hqfpga` 并执行 cmd 文件 |
| `-dl` | 启动下载器 `hqdnload` |
| `-cable [args]` | 启动 `cable.exe`，透传所有子命令（只用最新版本） |
| `-doc` | 打开用户手册 |
| `-cd` | 在资源管理器中打开安装目录 |
| `-env` | 输出版本安装目录路径 |

## 判断逻辑

1. `-h` → 帮助
2. `-v` → 版本
3. `-ls` → 列出版本；`-ls -device` → 列出器件
4. `-cfg` → 配置管理
5. `-cable` → 启动 `cable.exe`，后续参数全部透传（只用最新版本）
6. `-doc` → 打开用户手册
7. `-cd` → 在资源管理器中打开安装目录
8. `-env` → 输出版本安装目录路径
9. `-cmd` → 启动 `hqfpga`，`-cmd` 及后续参数全部透传
10. `-dl` → 启动下载器 `hqdnload`
11. 其他 → 启动 `hqui`：
   - 如果参数是文件路径（不以 `-` 开头）且版本 build ≥ `FT051426` → 将路径传给 `hqui` 打开工程
   - 否则 → 忽略未知参数并发出警告

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
.\build.ps1 build

:: 清理构建产物
.\build.ps1 clean
```

使用 `build.ps1` 统一管理：

| 命令                  | 说明                                              |
| --------------------- | ------------------------------------------------- |
| `.\build.ps1`         | 先 `clean` 再 `build`，成功后自动复制 exe 并注册 PATH |
| `.\build.ps1 build`   | 打包 `hqlauncher.exe`，成功后自动复制 exe 并注册 PATH |
| `.\build.ps1 clean`   | 清理 exe、log、dump 及 PyInstaller 临时文件         |
| `.\build.ps1 help`    | 显示帮助                                          |

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
├── build.ps1            # 构建 / 清理统一管理，build 成功后自动注册 PATH
├── .gitignore
├── LICENSE
└── README.md
```

## License

[LICENSE](LICENSE)
