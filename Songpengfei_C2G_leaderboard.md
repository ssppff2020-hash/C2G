---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: e5fb81648b27451c79943c294a107249_0836c921c22711f1887c525400de85a5
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: e5fb81648b27451c79943c294a107249_0836c921c22711f1887c525400de85a5
---

# Songpengfei_C2G_leaderboard.md — BPB 对比榜单

> 作者：Songpengfei（真实作者署名，非占位符）｜最后更新：2026-10-07

> **成绩状态**：本队尚未获得 8×H100 算力，处于官方算力申请流程中。全包唯一成绩事实源为 `Songpengfei_C2G_submission.json`（当前 `val_bpb = null`，未运行）。
> **本表纪律**：下表"官方公开"列的数字全部来自官方 parameter-golf 仓库 `records` 目录，已逐条注明来源，**非本队成绩**；本队列如实标"未运行"，不填任何模拟或估算值。

---

## 1. 官方公开榜单（截至 2026-04-09）

| 排名 | 方案（records 目录名） | 作者 | val_bpb (mean) | std | seeds | 数据/词表 | 关键技术 | 来源 |
|---|---|---|---|---|---|---|---|---|
| 1 | `2026-04-09_SP8192_3LayerRecur_ParResid_QK525_LegalTTT` | bigbag | **1.0810** | 0.00020 | 42/314/999 | FineWeb10B sp8192 | 3 层循环 + 并行残差 + QK-Gain 5.25 + Score-First Legal TTT + GPTQ int6/brotli | 官方 README + submission.json |
| 2 | `2026-04-06_SP8192_QK5_LegalTTT_1.0828` | dexhunter | **1.0828** | — | 42/314/999 | FineWeb10B sp8192 | SP8192 + QK_GAIN_INIT=5.0 + 合法 TTT | 官方 README + submission.json |
| 3 | `2026-04-05_SP8192_GPTQ-Embeddings_SDClip_Loop45x2` | Kevin Clark | **1.0856** | — | 5 seeds | FineWeb10B sp8192 | GPTQ 量化 embeddings + SDClip(12.85/20.0) + Loop45x2 | 官方 README + submission.json |
| 4 | `2026-03-17_NaiveBaseline` | 官方基线 | **1.2244** | — | — | FineWeb10B sp1024 | nanoGPT 风格 9L/512d/KV4，无量化优化 | 官方 README + submission.json |

> 数值口径：1.2244（Baseline submission.json 记录 val_bpb 1.2243657）；1.0810（SOTA submission.json 记录 val_bpb 1.08100, std 0.00020）；1.0828（1.08279384 量级）；1.0856（1.08563 量级）。个别 README 与 submission 的小数位展示差异以官方文件为准。

---

## 2. 挑战级别门槛与本队状态

| Level | 门槛 BPB | 本队状态 |
|---|---|---|
| L1 | < 1.22 | ⏳ 未运行（预期可达：复现 SOTA 即可超出基线 1.2244） |
| L2 | < 1.18 | ⏳ 未运行（预期可达） |
| L3 | < 1.12 | ⏳ 未运行（预期可达） |
| L4 | < 1.085 | ⏳ 未运行（目标：复现 SOTA 1.0810 即满足） |

> 表中"预期可达"为**基于公开材料的判断**，不是成绩承诺；实际状态以 `submission.json` 为准。

---

## 3. 本队方案对比

| 方案 | val_bpb (mean) | std | 与 baseline 差距 | 与 SOTA 差距 | 状态 |
|---|---|---|---|---|---|
| 官方 Naive Baseline（sp1024） | 1.2244 | — | 0 | +0.1434 | 官方公开 |
| 官方 SOTA（bigbag） | 1.0810 | 0.00020 | −0.1434 | 0 | 官方公开 |
| **Songpengfei_C2G v1（复现 SOTA 配置）** | **未运行** | 未运行 | — | — | ⏳ 待 Round 0；阻塞项：算力券 |
| **Songpengfei_C2G v2（合并改进配置）** | **未运行** | 未运行 | — | — | ⏳ 待 Round 1/2 |

> **为什么不填数**：C2G 是打榜类挑战，**不可复现的数字等于无效数字**。本表的空白是真实状态，不是遗漏；回填后每一格都会有对应的真实日志行支撑（`Songpengfei_C2G_logs/seed_*.txt` 的 `quantized_ttt` 行）。
>
> 复现判定标准：与官方 1.08100 偏差 < 0.0005 视为复现成功。

---

## 4. 来源引用清单

1. 官方仓库根 `README.md`：全量榜单与 L1–L4 门槛定义。
2. `records__track_10min_16mb__2026-04-09_SP8192_3LayerRecur_ParResid_QK525_LegalTTT__*/submission.json`：val_bpb=1.08100, std=0.00020, seeds=[42,314,999], author=bigbag, hardware=8xH100。
3. `records__track_10min_16mb__2026-04-06_SP8192_QK5_LegalTTT_1.0828__*/submission.json`：val_bpb≈1.08279, author=dexhunter。
4. `records__track_10min_16mb__2026-04-05_SP8192_GPTQ-Embeddings_SDClip_Loop45x2__*/submission.json`：val_bpb≈1.08563, author=Kevin Clark。
5. `records__track_10min_16mb__2026-03-17_NaiveBaseline__*/submission.json`：val_bpb=1.2243657。
6. 本队成绩事实源：`Songpengfei_C2G_submission.json`（当前 `val_bpb = null`）。

*（本文件由 AI 辅助整理，内容经作者核对；不含任何未经运行的成绩数字。）*
