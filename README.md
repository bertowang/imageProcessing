# 数字图像处理：从经典算法到智能方法

> 一本面向本科到研究生的图像处理教材。**上卷 · 传统算法**把每个算法展开成公式与零依赖的 GNU Octave 脚本；**下卷 · AI 算法**给出原理主线、官方开源工程入口与最小复现命令。浏览器打开即可读，复制代码即可验证。

[![Static HTML](https://img.shields.io/badge/format-static%20HTML-orange)](./index.html)
[![Chapters](https://img.shields.io/badge/chapters-27%20%2B%20appendix-blue)](#内容结构)
[![Octave](https://img.shields.io/badge/GNU%20Octave-24%20demos-2ea44f)](#快速开始)
[![Python 3](https://img.shields.io/badge/toolchain-Python%203-3776AB)](#工具链与维护)
[![License](https://img.shields.io/badge/license-not%20specified-lightgrey)](#许可证)

**仓库**：[github.com/bertowang/imageProcessing](https://github.com/bertowang/imageProcessing) · **阅读入口**：[index.html](./index.html) · **版本**：v0.1 · 2026-11

---

## 目录

- [一眼看懂](#一眼看懂)
- [两条路线，一本书](#两条路线一本书)
- [快速开始](#快速开始)
- [内容结构](#内容结构)
- [仓库结构](#仓库结构)
- [每章包含什么](#每章包含什么)
- [工具链与维护](#工具链与维护)
- [质量保障](#质量保障)
- [约定与边界](#约定与边界)
- [同系列教材](#同系列教材)
- [作者与 AI 使用说明](#作者与-ai-使用说明)
- [许可证](#许可证)

## 一眼看懂

| 项目 | 内容 |
| --- | --- |
| 读者定位 | 本科到研究生；面向希望「能手推、能跑、能改」的计算机专业读者 |
| 规模 | 27 章（00–26）+ 附录 A · 上下两卷 · 29 个 HTML 页面 · 24 个 Octave 脚本 · 64 个开源工程 |
| 内容形态 | 纯静态 HTML5 + CSS + 原生 JS；无外部依赖，离线 / `file://` 可读 |
| 上卷（03–15） | 原理推导 + 自包含 GNU Octave 脚本，输出可手算核对的数值 |
| 下卷（16–26） | 原理简介 + 官方开源工程卡片 + 最小复现命令，不重复造轮子 |
| 扩展资源 | 130 条外部链接（教材、论文、官方文档、数据集、开源仓库） |
| 维护工具 | Python 3 标准库生成器 / 抽取器 / 自检器 + `run_octave.sh` 批量验证 |
| 状态 | 27 章全部完稿；静态自检 0 错误 0 提示，24/24 Octave 脚本实跑通过 |

## 两条路线，一本书

**传统算法**把先验写成公式，**AI 算法**把先验交给数据。两者不是替代关系：数据增强、退化建模、几何约束、评价指标与后处理全部来自上卷，而语义鸿沟与可训练表示是下卷要解决的问题。

- 上卷学习闭环：**读公式 → 跑代码 → 改参数 → 写结论**。
- 下卷学习闭环：**读原理 → 跑官方示例 → 换数据集 / 骨干 → 写消融表**。
- Octave 脚本**零第三方依赖**：只用核心函数，用 `meshgrid` 合成测试图像，不调用 image 包的 `imfilter` / `edge` / `imresize`，算法主体全部展开。
- 第 15 章给出一条可交付的传统综合流水线（颗粒计数），第 26 章给出工程落地与综合项目，形成前后对照。

**不适合**：期待本仓库提供深度学习训练代码或预训练权重的读者；下卷按设计只链接官方开源工程。

## 快速开始

### 1. 阅读（无需构建、无需服务器）

```bash
git clone git@github.com:bertowang/imageProcessing.git
cd imageProcessing
open index.html          # macOS；Linux 用 xdg-open，Windows 双击即可
```

也可以直接在本仓库点开 [index.html](./index.html) 查看源码，或启用 GitHub Pages 后以 `index.html` 为入口发布成站点。侧栏目录、面包屑与上下章导航共用 [assets/toc.js](./assets/toc.js) 这一份数据。

### 2. 跑一个 Octave 示例（约 30 秒）

```bash
# 安装 GNU Octave（macOS: brew install octave；Linux 用包管理器；Windows 有安装包）
octave --no-gui --quiet part1/04-spatial-filter/code/04-linear-filter.m
```

- 任意上卷章节的「Octave 实例」代码块右上角可一键复制；仓库里的 `code/*.m` 由 `tools/extract_code.py` 从 HTML 自动抽取，页面与脚本永远一致。
- 脚本开头的「参数区」集中所有可调量，先改这里；结尾 `printf` 打印可手算核对的数值，页面给出预期值与判读逻辑。
- 设置 `IP_HEADLESS=1` 可跳过绘图，适合批量验证。

### 3. 批量验证与自检

```bash
IP_HEADLESS=1 ./tools/run_octave.sh     # 共 24 个脚本：通过 24，失败 0
python3 tools/check_book.py             # 29 个 HTML 页面，28 个章节，24 个 Octave 脚本，0 条错误，0 条提示
```

## 内容结构

| 分部 | 章节 | 主要内容 |
| --- | --- | --- |
| 卷首 · 工具与约定 | 00–02 | 两条路线与阅读约定、Octave 环境与图像 I/O、图像数学表示（采样量化、卷积相关、边界、质量评价） |
| 上卷 · 第一篇 基础变换与增强 | 03–08 | 灰度变换与直方图、空域滤波、频域与傅里叶、图像复原、几何变换、彩色处理 |
| 上卷 · 第二篇 结构分析与理解 | 09–15 | 形态学、边缘、特征、分割、描述、压缩，最后完成传统综合流水线 |
| 下卷 · 第三篇 从特征到深度网络 | 16–19 | 机器学习基线、CNN 基础、骨干网络、数据集与评测 |
| 下卷 · 第四篇 视觉任务与工程落地 | 20–26 | 分类可解释性、检测、分割、复原、生成模型、ViT / 基础模型、部署与综合项目 |
| 附录 | A | 公式与术语速查、Octave 函数对照、开源工程与资源总表 |

建议两个学期、四阶段推进：共同语言 → 变换与复原 → 结构与理解 → 从基线到系统。完整目录与各章知识点见 [index.html](./index.html)。

## 仓库结构

```text
imageProcessing/
├── index.html                     # 总目录：双卷说明、Octave 运行说明、学习路线、参考资源
├── appendix/index.html            # 附录 A：速查与资源总表
├── part0/ … part4/                # 每章一个文件夹
│   └── NN-slug/
│       ├── index.html             # 正文：学习目标、§x.y、实例/开源工程、误区、习题、扩展学习
│       └── code/*.m               # 上卷章节的 Octave 脚本（下卷章节无此目录）
├── assets/
│   ├── style.css                  # 统一排版（含深色主题、打印样式）
│   ├── app.js                     # 侧栏、复制代码块、导航填充
│   └── toc.js                     # 目录唯一数据源：BOOK_TOC / BOOK_FLAT
├── tools/
│   ├── book_schema.py             # 分卷分部与章节数据结构
│   ├── book_data.py               # 章节汇总入口与数据校验
│   ├── book_resources.py          # 外部资源 / 开源工程链接唯一数据源
│   ├── chapters_00_04.py … chapters_22_A.py   # 正文与 Octave 示例（分文件）
│   ├── build_book.py              # 生成全部 HTML 与 assets/toc.js
│   ├── extract_code.py            # 从 HTML 代码块同步 code/*.m
│   ├── check_book.py              # 全书静态自检
│   └── run_octave.sh              # 批量运行全部 .m（IP_HEADLESS=1）
└── .gitignore                     # 忽略缓存、Octave 运行产物与本地验证输出
```

## 每章包含什么

| 栏目 | 作用 |
| --- | --- |
| 学习目标 | 学完应能做什么，用可检验的动词描述 |
| 知识点地图 | 逐条列出知识点，每条挂 1–2 个扩展学习链接 |
| 原理小节 §x.y | 概念、直觉、公式推导、对照表 |
| Octave 实例（上卷） | 完整可运行脚本 + 操作步骤 + 预期数值与判读 |
| 开源工程（下卷） | 官方仓库卡片、推荐用法与最小复现命令 |
| 常见误区 / 习题 | 典型错误与可动手验证的思考题 |
| 扩展学习 | 本章精读资料、GitHub 检索入口与全书资源总表 |
| 状态徽章 | `已完稿` / `框架待补` / `待建`，当前 27 章均为已完稿 |

## 工具链与维护

**单一数据源**：章节正文、Octave 示例与链接库都写在 `tools/` 的 Python 数据里，HTML 由生成器产出。**不要直接编辑章节 HTML**，否则下次重建会被覆盖。

| 想改什么 | 编辑哪里 |
| --- | --- |
| 某章正文或 Octave 示例 | `tools/chapters_*.py` 中对应的 `C(...)` / `demo(...)` |
| 开源工程与参考链接 | `tools/book_resources.py` 的 `R`、`TOPIC_RULES`、`CHAPTER_RESOURCES`，以及章节的 `highlights` |
| 页面结构与总目录 | `tools/build_book.py` 的 `render()` / `render_index()` |
| 样式与交互 | `assets/style.css`、`assets/app.js` |
| 新增章节 / 分卷 | `tools/book_schema.py` 的 `PARTS` + 对应 `chapters_*.py`，再重建（`toc.js` 自动同步） |

| 命令 | 作用 |
| --- | --- |
| `python3 tools/build_book.py` | 只生成缺失的章节页（不覆盖已有文件） |
| `python3 tools/build_book.py --force` | 全量重建（会丢失对章节页的手工修改） |
| `python3 tools/build_book.py --list` | 列出章节 id / 路径 / 状态 |
| `python3 tools/extract_code.py` | 从 HTML 代码块同步写出 `code/*.m` |
| `python3 tools/extract_code.py --check` | 只检查页面与脚本是否一致 |
| `python3 tools/extract_code.py --clean` | 同步并删除无对应代码块的旧 `.m` |
| `python3 tools/check_book.py` | 全文自检，退出码非 0 时逐条报错 |
| `python3 tools/check_book.py --urls` | 额外联网探测外部链接（需网络） |
| `IP_HEADLESS=1 ./tools/run_octave.sh` | 批量实跑全部 Octave 脚本；也可在后面接单个 `.m` 路径 |

推荐改动顺序：

```bash
python3 tools/build_book.py --force      # 1. 重建页面
python3 tools/extract_code.py            # 2. 同步脚本
python3 tools/check_book.py              # 3. 静态自检
IP_HEADLESS=1 ./tools/run_octave.sh      # 4. 实跑示例（需本机安装 Octave）
```

## 质量保障

`tools/check_book.py` 覆盖：目录与 `toc.js` 一致性、内部链接、HTML 标签配对、页面代码块与 `.m` 同步、Octave 零依赖与代码契约（`IP_HEADLESS`、`printf`、参数区等）、外部链接探测（可选）。

当前本地运行结果：

- `python3 tools/check_book.py` → **29 个 HTML 页面 / 28 个章节 / 24 个 Octave 脚本，0 条错误，0 条提示**
- `IP_HEADLESS=1 ./tools/run_octave.sh` → **24 / 24 脚本通过**

> 说明：静态自检不替代真机运行；数值结论请以本机 GNU Octave 实际输出及权威教材、官方文档为准。

## 约定与边界

- `code/*.m` 是源脚本，纳入版本控制；Octave 运行产物（`octave-workspace`、`*.asv`、`*.log` 等）与本地验证输出由 `.gitignore` 排除。
- 上卷脚本只用 Octave 核心函数、合成测试图像，不需要任何图片素材或第三方包。
- 下卷按设计**不提供本地算法实现**：只给官方开源工程链接与最小复现命令，避免复制一份会过时的训练代码。
- 外部开源工程的版权与许可证归各自维护者所有；本书与这些项目无从属关系。

## 同系列教材

三本教材共用同一套静态站点骨架与「单一数据源 + 自检」维护方式：

| 仓库 | 主题 | 示例形态 |
| --- | --- | --- |
| [analogCircuits](https://github.com/bertowang/analogCircuits) | 模拟电路（本科） | LTspice `.cir` 网表 |
| **imageProcessing**（本仓库） | 数字图像处理（本科到研究生） | GNU Octave `.m` + 开源工程链接 |
| [studyingEconomics](https://github.com/bertowang/studyingEconomics) | 经济学（本科到研究生） | Python 3 标准库 `.py` 建模脚本 |

## 作者与 AI 使用说明

- **作者**：汪亮（bertonwang） · [47608843@qq.com](mailto:47608843@qq.com)
- **AI 使用说明**：本教材的知识框架、正文、Octave 示例代码与开源工程清单在 AI 辅助下整理生成，并经人工校订与静态自检；公式、数值与运行结果请以 GNU Octave 实际输出及权威教材、官方文档为准。发现错漏欢迎通过上方邮箱勘误。

## 许可证

本仓库目前**未附带 `LICENSE` 文件**，尚未声明开源许可证。个人学习与课堂教学可直接阅读、使用页面内容；转载、二次分发或商业使用前请先联系作者。外部参考资料与开源工程的版权归各自维护者所有。
