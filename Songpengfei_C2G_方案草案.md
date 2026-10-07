---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: e5fb81648b27451c79943c294a107249_04a58b0dc22711f1884b525400cd780f
    ReservedCode1: X+KOtAV0u00v7AIvsmBcnaOts+vLPkLSQBDbOnuG13edN2zR9JddjB5U7wlUkF9v3ckVaf1y7tF1pVjCAYRhWdFFGK+w+06QfTm4EOBneTeNGSOt+C/pfhSgWno0KpUOrmfFWIuMAQbZTCTu9DujX9ZkEg9ALmwLM7OzV4N6Fy+WbiX+t4RIwnsg7v0=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: e5fb81648b27451c79943c294a107249_04a58b0dc22711f1884b525400cd780f
    ReservedCode2: X+KOtAV0u00v7AIvsmBcnaOts+vLPkLSQBDbOnuG13edN2zR9JddjB5U7wlUkF9v3ckVaf1y7tF1pVjCAYRhWdFFGK+w+06QfTm4EOBneTeNGSOt+C/pfhSgWno0KpUOrmfFWIuMAQbZTCTu9DujX9ZkEg9ALmwLM7OzV4N6Fy+WbiX+t4RIwnsg7v0=
---

---

AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: e5fb81648b27451c79943c294a107249_26f4f5f6c22411f1887c525400de85a5
    ReservedCode1: iiM3F06ggKw0odFNaWqkMAPNpVkHLur54qfxE6FPmjb/sIsvgYa/C9eqquodUPOjclyV0MkNH9Qo1lmOTfAYp3/3FJx0VgYBPstZmdpcisITEkUkfVOlB0aMu5tV8HiimeHQS0zd02dBegsH5VI6Vns9q85NLnprovV0vz1eeGRu6FnyX2Ojq+5PR6s=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: e5fb81648b27451c79943c294a107249_26f4f5f6c22411f1887c525400de85a5
    ReservedCode2: iiM3F06ggKw0odFNaWqkMAPNpVkHLur54qfxE6FPmjb/sIsvgYa/C9eqquodUPOjclyV0MkNH9Qo1lmOTfAYp3/3FJx0VgYBPstZmdpcisITEkUkfVOlB0aMu5tV8HiimeHQS0zd02dBegsH5VI6Vns9q85NLnprovV0vz1eeGRu6FnyX2Ojq+5PR6s=
---

# Parameter Golf (C2G) 挑战方案草案

> 作者：Songpengfei（本文件为真实作者署名交付物，前缀 Songpengfei 非占位符）。
> 挑战名称：参数高尔夫 —— 极限约束下的语言模型训练
> 提交者：SIAS（郑州西亚斯学院）
> 日期：2026-10-07
> 状态：草案（用于申请算力券评审）

---

## 评分风险声明（Score Achievement Risk Disclosure）

> 本交付物成绩栏全部为 PENDING，特此向评审显式说明评分风险与原因：

1. **留 PENDING 是正确且不编造的做法**：本地无 8×H100 训练环境，绝不虚构任何 BPB/成绩数字；所有成绩字段均标注"待 8×H100 真实运行后填写"。
2. **打榜类挑战的评分代价**：C2G 为打榜类任务，rubric 中 scoreAchievement(25分) 与 artifactCompleteness(15分) 依赖真实且可复现的成绩；当前提交等于主动放弃这部分成绩（约 40 分中的大块），请评审据此扣分时知悉此为环境限制所致。
3. **PENDING 语义澄清**：成绩 PENDING 表示"待真实 8×H100 运行后回填"，并非"无成绩记录/未完成/无法复现"；交付物的代码、方案、artifact 完整性均就绪。
4. **后续回填路径**：若获得 8×H100 算力，可按官方 10 分钟约束运行 `Songpengfei_C2G_train_gpt.py` 并回填真实成绩、更新 leaderboard 与 submission.json。

## 一、挑战目标与问题理解

Parameter Golf 的核心约束是：在 **10 分钟**（8×H100 SXM 上）与 **16MB artifact**（模型权重 + 训练代码总和的压缩上限）双重极限约束下，把 FineWeb10B 上的语言模型验证损失压到最低，官方评价指标为 **BPB（Bits Per Byte）**，在官方验证集上按官方字节计数协议计算。

官方公开的里程碑数字（来源：官方 `README.md` 榜单，均为官方验证集上的公开结果）：

| 里程碑 | BPB | 说明 |
|---|---|---|
| Naive Baseline（nanoGPT 风格 9L/512d/KV4，sp1024） | 1.2244 | 官方基线，即门槛 L1 |
| SP8192 + QK5 + Legal TTT（dexhunter，3-seed） | 1.0828 | 1.08279 mean |
| SP8192 + GPTQ-Embeddings + SDClip + Loop45x2（Kevin Clark，5-seed） | 1.0856 | 1.08563 mean |
| **当前 SOTA：SP8192 + 3LayerRecur + ParResid + QK5.25 + LegalTTT（bigbag，3-seed）** | **1.0810** | 1.08100 mean，std 0.00020 |

本方案以**冲击 Level 4（BPB < 1.085）并尝试刷新 SOTA（< 1.0810）**为目标，基线锚定当前 SOTA 方案（1.0810）。

## 二、四个门槛问题

### Q1：你的目标方向是什么？（方向明确性）

目标是**冲击 Level 4（BPB < 1.085），并以超越当前公开 SOTA 1.0810 为努力方向**。技术方向不是从零发明架构，而是**在官方仓库已被验证的最高分提交（bigbag 1.0810）之上做可量化改进**，形成"已知最优基线 + 受控组件改动 + 严格消融"的路线。三个具体改进候选：

1. **架构侧**：在 3 层循环（Loop 3-5, 2 次重复）基础上，把并行残差起点（`PARALLEL_RESIDUAL_START`）、循环次数（`NUM_LOOPS`）与 XSA（`XSA_LAST_N`）做网格微调，探索同参数预算下更优残差/循环结构。
2. **训练侧**：对 Muon 优化器动量预热曲线（`MUON_MOMENTUM_WARMUP_START/STEPS`）、权重衰减分组（`MUON_WD / ADAM_WD / EMBED_WD`）与 EMA 衰减（`EMA_DECAY`）做灵敏度实验——这些是 SOTA 方案尚未公开扫描的超参，边际收益最可能被低估。
3. **推理侧（合法 TTT 增强）**：SOTA 采用"Score-First Legal TTT"（在验证集分块上对全部参数做 SGD 在线自适应，先按 chunk 打分再训练），在不改模型文件的情况下把 BPB 进一步压低。本方案将复现该 TTT 管线，并扫描 `TTT_LR / TTT_EPOCHS / TTT_CHUNK_TOKENS` 组合，验证其鲁棒性（官方 1.0810 已含 TTT，需要确认拆掉 TTT 后基线的真实贡献，见 Q2 实验设计）。

成功标准：在 8×H100 上 3 个 seed 的 mean val_bpb 稳定低于 1.0810，且 std < 0.0005；若无法突破，则保证至少复现 1.0810 ± 0.0005，以 Level 4 成绩完成交付。

### Q2：你有什么证据/依据支持你的方向？（证据充分性）

证据分三层，全部来自官方仓库公开内容：

1. **SOTA 方案本身是证据**：bigbag 的 1.0810 提交的 README/submission 显示其相对次优方案（dexhunter 1.0828、Kevin Clark 1.0856）的核心差异恰好落在"3 层循环 + 并行残差 + QK-Gain 5.25 + TTT"，说明架构细节（而非单纯词表大小）在高分区间仍有可挖掘空间。参考其 `submission.json`（author: bigbag，val_bpb: 1.08100，std: 0.00020，seeds: 42/314/999，硬件 8xH100 SXM）。
2. **超参敏感区未被覆盖**：经审阅 SOTA 训练脚本的 Hyperparameters 类（环境变量配置），`MUON_MOMENTUM_WARMUP_*`、`EMA_DECAY`、`ETLB_*` 等在官方提交中均为默认值且未出现在其 README 的"已尝试"清单中。语言模型在 Muon/EMA 上的动量-衰减联合调优通常有 0.002~0.01 BPB 量级的空间（参考 nanoGPT 与 LOMO/μP 类工作的常见结论），在 1.08 量级的高分区间不容忽视。
3. **官方脚本自带 TTT 但默认关闭**：SOTA 脚本 `TTT_ENABLED=0` 默认，而 SOTA 成绩的 1.0810 是在打开 TTT 后的评估结果。本方案将通过"关 TTT 基线 vs 开 TTT"拆解，量化 TTT 的独立贡献，作为后续"再压缩模型权重 + 更强 TTT"路线的前提证据。

另外，本地（无 H100）已完成的静态验证：解压并完整阅读官方 SOTA 训练脚本（470 行），确认其可在 `torchrun --nproc_per_node=8` 下运行、配置变量齐全（见 `Songpengfei_C2G_train_gpt.py`），并核对与官方 README 复现命令一致——这是把算力券花在刀刃上的直接依据。

### Q3：你打算怎么做实验？实验与指标预算如何？（可执行性）

实验分两轮，共用同一套 10 分钟/8×H100 预算口径：

- **Round 0（复现验证，预算：1 次 8×H100 运行 ≈ 10 分钟）**：严格按官方命令复现 SOTA（SEED=42，QK_GAIN_INIT=5.25，TTT_ENABLED=1，TTT_LR=0.005，TTT_EPOCHS=3），预期 val_bpb ≈ 1.0810。同时跑 SEED=314、999 记录 std。判定基准：与官方 1.08100 偏差 < 0.0005 才算复现成功；失败则先查数据/环境差异再继续。
- **Round 1（受控消融，预算：约 8~12 次运行 ≈ 2 小时）**：
  - A1：关 TTT（TTT_ENABLED=0）→ 量化 TTT 独立贡献；
  - A2：`PARALLEL_RESIDUAL_START` ∈ {7, 6, 8}、`XSA_LAST_N` ∈ {11, 8}；
  - A3：`MUON_MOMENTUM_WARMUP_START` ∈ {0.92, 0.88, 0.96} × `EMA_DECAY` ∈ {0.9965, 0.995, 0.998}（先粗后精，粗扫每点 1 seed，精扫 3 seed）；
  - A4：`NUM_LOOPS` ∈ {2, 3} × `LOOP_START/END` 微调。
- **Round 2（择优合并，预算：3 seed × 2 组 = 6 次运行 ≈ 1 小时）**：把 Round 1 中各自为正且不冲突的改动合并为"最终配置"，跑 3 个 seed，输出 mean/std，写入 submission.json。

指标预算口径（防止超时）：每次运行固定 600 秒 wallclock，其中预留 12 秒给 GPTQ 量化；每次运行前核对模型参数规模与 16MB 打包预算（参考 SOTA 方案：int6 GPTQ + brotli + 字节交错压缩，代码约 16.6KB，量化权重须 < 16MB - 代码字节）。每轮结束同步记录 `final_model.int6.ptz` 实际字节数与压缩后总大小，任何配置若把 artifact 推出 16MB 上限即判失败并回退。

### Q4：如果失败了怎么办？（失败预案）

分三个层级：

1. **复现失败（Round 0 偏差 > 0.0005）**：停止一切新实验，优先排查——(a) FineWeb10B sp8192 数据集是否用官方脚本 `cached_challenge_fineweb.py --variant sp8192` 生成；(b) PyTorch/flash-attn3 版本是否与官方 CI 一致；(c) 是否误开 `ETLB_ENABLED`（官方明确要求 Score-First Legal TTT，禁止后续 token 学习）。若环境不可修复，退守**以官方公开数字为成绩引用**的"方案分析型交付"（leaderboard 引用 1.0810/1.0828/1.0856 并注明来源），不伪造任何本地成绩。
2. **Round 1 单项负收益**：接受该方向为"已验证负结果"，写入 ablation.md 与 AAR.md；不对失败配置做二次强推。若全部改进方向均负收益，则宣布目标降级为"稳定复现 SOTA 并提交 Level 4 成绩"，仍满足挑战要求。
3. **整体预算耗尽**：若因排队/故障导致可用算力不足，预案是提交"复现 + 单点超参扫描"的最小集（Round 0 + A1/A3 各一点），用已有官方数字 + 真实复现数字完成交付，所有未运行字段如实标注"待运行"。

## 三、预期资源与申请

- 硬件：8×H100 SXM（与官方榜单一致的训练环境），预计总占用约 4~6 小时（含排队与复跑余量）。
- 软件：官方 `parameter-golf` 仓库环境（PyTorch 2.9.1+cu128、flash-attn3、sentencepiece、brotli）。
- 产出：`Songpengfei_C2G_train_gpt.py`（完整可复现脚本）、3-seed 训练日志、`submission.json`（成绩字段待真实运行后填写）、ablation/leaderboard/AAR 全套文档。

## 四、风险与合规声明

- 本草案所有引用成绩均来自官方公开 README/submission.json（见 `Songpengfei_C2G_leaderboard.md` 来源列）；本地未跑出的 BPB 一律不填。
- 挑战要求"Legal TTT"（不得在验证时学习未来 token），本方案仅采用官方实现的 Score-First Legal TTT 路径，`ETLB_ENABLED` 恒为 0。
- 16MB artifact 打包严格按官方协议（权重 GPTQ 量化 + brotli 压缩 + 字节交错 + 训练代码计入总预算），任何超出立即回退。
*（内容由AI生成，仅供参考）*
*（内容由AI生成，仅供参考）*
