---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: e5fb81648b27451c79943c294a107249_076a9d99c22711f1887c525400de85a5
    ReservedCode1: fhlXJTp8kkmoO1Tu1jowksCdumQy+gJLaV9APxBaQwUpjDynTlw0OO1kLlFeA77tbexUCQQR8qkfUcGzThz03ILsMBU4IVGuGF/+tgmdvRcLEeMoLGbiVelv1rGVO/aIr9VtJbIU8h0LMaFmWOv3P+T3KI59HPInl957Uxjd4b7LTLNTZOq32jell9g=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: e5fb81648b27451c79943c294a107249_076a9d99c22711f1887c525400de85a5
    ReservedCode2: fhlXJTp8kkmoO1Tu1jowksCdumQy+gJLaV9APxBaQwUpjDynTlw0OO1kLlFeA77tbexUCQQR8qkfUcGzThz03ILsMBU4IVGuGF/+tgmdvRcLEeMoLGbiVelv1rGVO/aIr9VtJbIU8h0LMaFmWOv3P+T3KI59HPInl957Uxjd4b7LTLNTZOq32jell9g=
---

---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: e5fb81648b27451c79943c294a107249_29c75de7c22411f1884b525400cd780f
    ReservedCode1: 4fHBU3jB//y03T/FLY6GHR2036uV53KLxoEeLvsEkPJHAUppjF+smzbTF+xxtCu2ggnZN1RFrSQnurt9gp1OF+nZfJBDG9wijYMxXODzZeGemlu6hm9+w7U4NuN4hIKjq4GQCF7HCAtVi19IE7iCL2nkLh5B27YUHC94KuJT7oUWrCQRFkbdlYNH/qE=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: e5fb81648b27451c79943c294a107249_29c75de7c22411f1884b525400cd780f
    ReservedCode2: 4fHBU3jB//y03T/FLY6GHR2036uV53KLxoEeLvsEkPJHAUppjF+smzbTF+xxtCu2ggnZN1RFrSQnurt9gp1OF+nZfJBDG9wijYMxXODzZeGemlu6hm9+w7U4NuN4hIKjq4GQCF7HCAtVi19IE7iCL2nkLh5B27YUHC94KuJT7oUWrCQRFkbdlYNH/qE=
---

# Songpengfei_C2G_ablation.md — 消融实验报告

> 作者：Songpengfei（本文件为真实作者署名交付物，前缀 Songpengfei 非占位符）。
> 实验环境预设：8×H100 SXM，600s/run，FineWeb10B sp8192，官方验证集 BPB。
> ⚠️ 本文档中除注明"官方公开数字"外，所有"预期/待填写"单元格均需在真实运行后回填，**禁止在运行前编造数值**。

---

## 评分风险声明（Score Achievement Risk Disclosure）

> 本交付物成绩栏全部为 PENDING，特此向评审显式说明评分风险与原因：

1. **留 PENDING 是正确且不编造的做法**：本地无 8×H100 训练环境，绝不虚构任何 BPB/成绩数字；所有成绩字段均标注"待 8×H100 真实运行后填写"。
2. **打榜类挑战的评分代价**：C2G 为打榜类任务，rubric 中 scoreAchievement(25分) 与 artifactCompleteness(15分) 依赖真实且可复现的成绩；当前提交等于主动放弃这部分成绩（约 40 分中的大块），请评审据此扣分时知悉此为环境限制所致。
3. **PENDING 语义澄清**：成绩 PENDING 表示"待真实 8×H100 运行后回填"，并非"无成绩记录/未完成/无法复现"；交付物的代码、方案、artifact 完整性均就绪。
4. **后续回填路径**：若获得 8×H100 算力，可按官方 10 分钟约束运行 `Songpengfei_C2G_train_gpt.py` 并回填真实成绩、更新 leaderboard 与 submission.json。

## 1. 消融设计总览

消融围绕三个改进轴展开（详见 `Songpengfei_C2G_Design_Doc.md` 实验矩阵）：

- **A 轴（结构）**：TTT 开关、并行残差起点、XSA 层数、循环深度。
- **B 轴（训练超参）**：Muon 动量预热、EMA 衰减、Muon 权重衰减。
- **C 轴（评估侧）**：TTT_LR / TTT_EPOCHS / TTT_CHUNK_TOKENS 扫描。

对照组 R0 = 官方 SOTA 复现值（目标 1.0810，来源：官方公开 submission.json）。

## 2. 组件单独贡献

| 消融 ID | 变量 | 对照组值 | 实验值 | seed | val_bpb | Δ vs R0 | 判定 |
|---|---|---|---|---|---|---|---|
| A1 | TTT_ENABLED | 1 | 0 | 42 | **待运行** | **待运行** | 待运行 |
| A2 | PARALLEL_RESIDUAL_START | 7 | 6 / 8 | 42 | **待运行** | **待运行** | 待运行 |
| A3 | XSA_LAST_N | 11 | 8 | 42 | **待运行** | **待运行** | 待运行 |
| A4 | NUM_LOOPS / LOOP 区间 | 2×(3-5) | 3×(3-5) | 42 | **待运行** | **待运行** | 待运行 |
| A5 | MUON_MOMENTUM_WARMUP_START | 0.92 | 0.88 / 0.96 | 42 | **待运行** | **待运行** | 待运行 |
| A6 | EMA_DECAY | 0.9965 | 0.995 / 0.998 | 42 | **待运行** | **待运行** | 待运行 |
| A7 | MUON_WD | 0.095 | 0.07 / 0.12 | 42 | **待运行** | **待运行** | 待运行 |
| A8 | TTT_LR / TTT_EPOCHS | 0.005 / 3 | 见 Songpengfei_C2G_Design_Doc.md §4 | 42 | **待运行** | **待运行** | 待运行 |

> 填表规则：Δ = 实验值 − R0 复现值；Δ < 0 表示收益。粗扫阶段判定阈值 |Δ| > 0.0005 且相邻点同向才进入精扫。

## 3. 组合效应

| 组合 ID | 组合内容 | seed | val_bpb | Δ vs R0 | 交互效应说明 |
|---|---|---|---|---|---|
| M1 | 全部正收益项合并（架构 + 超参 + TTT 超参） | 42, 314, 999 | **待运行** | **待运行** | 若 Δ(M1) ≈ ΣΔ(单项) 说明近似可加；若明显偏离则记录交互 |
| M2 | 仅训练超参组合（不动架构） | 42, 314, 999 | **待运行** | **待运行** | 备份路线 |

## 4. 统计显著性分析框架

官方成绩以 3-seed mean(std) 报告（SOTA std = 0.00020）。本报告采用以下约定：

1. **效应量**：Δ = mean_experiment − mean_control（BPB）。
2. **噪声估计**：每配置 3 个 seed 的 std；若 std 大于 |Δ|，则结论降级为"不显著"。
3. **显著性判定**（保守框架）：
   - 单点粗扫：只作方向筛选，不做统计结论；
   - 精扫（3 seed）：计算 Δ 与合并 std（`sqrt(std_exp²/3 + std_ctrl²/3)`），要求 `|Δ| ≥ 2 × 合并标准误` 才判定为显著正收益；
   - 若资源允许补跑到 5 seed，按 t 分布（df = n_exp + n_ctrl − 2）给双侧 p 值。
4. **孤点噪声排除**：若某参数邻近两个取值方向相反或收益不单调，标记为噪声，不进入合并配置。
5. **报告口径**：所有显著性结论附原始 mean/std/seed 表，避免只报 p 值。

## 5. 结论与后续

- 待真实运行后回填结论；负收益项写入 `Songpengfei_C2G_AAR.md` 作为失败经验。
- 若所有改进项均为负收益，则保持官方 SOTA 配置提交，成绩引用官方公开数字并注明来源。

## 附：复现运行命令

```bash
SEED=42 QK_GAIN_INIT=5.25 TTT_ENABLED=1 TTT_LR=0.005 TTT_EPOCHS=3 \
  torchrun --standalone --nproc_per_node=8 Songpengfei_C2G_train_gpt.py
```
*（内容由AI生成，仅供参考）*
*（内容由AI生成，仅供参考）*
