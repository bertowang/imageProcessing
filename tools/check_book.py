#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全书静态自检：目录一致性、内部链接、HTML 标签、代码块与 .m 同步、Octave 代码规范。

用法:
  python3 tools/check_book.py           # 退出码 0 表示全部通过
  python3 tools/check_book.py --urls    # 额外联网探测 book_resources.R 中的 URL
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from book_schema import PART_BY_ID, PARTS  # noqa: E402
from book_data import CHAPTERS, problems  # noqa: E402
from book_resources import R  # noqa: E402
from extract_code import BLOCK, collect  # noqa: E402

VOID_TAGS = {"meta", "link", "br", "hr", "img", "input", "source", "area",
             "base", "col", "embed", "param", "track", "wbr"}
SKIP_SCHEMES = ("http://", "https://", "mailto:", "data:", "#")
STATUS_LABEL = {"done": "已完稿", "skeleton": "框架待补", "todo": "待建"}

# image 包专有函数：出现即破坏「零依赖」约定
BANNED_FUNCS = re.compile(
    r"\b(imfilter|imshow|fspecial|imresize|imrotate|medfilt2|ordfilt|bwlabel|bwmorph|"
    r"rgb2gray|im2double|im2uint8|imhist|graythresh|padarray|nlfilter|strel|"
    r"imerode|imdilate|imfill|imfindcircles|edge|phantom)\s*\(", re.I)

errors = []
warnings = []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def all_pages():
    return sorted(ROOT.rglob("*.html"))


class TagBalance(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.problems = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID_TAGS:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if tag in VOID_TAGS:
            return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        elif tag in self.stack:
            self.problems.append("标签交叉：期望 </%s>，实际 </%s>" % (self.stack[-1], tag))
            while self.stack and self.stack[-1] != tag:
                self.stack.pop()
            if self.stack:
                self.stack.pop()
        else:
            self.problems.append("多余的 </%s>" % tag)


# ---------- 1. 章节数据与 toc.js ----------
for p in problems():
    err("章节数据: " + p)

toc_text = (ROOT / "assets/toc.js").read_text(encoding="utf-8")
try:
    a = toc_text.index("window.BOOK_TOC = ") + len("window.BOOK_TOC = ")
    b = toc_text.index(";\n\nwindow.BOOK_FLAT")
    toc = json.loads(toc_text[a:b])
except (ValueError, json.JSONDecodeError) as e:
    err("无法解析 assets/toc.js: " + str(e))
    toc = {"parts": []}

part_key = {p["id"]: p["key"] for p in PARTS}
toc_items = [(c["path"], c["status"], c["id"], part.get("volume", ""), part_key.get(part["id"], ""))
             for part in toc.get("parts", []) for c in part["chapters"]]
toc_paths = [x[0] for x in toc_items]
if len(toc_paths) != len(CHAPTERS):
    err("toc.js 章节数 (%d) 与 book_data.CHAPTERS (%d) 不一致" % (len(toc_paths), len(CHAPTERS)))
if len(set(toc_paths)) != len(toc_paths):
    err("toc.js 中存在重复 path")
for path in toc_paths:
    if not (ROOT / path).is_file():
        err("toc.js 指向的页面不存在: " + path)

index_text = (ROOT / "index.html").read_text(encoding="utf-8")
index_links = re.findall(r'class="toc-title"\s+href="([^"]+)"', index_text)
for p in toc_paths:
    if p not in index_links:
        err("总目录缺少章节链接: " + p)
for p in index_links:
    if p not in toc_paths:
        err("总目录链接不在 toc.js 中: " + p)
if index_text.count('class="toc-extra"') < len(toc_paths):
    err("总目录中有章节缺少「扩展阅读」入口")
if index_text.count('<span class="badge done">已完稿</span>') < len(toc_paths):
    err("总目录中有章节状态徽章未更新为已完稿")
if 'class="volume-banner"' not in index_text or 'class="volume-banner lower"' not in index_text:
    err("总目录缺少上卷 / 下卷分区标识")

# 状态徽章与 toc.js 一致
for path, status, cid, volume, key in toc_items:
    page_file = ROOT / path
    if not page_file.is_file():
        continue
    badge = '<span class="badge ' + status + '">' + STATUS_LABEL.get(status, "") + "</span>"
    if badge not in page_file.read_text(encoding="utf-8"):
        err("章节页状态徽章与 toc.js 不一致: " + path)


# ---------- 2. 逐页检查 ----------
for page in all_pages():
    text = page.read_text(encoding="utf-8")
    rel = str(page.relative_to(ROOT))
    if 'class="site-foot"' not in text:
        err("缺少页脚: " + rel)
    for token in ("汪亮", "bertonwang", "47608843@qq.com", "AI 使用说明"):
        if token not in text:
            err("页脚缺少署名信息 [%s]: %s" % (token, rel))
    if page.parent != ROOT:
        if 'id="extra-links"' not in text:
            err("缺少扩展学习小节: " + rel)
        if "扩展学习</th>" not in text:
            err("知识点地图缺少扩展学习列: " + rel)
        if "data-chapter=" not in text:
            err("章节页缺少 data-chapter: " + rel)
    if "</html>" not in text:
        err("HTML 未闭合: " + rel)

    # 上下卷栏目
    if rel != "index.html":
        cid = re.search(r'data-chapter="([^"]+)"', text)
        ch = next((c for c in CHAPTERS if c["id"] == (cid.group(1) if cid else "")), None)
        if ch:
            key = PART_BY_ID[ch["part"]]["key"]
            if key == "lower":
                if 'id="repos"' not in text or text.count('class="repo-card"') < 3:
                    err("下卷章节缺少开源工程栏目或卡片: " + rel)
                if 'id="lab"' in text:
                    err("下卷章节不应出现 Octave 实例栏目: " + rel)
            else:
                if 'id="lab"' not in text or 'data-file="code/' not in text:
                    err("上卷章节缺少 Octave 实例栏目: " + rel)

    for attr in re.findall(r'(?:href|src)\s*=\s*(["\'])([^"\']+)\1', text):
        target_url = attr[1]
        if target_url.startswith(SKIP_SCHEMES):
            continue
        path_part = target_url.split("#", 1)[0]
        if not path_part:
            continue
        if not (page.parent / path_part).resolve().exists():
            err("失效链接 %s -> %s" % (rel, target_url))

    parser = TagBalance()
    parser.feed(text)
    parser.close()
    for problem in parser.problems[:5]:
        err("HTML 标签 %s: %s" % (rel, problem))
    if parser.stack:
        err("HTML 标签未闭合 %s: %s" % (rel, ", ".join(parser.stack[:5])))


# ---------- 3. 代码块与 .m 同步 ----------
found = collect()
if not found:
    err("没有抽取到任何 Octave 代码块")
for target, code in sorted(found.items()):
    rel = str(target.relative_to(ROOT))
    if not target.exists():
        err("缺少脚本文件（请运行 extract_code.py）: " + rel)
        continue
    if target.read_text(encoding="utf-8") != code:
        err("脚本与 HTML 代码块不一致: " + rel)


# ---------- 4. Octave 代码规范 ----------
for target in sorted(found):
    rel = str(target.relative_to(ROOT))
    code = target.read_text(encoding="utf-8")
    lines = code.splitlines()
    if not lines or not lines[0].startswith("%%"):
        err("脚本首行应为 %% 注释标题: " + rel)
    for needed in ("IP_HEADLESS", "printf(", "clear; close all; clc;", "参数区"):
        if needed not in code:
            err("Octave 脚本缺少 %s: %s" % (needed, rel))

    def strip_comment(line):
        """只去掉字符串外的 % 注释，避免误删 printf 格式串里的 %.2f 等内容。"""
        out, in_str = [], False
        for ch in line:
            if ch == '"':
                in_str = not in_str
                out.append(ch)
            elif ch == "%" and not in_str:
                break
            else:
                out.append(ch)
        return "".join(out)

    body = "\n".join(strip_comment(l) for l in lines)
    if BANNED_FUNCS.search(body):
        err("Octave 脚本使用了 image 包专有函数（破坏零依赖）: %s -> %s" %
            (rel, BANNED_FUNCS.search(body).group(1)))
    for op, cl in (("(", ")"), ("[", "]")):
        if body.count(op) != body.count(cl):
            warn("括号数量不平衡 %s%s: %s" % (op, cl, rel))


# ---------- 5. 资源链接（可选联网探测） ----------
def probe(item):
    """区分可达 / 反爬拦截 / 疑似失效 / 本环境不可达四类结果。"""
    key, (name, url, _desc, _cat) = item
    last = "unknown"
    for _attempt in range(2):  # 第一次超时多为并发限流，重试一次再判定
        for method in ("HEAD", "GET"):
            try:
                req = urllib.request.Request(url, method=method,
                                             headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=6) as r:
                    return key, r.status, "", "ok"
            except urllib.error.HTTPError as e:
                if e.code in (404, 410):
                    return key, e.code, str(e)[:60], "bad"
                return key, e.code, "HTTP %d" % e.code, "blocked"
            except Exception as e:  # noqa: BLE001
                last = str(e)[:70]
    return key, 0, last, "unreachable"


# ---------- 6. 报告 ----------
ap = argparse.ArgumentParser(description="图像处理教材静态自检")
ap.add_argument("--urls", action="store_true", help="联网探测全部外部链接（需要网络）")
args = ap.parse_args()

if args.urls:
    with ThreadPoolExecutor(max_workers=8) as ex:
        results = list(ex.map(probe, R.items()))
    bad = [r for r in results if r[3] == "bad"]
    blocked = [r for r in results if r[3] == "blocked"]
    unreachable = [r for r in results if r[3] == "unreachable"]
    wiki = [r for r in unreachable if "wikipedia.org" in R[r[0]][1]]
    for k, s, e, _ in bad:
        warn("疑似失效链接 [%s] %s (%s)" % (k, R[k][1], e))
    for k, s, e, _ in unreachable:
        if "wikipedia.org" not in R[k][1]:
            warn("本环境不可达，需人工确认 [%s] %s (%s)" % (k, R[k][1], e))
    print("链接探测：%d 条，可达 %d，反爬拦截 %d，本环境不可达 %d（wikipedia.org %d），疑似失效 %d" %
          (len(results), len(results) - len(bad) - len(blocked) - len(unreachable),
           len(blocked), len(unreachable), len(wiki), len(bad)))

for w in warnings:
    print("提示:", w)
for e in errors:
    print("错误:", e)
print("自检：%d 个 HTML 页面，%d 个章节，%d 个 Octave 脚本，%d 条错误，%d 条提示" %
      (len(all_pages()), len(CHAPTERS), len(found), len(errors), len(warnings)))
sys.exit(1 if errors else 0)
