#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Songpengfei_C2G_backfill.py — 从真实训练日志机械回填 submission.json

用途：在 8xH100 上跑完 3 个 seed (42/314/999) 后，从真实 stdout 日志中
      提取 quantized_ttt 的 val_bpb 与 Total submission size，计算
      mean / sample-std，写入 Songpengfei_C2G_submission.json。

设计原则（重要）：
  本脚本刻意【拒绝】在模板日志上运行。日志中若出现 SIMULATED / 模板 / 占位
  等标记，脚本直接报错退出，不产生任何输出。这是为了防止"用示例数字回填成
  绩"这一历史失败重演 —— 回填必须来自真实运行，且由机械提取而非人工转述。

用法：
  python Songpengfei_C2G_backfill.py [--logs DIR] [--submission FILE] [--dry-run]

默认：
  --logs       Songpengfei_C2G_logs/
  --submission Songpengfei_C2G_submission.json

作者：Songpengfei（真实作者署名，非占位符）
"""

import argparse
import json
import os
import re
import statistics
import sys

SEEDS = [42, 314, 999]
BUDGET_BYTES = 16_000_000  # 官方硬约束：含代码 + 压缩权重 + tokenizer

# 提交口径字段：最终评估路径 quantized_ttt
RE_TTT_BPB = re.compile(r"^\s*quantized_ttt\b.*?\bval_bpb:\s*([0-9]*\.?[0-9]+)", re.M)
# 16MB 预算关键行
RE_SIZE = re.compile(r"^\s*Total submission size\b.*?:\s*([0-9][0-9,]*)\s*bytes", re.M)
# 模板 / 模拟标记：出现即拒绝
FORBIDDEN_MARKERS = ["SIMULATED", "模拟", "模板", "占位", "placeholder", "待运行", "待填写"]


def die(msg: str, code: int = 1):
    print(f"[backfill] 错误: {msg}", file=sys.stderr)
    sys.exit(code)


def read_log(path: str) -> str:
    if not os.path.isfile(path):
        die(f"找不到日志文件: {path}")
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def guard_template(path: str, text: str):
    """模板日志必须拒绝回填 —— 这是本脚本存在的首要理由。"""
    hits = [m for m in FORBIDDEN_MARKERS if m in text]
    if hits:
        die(
            f"{os.path.basename(path)} 含模板/模拟标记 {hits}，"
            "拒绝回填。\n"
            "       本脚本只接受真实 8xH100 运行的 stdout 日志。\n"
            "       请先用真实日志整体替换模板，再执行回填。"
        )


def parse_log(path: str):
    text = read_log(path)
    guard_template(path, text)

    bpb_matches = RE_TTT_BPB.findall(text)
    size_matches = RE_SIZE.findall(text)

    if not bpb_matches:
        die(f"{os.path.basename(path)} 中找不到 quantized_ttt 的 val_bpb 行。"
            "请确认日志完整（应含 'quantized_ttt val_loss: ... val_bpb: ...'）。")
    if not size_matches:
        die(f"{os.path.basename(path)} 中找不到 'Total submission size' 行。")

    # 一个日志可能出现多次 TTT 评估（多轮），取最后一次 = 最终提交口径
    val_bpb = float(bpb_matches[-1])
    size = int(size_matches[-1].replace(",", ""))
    return val_bpb, size


def main():
    ap = argparse.ArgumentParser(description="从真实日志回填 submission.json")
    ap.add_argument("--logs", default="Songpengfei_C2G_logs", help="日志目录")
    ap.add_argument("--submission", default="Songpengfei_C2G_submission.json",
                    help="submission.json 路径")
    ap.add_argument("--dry-run", action="store_true", help="只打印，不写文件")
    args = ap.parse_args()

    print(f"[backfill] 日志目录: {args.logs}")
    results = {}
    for seed in SEEDS:
        path = os.path.join(args.logs, f"seed_{seed}.txt")
        val_bpb, size = parse_log(path)
        results[seed] = {"val_bpb": val_bpb, "size_bytes": size}
        flag = "  <<< 超出 16MB 硬约束!" if size > BUDGET_BYTES else ""
        print(f"  seed {seed:3d}: val_bpb={val_bpb:.5f}  size={size:,} bytes{flag}")

    bpbs = [results[s]["val_bpb"] for s in SEEDS]
    sizes = [results[s]["size_bytes"] for s in SEEDS]
    mean = statistics.fmean(bpbs)
    std = statistics.stdev(bpbs)  # ddof=1，样本标准差
    max_size = max(sizes)

    print(f"\n[backfill] mean val_bpb = {mean:.5f}")
    print(f"[backfill] std  val_bpb = {std:.5f}  (sample std, ddof=1, n=3)")
    print(f"[backfill] max artifact size = {max_size:,} bytes "
          f"({max_size / 1e6:.2f} MB / 16.00 MB budget)")

    # 硬约束检查
    over = [s for s in SEEDS if results[s]["size_bytes"] > BUDGET_BYTES]
    if over:
        die(f"seed {over} 的 artifact 超出 16MB 硬约束 (16,000,000 字节)，禁止提交。"
            "请回退配置或改用官方压缩代码形式释放字节。")

    if args.dry_run:
        print("\n[backfill] --dry-run：未写入任何文件。")
        return

    if not os.path.isfile(args.submission):
        die(f"找不到 {args.submission}")

    with open(args.submission, "r", encoding="utf-8") as f:
        sub = json.load(f)

    # 写入成绩（单一事实源）
    import datetime
    today = datetime.date.today().isoformat()
    sub["date"] = today
    sub["val_bpb"] = round(mean, 5)
    sub["val_bpb_status"] = (
        f"REAL — 8×H100 真实运行回填于 {today}"
        f"（由 backfill.py 从 3 份 seed 日志机械提取，seed={SEEDS}）"
    )
    sub["std"] = round(std, 5)
    sub["std_status"] = "REAL — 3-seed 样本标准差 (ddof=1)，由 backfill.py 计算"
    sub["artifact_size_bytes"] = max_size
    sub["artifact_size_bytes_status"] = (
        f"REAL — 3-seed 中最大打包体积 {max_size:,} bytes（< 16MB 硬约束）"
    )
    sub["submission_stage"] = "STAGE_1_RUN_COMPLETE — 已含真实运行成绩"

    # 回填完成后，示例块失去存在意义，整体移除（防止被误引）
    if "format_reference_only" in sub:
        del sub["format_reference_only"]
        print("[backfill] 已移除 format_reference_only 示例块。")

    with open(args.submission, "w", encoding="utf-8") as f:
        json.dump(sub, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"[backfill] 已写入 {args.submission}")
    print("[backfill] 下一步：python Songpengfei_C2G_check_submission.py")


if __name__ == "__main__":
    main()
