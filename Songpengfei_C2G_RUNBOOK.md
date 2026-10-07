---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: e5fb81648b27451c79943c294a107249_26f4f5f6c22411f1887c525400de85a5
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: e5fb81648b27451c79943c294a107249_26f4f5f6c22411f1887c525400de85a5
---

# Songpengfei_C2G_RUNBOOK.md — 算力到位后的开跑手册

> 作者：Songpengfei（真实作者署名，非占位符）
> 目的：把"拿到算力券 → 跑完 → 回填 → 提交"压缩到 **1 个工作日**内完成。
> 前置：本手册假定你**已获得 8×H100 算力**。若尚未获得，见 `Songpengfei_C2G_方案草案.md` 的申请流程。

> **成绩状态**：本队尚未获得 8×H100 算力。全包唯一成绩事实源为 `Songpengfei_C2G_submission.json`（当前 `val_bpb = null`，未运行）。

---

## §0. 开跑前检查（5 分钟）

- [ ] 已有 8×H100 SXM 环境，且可 SSH / 提交作业
- [ ] 券额余量 ≥ 计划运行次数（Level 1：1–3 次；见方案草案 Q3）
- [ ] FineWeb10B 缓存已就位，**variant 必须是 sp8192**
- [ ] 已阅读 §4 的合规红线

---

## §1. 环境安装

```bash
pip install numpy sentencepiece brotli

pip install torch==2.9.1+cu128 --index-url https://download.pytorch.org/whl/cu128

pip install flash_attn_3 --no-deps \
  --find-links https://windreamer.github.io/flash-attention3-wheels/cu128_torch291/

# 校验
python -c "import torch, flash_attn_interface, sentencepiece, brotli; print('deps OK', torch.__version__)"
```

**数据准备**（若缓存缺失）—— 必须用官方脚本，variant 不匹配是复现失败的头号根因：

```bash
python cached_challenge_fineweb.py --variant sp8192
```

---

## §2. 运行 Round 0（复现）

```bash
# R0-a  seed 42
SEED=42 QK_GAIN_INIT=5.25 TTT_ENABLED=1 TTT_LR=0.005 TTT_EPOCHS=3 \
  torchrun --standalone --nproc_per_node=8 Songpengfei_C2G_train_gpt.py \
  2>&1 | tee Songpengfei_C2G_logs/seed_42.txt

# R0-b  seed 314
SEED=314 QK_GAIN_INIT=5.25 TTT_ENABLED=1 TTT_LR=0.005 TTT_EPOCHS=3 \
  torchrun --standalone --nproc_per_node=8 Songpengfei_C2G_train_gpt.py \
  2>&1 | tee Songpengfei_C2G_logs/seed_314.txt

# R0-c  seed 999
SEED=999 QK_GAIN_INIT=5.25 TTT_ENABLED=1 TTT_LR=0.005 TTT_EPOCHS=3 \
  torchrun --standalone --nproc_per_node=8 Songpengfei_C2G_train_gpt.py \
  2>&1 | tee Songpengfei_C2G_logs/seed_999.txt
```

> ⚠️ **必须用 `tee` 而不是 `>`**：日志要同时进文件和屏幕，若中途崩溃你还能看到最后一行。

**券额只够一次跑时**：只跑 R0-a，然后在 §3 回填时如实说明"1 seed 复现，3-seed 统计量顺延 Level 2"。**不要用 1 个 seed 冒充 3 个。**

---

## §3. 回填（15 分钟）

```bash
# 先用 dry-run 看一眼提取结果对不对
python Songpengfei_C2G_backfill.py --dry-run

# 确认无误后正式回填
python Songpengfei_C2G_backfill.py
```

脚本会：
1. 从 3 份日志中机械提取 `quantized_ttt` 的 `val_bpb` 与 `Total submission size`；
2. 计算 mean 与样本标准差 (ddof=1)；
3. 校验 artifact < 16MB（超限直接报错退出，不写入）；
4. 写回 `submission.json`，并把成绩状态串改为 `REAL`；
5. 删除 `format_reference_only` 示例块（回填后它已无意义且可能被误引）。

> **安全设计**：脚本**拒绝**在模板日志上运行。若日志里还有 `SIMULATED` / `模板` 等标记，它会直接报错退出——防止"用示例数字回填成绩"这一历史失败重演。

**回填后必做的判定**：

| 判据 | 结论 | 下一步 |
|---|---|---|
| \|val_bpb − 1.08100\| < 0.0005 | ✅ 复现成功 | 更新 leaderboard，申请 Level 2 |
| 偏差 ≥ 0.0005 | ❌ 复现失败 | 见 §5 排查；仍不通过则退守方案分析型交付 |

---

## §4. 合规红线（不可越）

1. `ETLB_ENABLED` **必须恒为 0** —— TTT 只能走官方 Score-First Legal 路径，不得在验证阶段学习未来 token。
2. 提交口径**只用 `quantized_ttt` 那一行**的 val_bpb，不要用 `quantized` 或 `pre-quantization post-ema`。
3. 16MB 是**含训练代码 + 压缩权重 + tokenizer** 的总和，不是只有权重。
4. 3 份日志必须是**真实 stdout 原样**，不得编辑数值、不得删行。

---

## §5. 复现失败排查顺序（按此顺序，别跳）

1. **数据 variant**：是否用官方脚本 `--variant sp8192` 生成？（最高频根因）
2. **版本**：PyTorch 是否 2.9.1+cu128？flash-attn3 是否 cu128_torch291 wheel？
3. **合规开关**：`ETLB_ENABLED` 是否为 0？误开会污染 TTT 与成绩。
4. **有效步数**：10 分钟内是否真跑满 20000 步？卡间通信异常会显著减少步数。
5. **打包口径**：`Total submission size` 是否包含了代码字节？

若四项均正常且偏差仍 > 0.0005，记录现象，按 AAR §4 的四段式写失败案例，退守方案分析型交付。

---

## §6. 提交前（10 分钟）

```bash
python Songpengfei_C2G_check_submission.py
```

退出码 0 才可提交。然后逐项确认：

- [ ] `check_submission.py` 输出 0 FAIL
- [ ] `submission.json` 三个成绩字段均为 `REAL` 且有对应状态串
- [ ] `format_reference_only` 块已被 backfill 删除
- [ ] 3 份日志为真实 stdout（无 SIMULATED / 模板残留）
- [ ] `submission.tar.gz` < 16,000,000 字节
- [ ] `leaderboard.md` / `ablation.md` 已用真实数字替换"待运行"
- [ ] `AAR.md` §4 已按四段式追加真实训练阶段的失败案例（含负结果）
- [ ] 官方必交文件名逐条核对（见 `check_submission.py` 的 C1 项）

---

## §7. 时间预算

| 步骤 | 预计 |
|---|---|
| §0 开跑前检查 | 5 min |
| §1 环境安装 + 数据 | 30–60 min（视镜像/带宽） |
| §2 Round 0 运行 | 3 × 12 min ≈ 36 min（含量化与评估） |
| §3 回填 | 15 min |
| §4–§5（仅失败时） | 0.5–2 h |
| §6 提交前检查 | 10 min |
| **合计（顺利）** | **≈ 2 小时** |

---

## §8. 拿到算力后要更新的文件清单

| 文件 | 更新内容 | 工具 |
|---|---|---|
| `submission.json` | 三个成绩字段 + 状态串 | `backfill.py` 自动 |
| `logs/seed_*.txt` | 模板 → 真实 stdout | `tee` 直接覆盖 |
| `leaderboard.md` | "待运行" → 真实 mean/std | 手工 |
| `ablation.md` | "待运行" → 真实 Δ（消融阶段才填） | 手工 |
| `AAR.md` §4 | 追加真实训练阶段失败案例 | 手工，四段式 |
| `README.md` §0 | 成绩状态声明改为已完成 | 手工 |
| `submission.tar.gz` | 放入真实 artifact | `pack_artifact.py` |

*（本手册由 AI 辅助整理，内容经作者核对。）*
