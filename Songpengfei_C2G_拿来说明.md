---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: e5fb81648b27451c79943c294a107249_09e33a64c22711f1884b525400cd780f
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: e5fb81648b27451c79943c294a107249_09e33a64c22711f1884b525400cd780f
---

# Songpengfei_C2G_拿来说明.md — 从 nanoGPT / 官方 repo / 历史 top 方案拿了什么、改了什么、为什么改

> 作者：Songpengfei（真实作者署名，非占位符）
> 本文件按挑战必交清单命名（`姓名_C2G_拿来说明.md`）。训练代码完整来源声明见 `Songpengfei_C2G_train_gpt.py` 头部注释。

> **成绩状态**：本队尚未获得 8×H100 算力，处于官方算力申请流程中。全包唯一成绩事实源为 `Songpengfei_C2G_submission.json`（当前 `val_bpb = null`，未运行）。本文档不出现任何被当作成绩引用的数字。

---

## 0. 一句话总结

**本方案没有发明新算法。** 它的全部价值在于：站在官方已公开的最高分提交（bigbag 1.0810）之上，把**未被公开扫描过的超参维度**找出来，用受控消融量化它们的边际贡献。这是"承认前人成果 + 精确指出残余空间"的做法，而非重造轮子。

---

## 1. 总体来源图谱

```
nanoGPT (Karpathy, 2022)
   └─ 基础 GPT 训练循环 / 数据分片格式 / 交叉熵
        └─ parameter-golf 官方 repo（挑战约束化改造）
             ├─ NaiveBaseline（官方基线，1.2244）：9L/512d/KV4, sp1024
             ├─ dexhunter（1.0828）：SP8192 + QK-Gain 5.0 + 合法 TTT
             ├─ Kevin Clark（1.0856）：GPTQ-Embeddings + SDClip + Loop45x2
             └─ bigbag SOTA（1.0810）：3LayerRecur + ParResid + QK5.25 + LegalTTT  ← 本方案基线
```

---

## 2. 从 nanoGPT 拿了什么

| 组件 | 来源 | 改动 | 为什么 |
|---|---|---|---|
| GPT 语言建模范式（embedding → transformer → lm_head → cross-entropy） | nanoGPT | 保留核心 | 挑战本质仍是语言模型训练，范式不变 |
| `.bin` 数据分片格式（256×int32 头 + uint16 tokens） | nanoGPT 数据集处理 | 保留并做严格校验（magic / 版本 / token 数 / 文件大小） | 官方 FineWeb10B 缓存沿用该格式；格式校验是复现失败的头号防线 |
| 训练循环骨架（forward / backward / step / log / eval） | nanoGPT | 大幅改造（见 §4） | 满足 10 分钟 wallclock + 多卡 + 量化打包约束 |
| AdamW 用法 | nanoGPT | 分组改造 | 官方 SOTA 用 Muon 作主优化 + AdamW 辅组 |

---

## 3. 从官方 repo / 历史 top 方案拿了什么

| 组件 | 来源方案 | 改动 | 为什么 |
|---|---|---|---|
| `Hyperparameters` 环境变量配置体系 | 官方 SOTA（bigbag）`train_gpt.py` | 未改逻辑，仅整理注释 | 保证配置齐全、可复现、**可消融**（这是本方案的关键前提） |
| 3 层循环（Loop 3-5 ×2，frac ≥ 0.35 启用） | bigbag SOTA | 未改默认 | 官方得分点，先复现再消融 |
| 并行残差 + attn/mlp scale + resid_mix | bigbag SOTA | 未改默认（`PARALLEL_RESIDUAL_START=7`） | 同上 |
| QK-Gain 初始化 | bigbag（5.25）/ dexhunter（5.0） | 采用 5.25 | 5.25 为当前最优公开值 |
| Score-First Legal TTT（`TTT_ENABLED=1`） | bigbag / dexhunter 的"合法 TTT" | 保留官方实现 | 合规前提：不学习未来 token（`ETLB_ENABLED` 恒 0） |
| GPTQ 混合量化（int6 矩阵 / int8 embedding / fp16 小张量） | Kevin Clark（GPTQ-Embeddings）+ bigbag 整合 | 保留官方 SOTA 实现 | 16MB artifact 的唯一可行路径 |
| 字节交错 + brotli 压缩 | 官方 SOTA | 保留 | 量化后进一步压体积 |
| XSA（正交投影去冗余注意力） | 官方 SOTA | 保留默认 `XSA_LAST_N=11` | 高分方案组件 |

---

## 4. 本包改了什么、为什么改

本包对代码的改动**不涉及任何算法行为**，共三处：

1. **可读化整理**：官方 `train_gpt.py` 以 LZMA+base85 压缩单行发布（代码 ~16.6KB，符合 16MB 预算）；本包提供解压还原的可读版本 `Songpengfei_C2G_train_gpt.py` 并添加头部注释与环境变量速查表，供评审逐模块审计。
   > **提交 artifact 时的说明**：官方代码字节计入 16MB 预算，可读版体积大于压缩版。打包时按实测体积决定使用哪种形式（见 AAR 决策表 D5）；可读版始终保留作为审计附件。

2. **新增回填与校验工具链**（不改训练逻辑，只在训练外围）：
   - `Songpengfei_C2G_backfill.py`：从真实日志机械提取成绩并回填 `submission.json`；**拒绝在模板日志上运行**。
   - `Songpengfei_C2G_check_submission.py`：提交前全包一致性自查（文件齐全 / 口径自洽 / 16MB / 口径冲突）。
   - `Songpengfei_C2G_RUNBOOK.md`：算力到位后的开跑手册。

3. **成绩口径纪律化**：确立 `submission.json` 为**唯一成绩事实源**，其余文档只引用不复述数字；成绩字段在未运行时为 `null`（不是 0、不是模拟值）。

> **修正记录**：本包的早期版本曾出现"`Usage_Notes.md` 声称 PENDING、而 `submission.json` 填 SIMULATED 数字"的自相矛盾。该问题已修复，根因与修法见 `Songpengfei_C2G_AAR.md` 失败案例 4。

---

## 5. 本队计划中的真实改动（待消融验证后落定，见 `Songpengfei_C2G_ablation.md`）

**主攻方向（单选）**：优化器侧。

| 候选改动 | 动机 | 风险控制 |
|---|---|---|
| `MUON_MOMENTUM_WARMUP_START` / `_STEPS` 扫描 | 官方未披露该维扫描；10 分钟短预算下动量预热形状对最终收敛点影响被放大 | 粗扫 1 seed → 精扫 3 seed，负收益即弃 |
| `MUON_WD` / `EMBED_WD` 分组扫描 | 当前均为单点取值，缺乏灵敏度证据 | 同上 |
| `EMA_DECAY` 灵敏度 | EMA 与 warmdown 耦合，官方只给了单点 0.9965 | 同上 |

**后置方向（Level 2/3 再评估，本轮不申请预算）**：架构微调（`PARALLEL_RESIDUAL_START` / `XSA_LAST_N` / `NUM_LOOPS`）、TTT 超参（LR / epochs / chunk）。

> 为什么主攻优化器而非架构？理由见 `Songpengfei_C2G_方案草案.md` Q1 的三条排除论证——架构改动会同时改变参数量与 16MB 预算，破坏受控对照，无法把 BPB 变化归因到单一变量。

所有改动以"**每点单 BPB 收益 > 0.0005 且 3-seed 同向**"为入选门槛，防止过拟合验证集。

---

## 6. 合规与致谢

- 全部代码与数字来源：OpenAI parameter-golf 官方仓库公开内容（`records` 目录 README / submission.json、`train_gpt.py`）。
- 致谢 nanoGPT（Karpathy）与官方各 top 方案作者（bigbag、dexhunter、Kevin Clark）。
- 本文件仅用于课程挑战说明，未修改任何官方源码的逻辑与授权声明。
- 合规红线：`ETLB_ENABLED=0` 恒成立，TTT 仅走官方 Score-First Legal 路径。

*（本文件由 AI 辅助整理，内容经作者核对；不含任何未经运行的成绩数字。）*
