#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""章节数据的最小接口与全书分部定义。

章节正文分散在 chapters_*.py 四个文件里，每个文件只 import 本模块，
避免出现循环依赖；build_book.py 再从 book_data.py 取汇总后的 CHAPTERS。
"""
from __future__ import annotations

VOL_PRE = "卷首 · 工具与约定"
VOL_UPPER = "上卷 · 传统算法"
VOL_LOWER = "下卷 · AI 算法"
VOL_APP = "附录"

# id -> (标题, 所属卷, 卷标记)。卷标记决定该章页面用「Octave 实例」还是「开源工程」栏目
PARTS = [
    dict(id="p0", title="卷首 · 工具与约定", volume=VOL_PRE, key="pre", folder="part0"),
    dict(id="p1", title="第一篇 · 基础变换与增强", volume=VOL_UPPER, key="upper", folder="part1"),
    dict(id="p2", title="第二篇 · 结构分析与理解", volume=VOL_UPPER, key="upper", folder="part2"),
    dict(id="p3", title="第三篇 · 从特征到深度网络", volume=VOL_LOWER, key="lower", folder="part3"),
    dict(id="p4", title="第四篇 · 视觉任务与工程落地", volume=VOL_LOWER, key="lower", folder="part4"),
    dict(id="pa", title="附录 · 速查与资源总表", volume=VOL_APP, key="appendix", folder="appendix"),
]
PART_BY_ID = {p["id"]: p for p in PARTS}


def C(cid, part, folder, title, lede, *, hours="2 学时", goals=(), points=(),
      sections=(), demos=(), repos=(), repo_note="", pitfalls=(), exercises=(),
      further=(), status="done"):
    """一章的全部数据。

    sections : [(编号, 标题, HTML 正文), ...]
    demos    : [demo(...), ...]                 上卷/卷首的可运行 Octave 实例
    repos    : [(资源 key, 推荐理由), ...]      下卷的开源工程卡片
    points   : 知识点细目，逐条自动挂扩展学习链接
    """
    return dict(id=cid, part=part, folder=folder, title=title, lede=lede,
                status=status, hours=hours, goals=list(goals), points=list(points),
                sections=list(sections), demos=list(demos), repos=list(repos),
                repo_note=repo_note, pitfalls=list(pitfalls), exercises=list(exercises),
                further=list(further))


def demo(file, title, code, steps, expect):
    """一段零依赖、自包含的 Octave 脚本；file 形如 code/03-gamma.m。"""
    return dict(file=file, title=title, code=code.strip("\n"), steps=steps, expect=expect)


# 常被多个示例复用的脚本骨架：参数区 -> 造图 -> 算法 -> 数值验证 -> 可视化
DEMO_HEAD = """%% {title}
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");   % 一键验证时设 IP_HEADLESS=1 不弹窗
"""
