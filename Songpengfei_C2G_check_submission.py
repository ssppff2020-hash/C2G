#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Songpengfei_C2G_check_submission.py — 提交前完整性 / 一致性自查

用途：在提交前跑一次，自动检查那些"单份文档看不出、合起来才矛盾"的问题。
      这个脚本的存在本身就是一次失败教训的产物：本包曾出现
      Usage_Notes 声称 PENDING 而 submission.json 填 SIMULATED 的自相矛盾，
      以及必交文件名不合规。人工检查会漏，脚本不会。

检查项：
  C1  官方必交文件是否齐全且非空（按 CHALLENGE.md 命名格式）
  C2  submission.json 成绩字段口径自洽（null=PENDING / 数值=REAL，状态串须匹配）
  C3  全包扫描：成绩位置是否残留未标注的模拟值
  C4  submission.tar.gz 是否 < 16MB 硬约束
  C5  口径一致性：各文档是否都指向唯一事实源，未复述数字
  C6  日志目录：模板日志 vs 真实日志的区分是否明确

退出码：0 = 全部通过；1 = 有 FAIL；2 = 仅有 WARN

作者：Songpengfei（真实作者署名，非占位符）
"""

import json
import os
import re
import sys
import tarfile

BUDGET_BYTES = 16_000_000

# 官方 CHALLENGE.md 必交文件（按命名格式）
REQUIRED = [
    "Songpengfei_C2G_方案草案.md",
    "Songpengfei_C2G_方案设计.md",
    "Songpengfei_C2G_train_gpt.py",
    "Songpengfei_C2G_submission.tar.gz",
    "Songpengfei_C2G_submission.json",
    "Songpengfei_C2G_ablation.md",
    "Songpengfei_C2G_leaderboard.md",
    "Songpengfei_C2G_AI日志.md",
    "Songpengfei_C2G_拿来说明.md",
    "Songpengfei_C2G_AAR.md",
]
REQUIRED_DIRS = ["Songpengfei_C2G_logs"]

FAILS, WARNS, OKS = [], [], []


def fail(msg): FAILS.append(msg)
def warn(msg): WARNS.append(msg)
def ok(msg):   OKS.append(msg)


def check_files(base):
    """C1 必交文件齐全且非空"""
    for name in REQUIRED:
        p = os.path.join(base, name)
        if not os.path.isfile(p):
            fail(f"C1 缺失必交文件: {name}")
        elif os.path.getsize(p) == 0:
            fail(f"C1 必交文件为空: {name}")
        else:
            ok(f"C1 {name} ({os.path.getsize(p):,} bytes)")
    for d in REQUIRED_DIRS:
        p = os.path.join(base, d)
        if not os.path.isdir(p):
            fail(f"C1 缺失必交目录: {d}")
        else:
            logs = [f for f in os.listdir(p) if f.startswith("seed_")]
            if len(logs) < 3:
                fail(f"C1 {d} 下 seed 日志不足 3 份（找到 {len(logs)} 份）")
            else:
                ok(f"C1 {d}/ 含 {len(logs)} 份 seed 日志")


def check_submission_json(base):
    """C2 成绩字段口径自洽"""
    p = os.path.join(base, "Songpengfei_C2G_submission.json")
    if not os.path.isfile(p):
        fail("C2 submission.json 不存在，无法检查")
        return None
    try:
        with open(p, "r", encoding="utf-8") as f:
            sub = json.load(f)
    except json.JSONDecodeError as e:
        fail(f"C2 submission.json 不是合法 JSON: {e}")
        return None

    pairs = [
        ("val_bpb", "val_bpb_status"),
        ("std", "std_status"),
        ("artifact_size_bytes", "artifact_size_bytes_status"),
    ]
    for field, status in pairs:
        val = sub.get(field, "<missing>")
        st = str(sub.get(status, ""))
        if val is None:
            if "PENDING" not in st and "未运行" not in st:
                fail(f"C2 {field}=null 但 {status} 未说明为 PENDING/未运行")
            else:
                ok(f"C2 {field}=null，状态串一致（未运行）")
        elif isinstance(val, (int, float)):
            if "REAL" not in st and "真实" not in st:
                fail(f"C2 {field}={val} 是数值，但 {status} 未标注为真实运行结果"
                     "（数值必须来自真实运行）")
            else:
                ok(f"C2 {field}={val}，状态串标注为真实运行")
        else:
            fail(f"C2 {field} 取值类型异常: {type(val).__name__} = {val!r}")

    # 示例块存在时，成绩字段必须仍为 null
    if "format_reference_only" in sub and sub.get("val_bpb") is not None:
        fail("C2 仍存在 format_reference_only 示例块，但成绩字段已填数值 —— "
             "说明回填未走 backfill.py，请核对来源")

    return sub


def check_stray_simulated(base):
    """C3 全包扫描成绩位置的未标注模拟值

    豁免规则：若命中行本身、或前 3 行的上下文里出现下列任一标注，则视为
    已标注（官方公开数字 / 未运行 / 格式示例），不报错。
    加入上下文窗口是因为来源清单里的数字常以「records__.../submission.json：val_bpb=1.08100」
    这种形式出现 —— 来源就在同一行或紧邻的标题行。
    """
    risky = re.compile(
        r"(val_bpb|val_loss|\bBPB\b)\s*[:：=≈]\s*([01]\.\d{3,})", re.I
    )
    exempt_markers = (
        # 明确标注为"非成绩"
        "SIMULATED", "模拟", "示例", "占位", "非成绩", "禁止引用",
        # 明确标注为"未运行"
        "待运行", "未运行", "待填写", "PENDING",
        # 明确标注为"官方公开"
        "官方", "公开", "来源", "records__", "submission.json", "≈",
    )
    WINDOW = 3  # 回看行数，用于捕获"标题行标注 + 内容行数字"的情况
    scan = [f for f in os.listdir(base)
            if f.endswith((".md", ".txt", ".json")) and f != "Songpengfei_C2G_submission.json"]
    hits = 0
    for name in scan:
        p = os.path.join(base, name)
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        for i, line in enumerate(lines, 1):
            for m in risky.finditer(line):
                ctx = "".join(lines[max(0, i - 1 - WINDOW):i])
                if any(k in ctx for k in exempt_markers):
                    continue
                fail(f"C3 {name}:{i} 出现疑似成绩数值 '{m.group(0)}' 且上下文未见标注"
                     "（官方公开 / 未运行 / 格式示例）—— 口径存疑")
                hits += 1
    if hits == 0:
        ok("C3 全包未发现未标注的成绩数值")


def check_tarball(base):
    """C4 tar.gz 体积与内容"""
    p = os.path.join(base, "Songpengfei_C2G_submission.tar.gz")
    if not os.path.isfile(p):
        fail("C4 submission.tar.gz 不存在")
        return
    size = os.path.getsize(p)
    if size > BUDGET_BYTES:
        fail(f"C4 submission.tar.gz {size:,} bytes 超出 16MB 硬约束 (16,000,000 字节)")
    else:
        ok(f"C4 submission.tar.gz {size:,} bytes（上限 16,000,000，余量 {BUDGET_BYTES - size:,}）")

    try:
        with tarfile.open(p, "r:gz") as tf:
            names = tf.getnames()
            nonascii = [n for n in names if any(ord(c) > 127 for c in n)]
            if nonascii:
                # 挑战本身要求中文文件名，故非 ASCII 属预期；仅在提示符下确认未乱码
                warn(f"C4 tar 内含中文文件名（预期，无碍）: {nonascii} —— "
                     "请在 UTF-8 locale 下解压确认未乱码")
            ok(f"C4 tar 内 {len(names)} 个条目")
            # 空文件检查
            for m in tf.getmembers():
                if m.isfile() and m.size == 0:
                    fail(f"C4 tar 内文件为空: {m.name}")
    except tarfile.TarError as e:
        fail(f"C4 submission.tar.gz 无法读取: {e}")


def check_consistency(base):
    """C5 口径一致性：各文档是否声明指向唯一事实源"""
    anchor = "Songpengfei_C2G_submission.json"
    docs = ["README.md", "Songpengfei_C2G_leaderboard.md", "Songpengfei_C2G_ablation.md",
            "Songpengfei_C2G_AAR.md", "Songpengfei_C2G_AI日志.md"]
    missing = []
    for name in docs:
        p = os.path.join(base, name)
        if not os.path.isfile(p):
            continue
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        if anchor not in text and "成绩事实源" not in text and "未运行" not in text:
            missing.append(name)
    if missing:
        warn(f"C5 下列文档未声明成绩口径来源（建议补一句指向 {anchor}）: {missing}")
    else:
        ok("C5 各文档均声明了成绩口径来源")

    # 检查 submission.json 自身是否声明为唯一源
    p = os.path.join(base, "Songpengfei_C2G_submission.json")
    if os.path.isfile(p):
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            if "_score_source_of_truth" in f.read():
                ok("C5 submission.json 已声明为唯一成绩事实源")
            else:
                warn("C5 submission.json 未声明为唯一成绩事实源（建议加 _score_source_of_truth）")


def check_logs(base):
    """C6 日志模板/真实区分"""
    d = os.path.join(base, "Songpengfei_C2G_logs")
    if not os.path.isdir(d):
        return
    for name in sorted(os.listdir(d)):
        if not name.startswith("seed_"):
            continue
        p = os.path.join(d, name)
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        is_template = any(k in text for k in ("SIMULATED", "模拟", "模板", "占位"))
        sub_p = os.path.join(base, "Songpengfei_C2G_submission.json")
        real = False
        if os.path.isfile(sub_p):
            with open(sub_p, "r", encoding="utf-8", errors="replace") as f:
                real = '"val_bpb": null' not in f.read()
        if is_template and real:
            fail(f"C6 {name} 仍为模板日志，但 submission.json 已填真实成绩 —— "
                 "疑似用模板回填，请核对")
        elif is_template:
            ok(f"C6 {name} 标记为模板（与 submission.json 未运行口径一致）")
        else:
            ok(f"C6 {name} 标记为真实日志")


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
    print(f"[check] 检查目录: {base}\n")

    check_files(base)
    check_submission_json(base)
    check_stray_simulated(base)
    check_tarball(base)
    check_consistency(base)
    check_logs(base)

    for m in OKS:
        print(f"  [OK]   {m}")
    for m in WARNS:
        print(f"  [WARN] {m}")
    for m in FAILS:
        print(f"  [FAIL] {m}")

    print(f"\n[check] 汇总: {len(OKS)} OK / {len(WARNS)} WARN / {len(FAILS)} FAIL")
    if FAILS:
        print("[check] 存在 FAIL，禁止提交。")
        sys.exit(1)
    if WARNS:
        print("[check] 无 FAIL，但有 WARN，请人工确认。")
        sys.exit(2)
    print("[check] 全部通过，可以提交。")
    sys.exit(0)


if __name__ == "__main__":
    main()
