#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""静态教材生成器：从结构化章节数据生成全部 HTML 与 assets/toc.js。

单一数据源：
  tools/book_data.py        -> CHAPTERS（章节内容，分散在 chapters_*.py）
  tools/book_schema.py      -> PARTS（分部与上下卷）
  tools/book_resources.py   -> R / TOPIC_RULES / CHAPTER_RESOURCES（链接库）

用法:
  python3 tools/build_book.py            # 生成缺失的章节页（总目录与 toc.js 总是重建）
  python3 tools/build_book.py --force    # 全部重建（会覆盖手工修改的章节页）
  python3 tools/build_book.py --list     # 列出章节清单
"""
from __future__ import annotations

import argparse
import html as html_mod
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from book_schema import PARTS, PART_BY_ID, VOL_PRE, VOL_UPPER, VOL_LOWER, VOL_APP  # noqa: E402
from book_data import CHAPTERS, chapters_of, demo_count, repo_count  # noqa: E402
from book_resources import (R, anchor, links_for_point, chapter_links_html,  # noqa: E402
                            all_resources_html, repo_card)

BOOK_TITLE = "数字图像处理：从经典算法到智能方法"
SUBTITLE = "本科到研究生 · 传统算法与 AI 算法双路线教材"
VERSION = "v0.1 · 2026-11"

STATUS_LABEL = {"done": "已完稿", "skeleton": "框架待补", "todo": "待建"}

CREDITS_HTML = (
    '<p class="credits"><strong>作者</strong>：汪亮（bertonwang）　'
    '<strong>联系邮箱</strong>：<a href="mailto:47608843@qq.com">47608843@qq.com</a></p>\n'
    '<p class="ai-note"><strong>AI 使用说明</strong>：本教材的知识框架、正文、Octave 示例代码与'
    '开源工程清单在 AI 辅助下整理生成，并经人工校订与静态自检。公式、数值与运行结果请以'
    'GNU Octave 实际输出及权威教材、官方文档为准；发现错漏欢迎通过上方邮箱勘误。</p>'
)

RESOURCE_KEYS = [
    "octave", "octave-docs", "skimage", "skimage-docs", "opencv", "opencv-docs",
    "cs231n", "d2l", "pytorch", "pytorch-tutorials", "torchvision", "timm",
    "mmdetection", "mmsegmentation", "hf-diffusers", "paperswithcode",
    "imagenet", "coco", "arxiv", "imagej",
]


def esc(s):
    return html_mod.escape(str(s), quote=False)


def li(items):
    return "\n".join("<li>" + x + "</li>" for x in items)


def head(title, root):
    return [
        "<!DOCTYPE html>", '<html lang="zh-CN">', "<head>", '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>" + esc(title) + " | " + BOOK_TITLE + "</title>",
        '<link rel="stylesheet" href="' + root + 'assets/style.css">',
        '<script src="' + root + 'assets/toc.js" defer></script>',
        '<script src="' + root + 'assets/app.js" defer></script>',
        "</head>",
    ]


def footer(root="../../"):
    return [
        '<footer class="pager" data-autofill></footer>' if root != "./" else "",
        '<footer class="site-foot">', CREDITS_HTML,
        '<p class="imprint">' + BOOK_TITLE +
        ' · 上卷每章一个 <code>code/*.m</code> Octave 脚本（由 <code>tools/extract_code.py</code> 从 HTML 同步）'
        ' · 下卷给出官方开源工程链接 · GNU Octave 为自由软件，本书与之无从属关系。</p>',
        "</footer>", "</main>", "</body>", "</html>",
    ]


# ---------------------------------------------------------------- 目录数据
def toc_js_text():
    parts = []
    for p in PARTS:
        parts.append({
            "id": p["id"], "title": p["title"], "volume": p["volume"],
            "chapters": [
                {"id": c["id"], "title": c["title"],
                 "path": c["folder"] + "/index.html", "status": c["status"]}
                for c in chapters_of(p["id"])
            ],
        })
    data = {"title": BOOK_TITLE, "subtitle": SUBTITLE, "parts": parts}
    flat = (
        "window.BOOK_FLAT = (function () {\n"
        "  const out = [];\n"
        "  (window.BOOK_TOC.parts || []).forEach(function (part) {\n"
        "    (part.chapters || []).forEach(function (ch) {\n"
        "      out.push(Object.assign({ partId: part.id, partTitle: part.title }, ch));\n"
        "    });\n"
        "  });\n"
        "  return out;\n"
        "})();\n"
    )
    return ("/* 由 tools/build_book.py 生成，请勿手工编辑。\n"
            "   目录、侧栏、面包屑、上下章导航共用这一份数据。 */\n"
            "window.BOOK_TOC = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n\n" + flat)


# ---------------------------------------------------------------- 总目录
def toc_entry(c):
    path = c["folder"] + "/index.html"
    out = ["<li>", '<div class="toc-head"><span class="num">' + c["id"] + "</span>"
           '<a class="toc-title" href="' + path + '">' + esc(c["title"]) + "</a> "
           '<a class="toc-extra" href="' + path + '#extra-links">扩展阅读 →</a>'
           '<span class="badge ' + c["status"] + '">' + STATUS_LABEL[c["status"]] + "</span></div>",
           '<p class="toc-desc">' + esc(c["lede"]) + "</p>",
           '<ul class="toc-points">' + "".join("<li>" + esc(p) + "</li>" for p in c["points"]) + "</ul>",
           "</li>"]
    return "\n".join(out)


def toc_html():
    out = []
    banner_upper = banner_lower = False
    for p in PARTS:
        key = p["key"]
        if key == "upper" and not banner_upper:
            out.append('<div class="volume-banner"><h2>上卷 · 传统算法</h2>'
                       '<p>第 03～15 章。原理可推导、代码可运行、结果可手算核对：每章至少配一个零依赖的 '
                       'GNU Octave 实例，输出可验证的数值。</p></div>')
            banner_upper = True
        if key == "lower" and not banner_lower:
            out.append('<div class="volume-banner lower"><h2>下卷 · AI 算法</h2>'
                       '<p>第 16～26 章。原理简介 + 官方开源工程链接 + 最小复现命令；'
                       '重点放在方法脉络、评价指标与工程取舍，而不是重造轮子。</p></div>')
            banner_lower = True
        pid = "卷首" if key == "pre" else ("附录" if key == "appendix" else p["title"].split(" · ")[0])
        out.append('<section class="toc-part"><h2><span class="part-id">' + pid + "</span>" +
                   esc(p["title"].split(" · ", 1)[-1]) + "</h2>")
        out.append('<ul class="toc-list">')
        out.extend(toc_entry(c) for c in chapters_of(p["id"]))
        out.append("</ul></section>")
    return "\n".join(out)


def resource_cards():
    out = ['<div class="repo-grid">']
    for k in RESOURCE_KEYS:
        name, url, desc, cat = R[k]
        out.append('<div class="repo-card"><h3>' + anchor(k, name) + "</h3>"
                   '<span class="tag">' + esc(cat) + "</span>"
                   "<p>" + esc(desc) + "</p>"
                   '<p style="margin:0"><code>' + esc(url) + "</code></p></div>")
    out.append("</div>")
    return "\n".join(out)


def render_index():
    out = head("总目录 · " + BOOK_TITLE, "./")
    out.append('<body data-root="./" data-page="index">')
    out.append('<aside id="sidebar"></aside>')
    out.append('<main class="book-page">')
    out.append('<nav class="breadcrumb" data-autofill>总目录</nav>')
    out.append('<header class="chapter-head">')
    out.append('<span class="kicker">Undergraduate → Graduate · Classical Algorithms + AI</span>')
    out.append("<h1>" + BOOK_TITLE + "</h1>")
    out.append('<p class="lede">一本面向本科到研究生的图像处理教材。全书按'
               '<strong>上卷 · 传统算法</strong>与<strong>下卷 · AI 算法</strong>分为两部分：'
               '上卷把每个算法展开成公式与可运行的 GNU Octave 脚本，下卷给出原理主线与官方开源工程入口。'
               '浏览器打开即可读，复制代码即可验证。</p>')
    out.append('<div class="meta">')
    out.append('<span class="badge done">全部 27 章已完稿</span>')
    out.append('<span class="badge done">上卷每章配可运行 Octave 实例</span>')
    out.append("<span>共 27 章 · 上下两卷 · 1 附录 · " + str(demo_count()) + " 个 Octave 实例 · " +
               str(repo_count()) + " 个开源工程</span>")
    out.append("<span>版本 " + VERSION + "</span>")
    out.append("</div></header>")

    out.append('<div class="card note"><span class="card-label">本书的主张</span>'
               '<p><strong>传统算法</strong>把先验写成公式，<strong>AI 算法</strong>把先验交给数据。'
               '两者不是替代关系：数据增强、退化建模、几何约束、评价指标、后处理全部来自上卷，'
               '而语义鸿沟与可训练表示是下卷要解决的问题。</p>'
               '<p style="margin-bottom:0">上卷的学习闭环固定为四步：'
               '<strong>读公式 → 跑代码 → 改参数 → 写结论</strong>；下卷的闭环是'
               '<strong>读原理 → 跑官方示例 → 换数据集/骨干 → 写消融表</strong>。</p></div>')

    out.append('<h2 id="howto">如何使用这本教材</h2>')
    out.append('<table><thead><tr><th style="width:22%">栏目</th><th>作用</th></tr></thead><tbody>'
               '<tr><td>学习目标</td><td>学完应能做什么，用可检验的动词描述</td></tr>'
               '<tr><td>知识点地图</td><td>逐条列出本章知识点，每条挂 1～2 个扩展学习链接</td></tr>'
               '<tr><td>原理小节 §x.y</td><td>概念、直觉、公式推导、对照表</td></tr>'
               '<tr><td>Octave 实例（上卷）</td><td>完整可运行脚本 + 操作步骤 + 预期数值与判读</td></tr>'
               '<tr><td>开源工程（下卷）</td><td>官方仓库卡片、推荐用法与最小复现命令</td></tr>'
               '<tr><td>常见误区 / 习题</td><td>典型错误与可动手验证的思考题</td></tr>'
               '<tr><td>扩展学习</td><td>本章精读资料、GitHub 检索入口与全书资源总表</td></tr>'
               '</tbody></table>')
    out.append('<p class="code-hint">状态徽章：<span class="badge done">已完稿</span> 表示正文、'
               '知识点地图、扩展链接与实例齐备；总目录每条还提供直达该章扩展学习小节的「扩展阅读 →」。</p>')

    out.append('<h2 id="octave">运行 Octave 示例（30 秒）</h2>')
    out.append('<ol>'
               '<li>安装 <a href="https://octave.org/download" target="_blank" rel="noopener">GNU Octave</a>'
               '（macOS 可用 <code>brew install octave</code>，Linux 用包管理器，Windows 有安装包）。</li>'
               '<li>在任意上卷章节的「Octave 实例」里点代码块右上角的「复制」，保存为 <code>.m</code>；'
               '<strong>或直接使用仓库里同名的 <code>code/*.m</code> 文件</strong>——'
               '它们由 <code>tools/extract_code.py</code> 从 HTML 自动抽取，永远与页面一致。</li>'
               '<li>命令行运行：<code>octave --no-gui --quiet part1/03-gray-transform/code/03-histeq.m</code>。</li>'
               '<li>批量验证全部示例：<code>IP_HEADLESS=1 ./tools/run_octave.sh</code>——不弹图形窗口，'
               '只检查每个脚本能否正常结束并打印数值。</li>'
               '</ol>')
    out.append('<div class="card contract"><span class="card-label">给程序员的代码契约</span>'
               '<ul style="margin-bottom:0">'
               '<li><strong>零依赖</strong>：只用 Octave 核心函数，不调用 image 包的 '
               '<code>imfilter</code>/<code>edge</code>/<code>imresize</code>，算法主体全部展开。</li>'
               '<li><strong>自包含</strong>：用 <code>meshgrid</code> 合成测试图像，不依赖任何外部图片素材。</li>'
               '<li><strong>参数集中</strong>：脚本开头的「参数区」集中所有可调量，先改这里。</li>'
               '<li><strong>数值可核对</strong>：结尾 <code>printf</code> 打印可手算的量，页面给出预期值。</li>'
               '<li><strong>可批量验证</strong>：<code>IP_HEADLESS=1</code> 时跳过绘图。</li>'
               '</ul></div>')

    out.append('<h2 id="roadmap">学习路线（建议两个学期）</h2>')
    out.append('<ol class="roadmap">'
               '<li><strong>阶段 A · 打好共同语言</strong>（卷首 00～02）：Octave 环境、图像即矩阵、'
               '卷积与边界、质量评价。目标：能自己造测试图并预测滤波结果。</li>'
               '<li><strong>阶段 B · 上卷前段：变换与复原</strong>（03～08）：灰度变换、空域/频域滤波、'
               '维纳复原、几何变换、彩色处理。目标：每章能解释参数对输出数值的影响。</li>'
               '<li><strong>阶段 C · 上卷后段：结构与理解</strong>（09～15）：形态学、边缘、特征、分割、'
               '描述、压缩，最后完成一条可交付的颗粒计数流水线。</li>'
               '<li><strong>阶段 D · 下卷：从基线到系统</strong>（16～26）：传统机器学习基线 → CNN 与骨干 → '
               '数据集与评测 → 分类/检测/分割/复原/生成/基础模型 → 部署与综合项目。'
               '目标：能复现官方工程，并完成与传统基线的定量对比。</li>'
               '</ol>')
    out.append('<p>时间有限时的最短路径：<a href="part0/01-octave-setup/index.html">01</a> → '
               '<a href="part0/02-image-basics/index.html">02</a> → '
               '<a href="part1/04-spatial-filter/index.html">04</a> → '
               '<a href="part1/05-frequency-domain/index.html">05</a> → '
               '<a href="part2/15-classical-pipeline/index.html">15</a> → '
               '<a href="part3/17-cnn-fundamentals/index.html">17</a> → '
               '<a href="part3/19-datasets-evaluation/index.html">19</a> → '
               '<a href="part4/26-projects/index.html">26</a>。</p>')

    out.append('<h2 id="toc">全书目录</h2>')
    out.append('<p class="lede">每一章一个文件夹，内含 <code>index.html</code>（知识讲解）；'
               '上卷章节另含 <code>code/*.m</code>（可直接运行的 Octave 脚本）。</p>')
    out.append(toc_html())

    out.append('<h2 id="resources">参考资源</h2>')
    out.append('<p class="lede">以下为全书高频引用的官方文档、课程、数据集与代码库；'
               '完整清单见<a href="appendix/index.html">附录 A.7 扩展学习链接总表</a>。</p>')
    out.append(resource_cards())

    out.append('<h2 id="contribute">维护约定</h2>')
    out.append('<p>全书由结构化数据生成，<strong>不要直接编辑章节 HTML</strong>，'
               '否则下次重建会被覆盖。改完数据后依次运行：'
               '<code>python3 tools/build_book.py --force</code> → '
               '<code>python3 tools/extract_code.py</code> → '
               '<code>python3 tools/check_book.py</code>。</p>')
    out.append('<table><thead><tr><th style="width:26%">想改什么</th><th>编辑哪里</th></tr></thead><tbody>'
               '<tr><td>细化某章正文或 Octave 示例</td><td><code>tools/chapters_*.py</code> 中对应的 <code>C(...)</code></td></tr>'
               '<tr><td>加扩展链接 / 开源工程</td><td><code>tools/book_resources.py</code> 的 '
               '<code>R</code>、<code>TOPIC_RULES</code>、<code>CHAPTER_RESOURCES</code>，以及章节的 <code>repos</code></td></tr>'
               '<tr><td>调整页面结构与总目录</td><td><code>tools/build_book.py</code> 的 <code>render()</code> / <code>render_index()</code></td></tr>'
               '<tr><td>样式与交互</td><td><code>assets/style.css</code>、<code>assets/app.js</code></td></tr>'
               '<tr><td>新增章节或分篇</td><td><code>tools/book_schema.py</code> 的 <code>PARTS</code> + 对应 '
               '<code>chapters_*.py</code>，再重建（<code>toc.js</code> 会自动同步）</td></tr>'
               '<tr><td>验证 Octave 示例</td><td><code>IP_HEADLESS=1 ./tools/run_octave.sh</code>（需本机安装 Octave）</td></tr>'
               '</tbody></table>')

    out.extend([x for x in footer("./") if x])
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- 章节页
def appendix_sections(ch):
    """附录 A.3 / A.7 由全书数据动态生成，保证与其它章节永远一致。"""
    lower = [c for c in CHAPTERS if PART_BY_ID[c["part"]]["key"] == "lower"]
    rows = []
    for c in lower:
        links = " · ".join(anchor(k) for k, _ in c["repos"])
        rows.append("<tr><td><a href='../" + c["folder"] + "/index.html'>第 " + c["id"] +
                    " 章 " + esc(c["title"]) + "</a></td><td>" + links + "</td></tr>")
    a3 = ("<p>下卷各章推荐的官方 / 开源实现，按章节汇总。每张卡片在各章「开源工程」栏目里"
          "还附有推荐用法。</p>"
          '<table><thead><tr><th style="width:26%">章节</th><th>开源工程</th></tr></thead><tbody>' +
          "\n".join(rows) + "</tbody></table>")
    sections = list(ch["sections"])
    sections.append(("A.3", "下卷开源工程总表", a3))
    sections.append(("A.7", "扩展学习链接总表", all_resources_html()))
    return sorted(sections, key=lambda x: x[0])


def render(ch):
    folder = pathlib.PurePosixPath(ch["folder"])
    root = "../" * len(folder.parts)
    part = PART_BY_ID[ch["part"]]
    key = part["key"]
    is_appendix = ch["id"] == "A"
    is_lower = key == "lower"
    chapter_attr = ' data-chapter="' + ch["id"] + '"'
    if is_appendix:
        chapter_attr += ' data-page="appendix"'
    head_title = ("附录 A · " + ch["title"]) if is_appendix else ("第 " + ch["id"] + " 章 · " + ch["title"])

    out = head(head_title, root)
    out.append('<body data-root="' + root + '"' + chapter_attr + ">")
    out.append('<aside id="sidebar"></aside>')
    out.append('<main class="book-page">')
    if is_appendix:
        out.append('<nav class="breadcrumb"><a href="' + root + 'index.html">总目录</a> / 附录</nav>')
    else:
        out.append('<nav class="breadcrumb" data-autofill>总目录</nav>')

    out.append('<header class="chapter-head">')
    out.append('<span class="kicker">' + esc(part["title"]) + "</span>")
    label = "附录 A" if is_appendix else ("第 " + ch["id"] + " 章")
    out.append('<h1><span class="ch-num">' + label + "</span>" + esc(ch["title"]) + "</h1>")
    out.append('<p class="lede">' + esc(ch["lede"]) + "</p>")
    out.append('<div class="meta">')
    out.append('<span class="badge ' + ch["status"] + '">' + STATUS_LABEL[ch["status"]] + "</span>")
    out.append("<span>建议 " + esc(ch["hours"]) + "</span>")
    if is_lower:
        out.append("<span>" + str(len(ch["repos"])) + " 个开源工程</span>")
    else:
        out.append("<span>" + str(len(ch["demos"])) + " 个 Octave 实例</span>")
    out.append('<span class="badge ' + ("lower" if is_lower else "upper") + '">' +
               ("下卷 · AI 算法" if is_lower else "上卷 · 传统算法") + "</span>")
    out.append("<span>" + BOOK_TITLE + "</span>")
    out.append("</div></header>")

    if ch["goals"]:
        out.append('<div class="card objectives"><span class="card-label">学习目标</span><ul>')
        out.append(li([esc(g) for g in ch["goals"]]))
        out.append("</ul></div>")

    out.append('<section id="map"><h2><span class="sec-num">§</span>知识点地图</h2>')
    out.append('<p class="code-hint">每个知识点都配了 1～2 个扩展学习链接；'
               '本章完整资源清单见 <a href="#extra-links">扩展学习</a>。</p>')
    out.append('<table><thead><tr><th style="width:44px">#</th><th style="width:26%">知识点</th>'
               '<th>扩展学习</th><th style="width:100px">状态</th></tr></thead><tbody>')
    for i, p in enumerate(ch["points"], 1):
        out.append("<tr><td>" + str(i) + "</td><td>" + esc(p) + "</td><td>" +
                   links_for_point(ch["id"], p) + "</td><td>正文已覆盖</td></tr>")
    out.append("</tbody></table></section>")

    sections = appendix_sections(ch) if is_appendix else ch["sections"]
    for num, title, body in sections:
        out.append('<section id="s' + num.replace(".", "-") + '"><h2><span class="sec-num">§' +
                   num + "</span>" + esc(title) + "</h2>")
        out.append(body)
        out.append("</section>")

    if is_lower:
        out.append('<section id="repos"><h2><span class="sec-num">§</span>开源工程与实现链接</h2>')
        out.append('<p>本章原理对应的官方 / 开源实现。建议先跑通最小复现命令，'
                   '再按「推荐用法」改动一个变量做对照实验。</p>')
        if ch["repo_note"]:
            out.append('<div class="card tip"><p style="margin-bottom:0">' + esc(ch["repo_note"]) + "</p></div>")
        out.append('<div class="repo-grid">')
        out.extend(repo_card(k, why) for k, why in ch["repos"])
        out.append("</div>")
        out.append('<p class="code-hint">使用约定：以下仓库均为各自维护者的项目，本书与之无从属关系；'
                   '请阅读其 README 与许可证后再用于课程或生产环境。'
                   '更多资源见 <a href="#extra-links">扩展学习</a> 与 '
                   '<a href="' + root + 'appendix/index.html">附录 A.3 开源工程总表</a>。</p>')
        out.append("</section>")
    else:
        out.append('<section id="lab"><h2><span class="sec-num">§</span>Octave 实例</h2>')
        for s in ch["demos"]:
            out.append("<h3>" + esc(s["title"]) + "</h3>")
            out.append('<pre class="code" data-file="' + s["file"] +
                       '" data-lang="GNU Octave"><code>' + esc(s["code"]) + "</code></pre>")
            out.append('<p class="code-hint"><strong>操作：</strong>' + esc(s["steps"]) +
                       "　<strong>预期与判读：</strong>" + esc(s["expect"]) +
                       "　文件位置：<code>" + esc(ch["folder"] + "/" + s["file"]) + "</code></p>")
        out.append('<div class="card note"><p style="margin-bottom:0">代码块右上角可一键复制；'
                   '本仓库 <code>code/*.m</code> 由 <code>tools/extract_code.py</code> 从这些代码块自动抽取，'
                   '页面与脚本永远一致。脚本只用 Octave 核心函数，设 <code>IP_HEADLESS=1</code> 可跳过绘图。</p></div>')
        out.append("</section>")

    if ch["pitfalls"]:
        out.append('<section id="pitfalls"><h2><span class="sec-num">§</span>常见误区</h2>'
                   '<div class="card warn"><ul>' + li([esc(x) for x in ch["pitfalls"]]) + "</ul></div></section>")
    if ch["exercises"]:
        out.append('<section id="exercises"><h2><span class="sec-num">§</span>习题与思考</h2><ol>' +
                   li([esc(x) for x in ch["exercises"]]) + "</ol></section>")
    out.append('<section id="extra-links"><h2><span class="sec-num">§</span>扩展学习</h2>')
    out.append(chapter_links_html(ch["id"], root))
    out.append("</section>")
    if ch["further"]:
        out.append('<section id="further"><h2><span class="sec-num">§</span>延伸阅读与内链</h2><ul>' +
                   li(ch["further"]) + "</ul></section>")

    out.extend([x for x in footer(root) if x])
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- 生成
def build(force=False):
    created, skipped = [], []
    toc_target = ROOT / "assets/toc.js"
    toc_target.write_text(toc_js_text(), encoding="utf-8")
    idx = ROOT / "index.html"
    idx.write_text(render_index(), encoding="utf-8")
    created += ["assets/toc.js", "index.html"]
    for ch in CHAPTERS:
        target = ROOT / ch["folder"] / "index.html"
        if target.exists() and not force:
            skipped.append(str(target.relative_to(ROOT)))
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render(ch), encoding="utf-8")
        created.append(str(target.relative_to(ROOT)))
    return created, skipped


def main():
    ap = argparse.ArgumentParser(description="生成图像处理教材 HTML")
    ap.add_argument("--force", action="store_true", help="覆盖已存在的章节页（会丢失手工修改）")
    ap.add_argument("--list", action="store_true", help="只列出章节清单")
    args = ap.parse_args()
    if args.list:
        for ch in CHAPTERS:
            p = PART_BY_ID[ch["part"]]
            print(ch["id"].rjust(2), p["key"].ljust(9), ch["folder"].ljust(44), ch["title"])
        print("共 %d 章 / %d 个 Octave 实例 / %d 个不同开源工程" %
              (len(CHAPTERS), demo_count(), repo_count()))
        return
    created, skipped = build(force=args.force)
    for p in created:
        print("生成", p)
    print("共 %d 个页面：新建/重建 %d，跳过 %d（章节页使用 --force 可重建）" %
          (len(CHAPTERS) + 1, len(created), len(skipped)))


if __name__ == "__main__":
    main()
