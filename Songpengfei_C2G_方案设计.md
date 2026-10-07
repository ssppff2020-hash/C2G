---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: e5fb81648b27451c79943c294a107249_05b37380c22711f1887c525400de85a5
    ReservedCode1: EPRruJYV2XvwbOFXGvuSAZM3788lJhAVfOv5YNfAdLP2zDNT2+91//bax/xPHMIZLuytkYXqrkBuGQqBl6uNaDsMntZrzMSI23KqbglUMoQwLOE29vFhvbxah3CStpqcB54ZrSM8vHIyQGWX58TotqPv6oMz7Xq4+boimDlPxXHyh4AM/Kv9GA3nhMo=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: e5fb81648b27451c79943c294a107249_05b37380c22711f1887c525400de85a5
    ReservedCode2: EPRruJYV2XvwbOFXGvuSAZM3788lJhAVfOv5YNfAdLP2zDNT2+91//bax/xPHMIZLuytkYXqrkBuGQqBl6uNaDsMntZrzMSI23KqbglUMoQwLOE29vFhvbxah3CStpqcB54ZrSM8vHIyQGWX58TotqPv6oMz7Xq4+boimDlPxXHyh4AM/Kv9GA3nhMo=
---

---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: e5fb81648b27451c79943c294a107249_280a2c1ec22411f1887c525400de85a5
    ReservedCode1: 2oE7cUH823gq7jfOrn1AFwN2PvvT/CQG8c4QgHQ7M+/7SzCPXFQ4Mzh7H8800eVqNDgywShoev/SG1TJMCs/C7JiPf2rQ1EqEUImK4QylR+x2Vq171NqkHhSnHPcbJOCBb9vRrciBi3zIB2lxeqFgwA0VtWrCNoY4BJ8d5BcAyzNvvjNpN5yM8nhp0o=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: e5fb81648b27451c79943c294a107249_280a2c1ec22411f1887c525400de85a5
    ReservedCode2: 2oE7cUH823gq7jfOrn1AFwN2PvvT/CQG8c4QgHQ7M+/7SzCPXFQ4Mzh7H8800eVqNDgywShoev/SG1TJMCs/C7JiPf2rQ1EqEUImK4QylR+x2Vq171NqkHhSnHPcbJOCBb9vRrciBi3zIB2lxeqFgwA0VtWrCNoY4BJ8d5BcAyzNvvjNpN5yM8nhp0o=
---

# Songpengfei_C2G_Design_Doc.md — Parameter Golf (C2G) 技术方案设计

> 作者：Songpengfei（本文件为真实作者署名交付物，前缀 Songpengfei 非占位符）。
> 目标：在 10 分钟 / 8×H100 / 16MB artifact 三重约束下冲击 Level 4（BPB < 1.085），并尝试刷新 SOTA（当前 1.0810）。
> 本文档与 `Songpengfei_C2G_train_gpt.py`、`Songpengfei_C2G_Proposal_Draft.md`、`Songpengfei_C2G_ablation.md` 配套阅读。

---

> **成绩状态**：本队尚未获得 8×H100 算力，处于官方算力申请流程中。全包唯一成绩事实源为 `Songpengfei_C2G_submission.json`（当前 `val_bpb = null`，未运行）。本文档不出现任何被当作成绩引用的数字。

## 1. 目标 Level 与评价口径

| 级别 | 门槛（BPB） | 本方案目标 |
|---|---|---|
| L1 | < 1.22（官方基线 1.2244） | — |
| L2 | < 1.18 | — |
| L3 | < 1.12 | — |
| L4 | < 1.085 | ✅ 主目标：mean val_bpb < 1.085，力争 < 1.0810 |

- 评价指标：官方验证集 BPB（Bits Per Byte），按官方字节计数协议（SentencePiece `▁` 前缀字节数 + 边界 token 修正）计算；成绩取 3 个固定 seed（42/314/999）的 mean 与 std。
- 成绩引用纪律：本地未真实跑出的数字一律不填；文档中出现的 1.2244 / 1.0810 / 1.0828 / 1.0856 均为官方公开数字并逐一注明来源。

## 2. 总体策略

**"已知最优基线 + 受控超参/结构改进 + 严格消融"**。以官方仓库当前 SOTA 提交（bigbag，SP8192 + 3LayerRecur + Parallel Residuals + QK5.25 + Legal TTT，1.0810）为起点，不做激进重构（激进重构在 10 分钟预算内风险极高），只在三处被官方 README 标注为"未扫描/未披露"的维度做边际改进：

1. **训练超参（主攻轴，Level 1–2 唯一投入预算的轴）**：Muon 动量预热、EMA 衰减、权重衰减分组（官方脚本已暴露为环境变量但未在提交 README 中披露扫描结果）。
2. **结构细节（后置，Level 3 再评估）**：并行残差起点、XSA 层数、循环深度（均已有环境变量开关，改动成本低、可精确消融）。
3. **评估侧（部分可附带）**：Score-First Legal TTT 的超参（LR/epochs/chunk）与"关 TTT"对照，量化其对最终成绩的贡献边界。

> **分阶段投入的理由**：结构改动会同时改变参数量与 16MB 预算，破坏受控对照，无法把 BPB 变化归因到单一变量；而优化器超参全部是独立环境变量，注入后不改变模型结构与体积，是唯一能做到纯单变量的轴。因此主攻轴 1，轴 2/3 后置。完整论证见 `Songpengfei_C2G_方案草案.md` Q1。

## 3. 技术选型

### 3.1 Tokenizer

- **选择：SentencePiece BPE，词表 8192（sp8192）**。
- 依据：官方榜单前三方案全部使用 sp8192 词表（Baseline 用 sp1024，BPB 1.2244 明显劣势）。更大的词表（如 sp16k）在 16MB artifact 下会显著挤压权重预算；sp8192 是官方数据管线直接支持的最高分词表档位，无需自训练 tokenizer，复现成本最低。

### 3.2 Architecture

基于官方 SOTA 架构（详见 `Songpengfei_C2G_train_gpt.py` 与 `Songpengfei_C2G_Usage_Notes.md`）：

| 组件 | 配置 | 说明 |
|---|---|---|
| 层数 | 11 层（enc/dec 拆分） | SOTA 口径 |
| 模型维度 | 512（embedding 512，head_proj 连接） | — |
| 注意力 | 8 heads × 64 head_dim，4 KV heads，GQA | — |
| MLP | 4× 隐藏，LeakyReLU(0.5)²（Squared ReLU 变体） | — |
| 循环 | 3 层循环（LOOP_START=3, LOOP_END=5, NUM_LOOPS=2），训练中 frac≥0.35 时启用 | 关键得分点 |
| 残差 | 并行残差（PARALLEL_RESIDUAL_START=7）+ attn/mlp scale + resid_mix | 关键得分点 |
| XSA | 后 XSA_LAST_N=11 层启用（消融变量） | — |
| QK 增益 | q_gain 初始化 5.25（QK_GAIN_INIT） | 关键得分点 |
| 其他 | RMSNorm + LN_Scale、RoPE(16 dims, base 1e4)、logit softcap 30、tied embeddings | SOTA 口径 |

**拟消融的结构变量**：`PARALLEL_RESIDUAL_START ∈ {6,7,8}`、`XSA_LAST_N ∈ {8,11}`、`NUM_LOOPS ∈ {2,3}`、`LOOP_START/END` 微调。

### 3.3 Optimizer

- **主优化器：Muon**（矩阵参数，正交化 + 动量 + 行列范数归一，Newton-Schulz 5 步），`MATRIX_LR=0.022`，`MUON_WD=0.095`，动量 0.99（含 0.92→0.99 预热 1500 步）。
- **辅助优化器：AdamW** 分三组：
  - token embedding（`TIED_EMBED_LR=0.03`，`EMBED_WD=0.085`，tied 初始化 std 0.005）；
  - scalar/控制参数（`SCALAR_LR=0.02`，`ADAM_WD=0.02`）：attn_scale / mlp_scale / resid_mix / q_gain / skip_weights / skip_gates；
  - 非 tied 时 lm_head（`HEAD_LR=0.008`，Adam 无 WD）。
- **LR 调度**：warmup 20 步 + warmdown 72% 余弦式衰减至 MIN_LR=0；EMA 衰减 0.9965（消融变量）。
- **拟消融**：`MUON_MOMENTUM_WARMUP_START ∈ {0.88,0.92,0.96}`、`MUON_MOMENTUM_WARMUP_STEPS ∈ {1000,1500,2000}`、`EMA_DECAY ∈ {0.995,0.9965,0.998}`、`MUON_WD ∈ {0.07,0.095,0.12}`。

### 3.4 Quantization & Artifact Packing

- **量化：GPTQ 混合精度**——矩阵权重 int6（clip ±63σ，12.85σ 裁剪）、embedding int8（20σ 裁剪）、小块顺序误差补偿（block_size=128），小于 65536 参数的张量 float16 直通。
- **压缩：brotli quality=11 + 字节交错（stride=2）**，官方 SOTA 实测量化权重 + 代码 < 16MB。
- **协议**：`serialize()` 输出 `final_model.int6.ptz`；总预算 = 量化权重字节 + 训练代码字节（本脚本约 50KB，远超官方压缩版 16.6KB，若审计严格需在提交前将本脚本重新压缩为 lzma+b85 单行形式以贴近官方口径——见 `Songpengfei_C2G_submission.tar.gz` 内 pack_artifact.py 的说明）。
- 校准：训练后用 64 个 calibration batch 收集 Hessian（预留 12s）。

### 3.5 Training Loop

- 数据：FineWeb10B 官方缓存（sp8192），`TRAIN_BATCH_TOKENS=786432`，`TRAIN_SEQ_LEN=2048`，grad_accum = 8//world_size，8 卡各持 0.5M tokens/step。
- 时长：`ITERATIONS=20000`，`MAX_WALLCLOCK_SECONDS=600`（预留 12s 给 GPTQ）；`WARMUP_STEPS=20`（含循环结构 warmup 阶段，warmup 后恢复初态）。
- 验证：`VAL_LOSS_EVERY=4000`，最终评估含 pre-quantization post-EMA / quantized / quantized_sliding_window / quantized_ttt 四条路径，BPB 以官方口径取 sliding + TTT 路径为准。

### 3.6 Artifact Packing（提交物）

| 文件 | 说明 |
|---|---|
| `final_model.int6.ptz` | 量化权重（brotli + 字节交错），训练时自动产出 |
| `train_gpt.py`（压缩单行版） | 训练代码计入 16MB 预算 |
| `submission.json` | 元数据 + val_bpb/std/seeds/硬件/时间 |

## 4. 实验矩阵设计

统一口径：8×H100，600s/run；成绩 = 3-seed mean(std)，粗扫 1-seed、精扫 3-seed。

### Round 0 — 复现验证（1 次运行 + 2 次补跑）

| ID | 配置 | seed | 目的 | 判定 |
|---|---|---|---|---|
| R0 | SOTA 全默认 + QK5.25 + TTT on | 42, 314, 999 | 复现 1.0810 | \|Δ\| < 0.0005 |

### Round 1 — 受控消融（12 点，粗扫 1-seed，正收益项 3-seed 精扫）

| ID | 变量 | 取值 | 固定其余 |
|---|---|---|---|
| A1 | TTT_ENABLED | 0 / 1 | 拆解 TTT 独立贡献 |
| A2 | PARALLEL_RESIDUAL_START | 6, 7, 8 | — |
| A3 | XSA_LAST_N | 8, 11 | — |
| A4 | NUM_LOOPS × LOOP 区间 | 2×(3-5), 3×(3-5) | — |
| A5 | MUON_MOMENTUM_WARMUP_START | 0.88, 0.92, 0.96 | — |
| A6 | EMA_DECAY | 0.995, 0.9965, 0.998 | — |
| A7 | MUON_WD | 0.07, 0.095, 0.12 | — |
| A8 | TTT_LR × TTT_EPOCHS | 0.0025/0.005/0.01 × 2/3/5（仅正收益区精扫） | — |

### Round 2 — 择优合并（2 组 × 3 seed）

| ID | 组合 | 说明 |
|---|---|---|
| M1 | 全部正收益项合并 | 若交互效应为负则拆分为 M2 |
| M2 | 仅训练超参组合（不动架构） | 备份路线 |

### 判定与门槛

- 每项消融的"正收益"定义：单点 BPB 相对 R0 复现值改善 > 0.0005 且非孤点噪声（相邻点同向）。
- 每轮结束必须记录 artifact 总字节数；>16MB 即失败回退。
- 全部结果写入 `Songpengfei_C2G_ablation.md`（含统计显著性框架）与 `Songpengfei_C2G_leaderboard.md`。

## 5. 交付清单映射

| 挑战要求 | 本包文件 |
|---|---|
| 方案草案（4 门槛问题） | `Songpengfei_C2G_Proposal_Draft.md` |
| 方案设计 | 本文档 |
| 训练脚本（可复现） | `Songpengfei_C2G_train_gpt.py` |
| 提交元数据 | `Songpengfei_C2G_submission.json` |
| 16MB artifact 打包 | `Songpengfei_C2G_submission.tar.gz`（脚本 + 清单 + 说明） |
| 训练日志 | `Songpengfei_C2G_logs/`（3-seed 模板 + 说明） |
| 消融报告 | `Songpengfei_C2G_ablation.md` |
| 榜单对比 | `Songpengfei_C2G_leaderboard.md` |
| AI 使用日志 | `Songpengfei_C2G_AI_Log.md` |
| 拿来说明 | `Songpengfei_C2G_Usage_Notes.md` |
| 复盘 | `Songpengfei_C2G_AAR.md` |
*（内容由AI生成，仅供参考）*
*（内容由AI生成，仅供参考）*
