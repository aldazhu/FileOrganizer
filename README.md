# 文件夹整理工具 (File Organizer)

一个用Python编写的智能文件夹整理工具，可以自动扫描指定文件夹并根据文件扩展名分类移动文件。

## 功能特性

- **自动分类**: 根据文件扩展名自动分类到对应的子文件夹
- **配置文件**: 支持JSON配置文件，可自定义分类规则和目标文件夹
- **冲突处理**: 支持多种冲突解决策略（重命名、跳过、覆盖）
- **模拟运行**: 支持模拟运行，预览整理效果而不实际移动文件
- **撤销功能**: 记录操作日志，支持撤销上一次整理操作
- **日志记录**: 详细的运行日志和统计信息
- **跨平台**: 支持Windows、macOS、Linux系统

## 安装要求

- Python 3.7 或更高版本
- 无需额外安装依赖（使用Python标准库）

## 快速开始

### 1. 配置设置

编辑 `config.json` 文件，设置目标文件夹和分类规则：

```json
{
  "target_folder": "C:\\Users\\YourUsername\\Downloads",
  "file_categories": {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
    "Documents": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".md"],
    "Installers": [".exe", ".msi", ".dmg", ".app", ".deb", ".rpm", ".pkg"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Media": [".mp3", ".mp4", ".avi", ".mkv", ".mov", ".wav"],
    "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".json", ".xml"],
    "Others": []
  },
  "log_file": "organizer_log.json",
  "enable_undo": true,
  "conflict_resolution": "rename",
  "dry_run": false
}
```

### 2. 基本使用

运行整理工具：

```bash
python organizer.py
```

### 3. 命令行选项

```bash
# 使用自定义配置文件
python organizer.py --config my_config.json

# 模拟运行（不实际移动文件，默认模式）
python organizer.py --dry-run

# 实际运行（移动文件，覆盖默认的dry run模式）
python organizer.py --run

# 指定目标文件夹（覆盖配置文件）
python organizer.py --target "C:\Users\YourUsername\Desktop"

# 递归处理子文件夹中的文件
python organizer.py --recursive

# 不递归处理子文件夹（仅处理根目录文件，默认模式）
python organizer.py --no-recursive

# 撤销上一次操作
python organizer.py --undo

# 组合使用（安全模式：模拟运行 + 不递归）
python organizer.py --config config.json --dry-run --no-recursive

# 组合使用（实际运行 + 递归处理）
python organizer.py --config config.json --run --recursive --target "C:\Downloads"
```

## 配置文件说明

### 主要配置项

| 配置项                | 类型    | 默认值               | 说明                                                            |
| --------------------- | ------- | -------------------- | --------------------------------------------------------------- |
| `target_folder`       | string  | 用户下载文件夹       | 要整理的目标文件夹路径                                          |
| `file_categories`     | object  | 预定义分类           | 文件分类规则，键为文件夹名，值为扩展名列表                      |
| `log_file`            | string  | "organizer_log.json" | 操作日志文件路径                                                |
| `enable_undo`         | boolean | true                 | 是否启用撤销功能                                                |
| `conflict_resolution` | string  | "rename"             | 冲突解决策略：rename（重命名）、skip（跳过）、overwrite（覆盖） |
| `dry_run`             | boolean | true                 | 是否模拟运行（默认模拟运行，安全模式）                          |
| `recursive`           | boolean | false                | 是否递归处理子文件夹中的文件（默认不递归，保护项目结构）        |

### 自定义分类规则

你可以根据需要修改 `file_categories` 部分：

```json
"file_categories": {
  "图片": [".jpg", ".png", ".gif"],
  "文档": [".pdf", ".docx", ".xlsx"],
  "软件": [".exe", ".dmg", ".app"],
  "压缩包": [".zip", ".rar"],
  "其他": []
}
```

## 使用示例

### 示例1：整理下载文件夹

```bash
# 编辑配置文件，设置 target_folder 为你的下载文件夹路径
# 然后运行：
python organizer.py
```

输出示例：
```
开始扫描文件夹: C:\Users\YourUsername\Downloads
模式: 实际运行
--------------------------------------------------
创建文件夹: C:\Users\YourUsername\Downloads\Images
移动: photo1.jpg -> Images/
创建文件夹: C:\Users\YourUsername\Downloads\Documents
移动: report.pdf -> Documents/
创建文件夹: C:\Users\YourUsername\Downloads\Installers
移动: setup.exe -> Installers/
移动: unknown_file.xyz -> Others/
--------------------------------------------------
整理完成！
总文件数: 15
移动文件: 12
跳过文件: 2
创建文件夹: 6
错误数: 0
操作日志已保存到: organizer_log.json
```

### 示例2：模拟运行测试

```bash
python organizer.py --dry-run
```

输出示例：
```
开始扫描文件夹: C:\Users\YourUsername\Downloads
模式: 模拟运行
--------------------------------------------------
[模拟] 创建文件夹: C:\Users\YourUsername\Downloads\Images
[模拟] 移动: photo1.jpg -> Images/
[模拟] 创建文件夹: C:\Users\YourUsername\Downloads\Documents
[模拟] 移动: report.pdf -> Documents/
--------------------------------------------------
整理完成！
总文件数: 15
移动文件: 12
跳过文件: 2
创建文件夹: 6
错误数: 0

注意：本次为模拟运行，未实际移动文件
如需实际移动，请将配置文件中的 dry_run 设置为 false
```

### 示例3：撤销操作

```bash
# 如果对整理结果不满意，可以撤销
python organizer.py --undo
```

输出示例：
```
准备撤销操作 (时间: 2024-01-15T10:30:45.123456)
目标文件夹: C:\Users\YourUsername\Downloads
撤销移动: photo1.jpg -> Downloads/
撤销移动: report.pdf -> Downloads/
成功撤销 2 个文件移动操作
```

## 高级功能

### 1. 安全默认设置

工具采用安全第一的设计原则，默认设置保护用户数据：

1. **默认模拟运行（dry_run: true）**：
   - 首次运行仅预览整理效果，不实际移动文件
   - 避免误操作导致文件丢失或错位
   - 使用 `--run` 参数进行实际文件移动

2. **默认非递归处理（recursive: false）**：
   - 仅处理目标文件夹根目录下的零散文件
   - 不处理子文件夹中的文件，保护项目结构和文档集完整性
   - 使用 `--recursive` 参数进行递归处理

### 2. 递归处理控制

工具提供灵活的递归处理控制，保护文件夹结构的完整性：

1. **非递归模式（默认）**：仅处理目标文件夹根目录下的文件，不处理子文件夹
   - 适用场景：整理下载文件夹、桌面等零散文件
   - 优点：保护项目文件夹、文档集的完整性
   - 使用方式：配置文件设置 `"recursive": false` 或命令行参数 `--no-recursive`

2. **递归模式**：处理目标文件夹及其所有子文件夹中的文件
   - 适用场景：深度整理整个文件夹树
   - 注意：会移动子文件夹中的文件，可能破坏项目结构
   - 使用方式：配置文件设置 `"recursive": true` 或命令行参数 `--recursive`

### 2. 冲突解决策略

工具支持三种冲突解决策略：

1. **rename**（默认）：如果目标文件已存在，自动重命名（如 `file_1.txt`, `file_2.txt`）
2. **skip**：跳过已存在的文件，不移动
3. **overwrite**：覆盖已存在的文件（谨慎使用）

### 3. 操作日志

每次运行都会生成详细的JSON格式日志文件（默认：`organizer_log.json`），包含：
- 操作时间戳
- 配置文件信息
- 目标文件夹路径
- 所有移动操作的详细记录
- 运行统计信息

### 4. 错误处理

工具会捕获并记录以下错误：
- 文件移动失败
- 文件夹创建失败
- 配置文件读取错误
- 日志保存错误

所有错误都会显示在控制台并记录到统计信息中。


## 注意事项

1. **安全第一**：工具默认采用模拟运行模式，首次使用会自动预览整理效果，不会实际移动文件
2. **预览确认**：使用默认设置（或 `--dry-run`）先预览整理效果，确认无误后再使用 `--run` 参数实际运行
3. **保护项目结构**：默认不递归处理子文件夹，保护项目文件夹和文档集的完整性
4. **备份重要文件**：首次实际运行前建议备份重要文件
5. **配置文件路径**：Windows路径使用双反斜杠 `\\` 或正斜杠 `/`
6. **权限问题**：确保有目标文件夹的读写权限
7. **大文件处理**：移动大文件可能需要较长时间
8. **递归处理谨慎使用**：默认不递归处理子文件夹，避免破坏项目结构。如需递归处理，请确认子文件夹中没有需要保持完整的文件集


## 更新日志

### v1.0.0 (2024-01-15)
- 初始版本发布
- 基本文件分类和移动功能
- 配置文件支持
- 冲突解决策略
- 模拟运行模式
- 撤销功能
- 详细日志记录