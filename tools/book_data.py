#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全书章节数据的唯一汇总入口。

按编号段拆成 chapters_*.py 五个文件，编辑时定位更快；本文件只负责汇总与
基本一致性校验。build_book.py / check_book.py 都从这里取 CHAPTERS。
"""
from __future__ import annotations

from chapters_00_04 import CH as CH_00_04
from chapters_05_09 import CH as CH_05_09
from chapters_10_15 import CH as CH_10_15
from chapters_16_21 import CH as CH_16_21
from chapters_22_A import CH as CH_22_A
from book_schema import PARTS, PART_BY_ID

CHAPTERS = CH_00_04 + CH_05_09 + CH_10_15 + CH_16_21 + CH_22_A
BY_ID = {ch["id"]: ch for ch in CHAPTERS}


def problems():
    """返回数据层面的问题列表，供自检脚本使用。"""
    out = []
    ids = [c["id"] for c in CHAPTERS]
    if len(ids) != len(set(ids)):
        out.append("章节 id 重复")
    folders = [c["folder"] for c in CHAPTERS]
    if len(folders) != len(set(folders)):
        out.append("章节目录重复")
    for ch in CHAPTERS:
        p = PART_BY_ID.get(ch["part"])
        if not p:
            out.append("未知分部: " + ch["id"])
            continue
        if not ch["folder"].startswith(p["folder"] + "/") and ch["folder"] != p["folder"]:
            out.append("章节目录与分部不匹配: " + ch["id"] + " -> " + ch["folder"])
        if ch["status"] != "done":
            out.append("章节状态不是 done: " + ch["id"])
        if not ch["goals"] or not ch["points"] or not ch["sections"]:
            out.append("章节缺少目标/知识点/正文: " + ch["id"])
        if p["key"] in ("pre", "upper") and ch["id"] != "A" and not ch["demos"]:
            out.append("上卷章节缺少 Octave 实例: " + ch["id"])
        if p["key"] == "lower" and not ch["repos"]:
            out.append("下卷章节缺少开源工程链接: " + ch["id"])
        for d in ch["demos"]:
            code = d["code"]
            if "IP_HEADLESS" not in code or "printf(" not in code:
                out.append("Octave 示例缺少 headless 开关或数值打印: " + ch["id"])
    return out


def chapters_of(part_id):
    return [c for c in CHAPTERS if c["part"] == part_id]


def demo_count():
    return sum(len(c["demos"]) for c in CHAPTERS)


def repo_count():
    return len({k for c in CHAPTERS for k, _ in c["repos"]})


if __name__ == "__main__":
    print("章节数:", len(CHAPTERS), "| Octave 实例:", demo_count(), "| 不同开源工程:", repo_count())
    for p in PARTS:
        print(p["id"], p["title"], "->", len(chapters_of(p["id"])), "章")
    for x in problems():
        print("问题:", x)
