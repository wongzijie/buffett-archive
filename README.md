# Buffett Archive · 巴菲特本地知识库

把本仓库链接发给能操作电脑的 AI，即可让它按照 [AI_INSTALL.md](AI_INSTALL.md) 帮你部署。无需访问作者的电脑、Tailscale、私有服务器或付费模型 API。

> 请阅读 https://github.com/wongzijie/buffett-archive 的 AI_INSTALL.md，检查我的电脑环境，部署数据库，运行验证，并把检索工具接入我使用的 AI。先安装无需显卡的版本；不要未经我同意下载大模型或覆盖现有配置。

纯聊天网页中的 AI 如果不能执行命令，只能提供安装指导；实际安装需要能操作本机的 AI 助手，或由你执行命令。不是所有 AI 产品都支持 MCP。

## 包含什么

| 内容 | 数量 / 状态 |
|---|---|
| 完整逻辑备份 | 459 篇文档、16,649 个片段及其 1024 维 WeMM 向量 |
| 可检索内容 | 412 篇文档、16,065 个片段 |
| 可检索资料构成 | 317 篇访谈／大会等转录 + 95 篇信件／文章 |
| 屏蔽内容 | 47 篇已存档但排除／待定文档；普通检索与上下文工具均不可访问 |
| 原始 416 篇转录初筛 | 317 保留候选、90 排除、9 待定；保留候选中有 1 篇完全重复 |
| 音视频认证 | 未进行；不是逐句说话人认证或权威原话全集 |
| 数据包 | 约 81 MB 压缩数据，恢复后约 276 MB；安装时建议预留 1 GB |

快照日期：2026-09-20。备份保存 Markdown 原文、片段、出处、真实性标签、内容审查和预计算向量。它是可移植的 SQLite **逻辑备份**，不是原服务器磁盘镜像；不包含服务密钥、个人路径、网络配置、模型权重和音视频。排除数据仍存在备份中，开发者直接读取数据库能够看到；检索屏蔽不等于数据加密。

## 两种运行方式

| 模式 | 电脑要求 | 能力 |
|---|---|---|
| 默认关键词检索 | Windows / macOS / Linux；Python 3.10+；无需显卡、无需 pip 依赖 | 本地英文全文检索、出处与上下文读取。中文提问时让 AI 先转成英文关键词 |
| 可选 WeMM 语义检索 | CUDA / NVIDIA GPU；原运行环境为 RTX 5090 32 GB | 多语言语义检索与关键词混合排序；复用已有向量，只计算查询向量 |

默认模式不是向量检索。没有足够显存时不要强行启用 WeMM。预计算向量必须配合同一模型、维度和编码规则，不能随意换一个 embedding 模型继续查询。详见 [WeMM 配置](docs/WEMM.md)。

## 三步开始

安装 Python 3.10+ 和 Git 后，在终端执行：

```sh
git clone https://github.com/wongzijie/buffett-archive.git
cd buffett-archive
python setup_archive.py
python archive.py search "insurance float"
```

macOS / Linux 常用命令是 `python3`；Windows 也可以用 `py -3`。若 `python --version` 低于 3.10，安装新版 Python。也可在 GitHub 点 **Code → Download ZIP**，完整解压后进入目录执行后两条命令。数据直接随仓库提供，无需 Git LFS 或 GitHub 登录。

安装脚本验证各分片 SHA-256，恢复 SQLite，再验证完整数据库哈希、完整性与数量。它不下载模型、不改系统服务，也不覆盖已有的不同数据库。

```sh
python archive.py stats
python archive.py search "margin of safety" --top-k 3 --max-chars 5000
python archive.py context '<检索结果中的 chunk_id>'
python -m unittest discover -s tests -v
```

`max_chars` 是正文字符预算，不是假装精确的模型 token 数；返回元数据另计。默认最多返回 5 个片段，每篇最多 2 个，便于 AI 按需读取，节省上下文。

## 接入 Claude / Gemini / Codex 等 AI

支持本地 MCP 的客户端可以共用该数据库，不需要每家重新向量化：

```sh
python -m venv .venv
# macOS / Linux：
.venv/bin/python -m pip install -r requirements-mcp.txt
# Windows：
.venv\Scripts\python.exe -m pip install -r requirements-mcp.txt
```

在客户端的 MCP 设置中**合并**以下条目，把路径替换为你电脑的绝对路径：

```json
{
  "mcpServers": {
    "buffett-archive": {
      "command": "/ABSOLUTE/PATH/buffett-archive/.venv/bin/python",
      "args": ["/ABSOLUTE/PATH/buffett-archive/archive.py", "mcp"]
    }
  }
}
```

Windows 的 `command` 用 `.venv\\Scripts\\python.exe` 的完整路径。不同客户端配置格式可能不同，AI 应按该客户端文档转换，保留已有工具。提供三个工具：`search_buffett`、`get_buffett_context`、`buffett_archive_status`。

网页版／手机端不会因为克隆仓库就自动连上你的电脑；它们需要产品支持的远程接入方式，本仓库不自动开启公网服务。仅支持工具调用 API 的应用也可直接运行 CLI 或调用 `Archive.search()`。

## 可信度与许可

标题、文档说话人标签或搜索分数不能证明某句话是巴菲特讲的。混合访谈可能包含主持人、其他嘉宾与问题；初审通过的 `unverified` 资料可以被检索，但返回标签保持不变。未知年份不猜填。引用时检查原文上下文和 `source_url`，说明未核验限制。

部署代码采用 MIT；第三方原文与模型受各自权利和许可约束，并未被本项目重新授权。详见 [DATA_NOTICE.md](DATA_NOTICE.md)。来源与分类详见 `data/content_audit.json` 和数据库元数据。部署与验收记录见 [VALIDATION.md](docs/VALIDATION.md)。
