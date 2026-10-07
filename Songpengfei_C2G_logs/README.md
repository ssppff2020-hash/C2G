---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: e5fb81648b27451c79943c294a107249_0689a593c22711f1887c525400de85a5
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: e5fb81648b27451c79943c294a107249_0689a593c22711f1887c525400de85a5
---

# Songpengfei_C2G_logs/ — 训练日志目录说明

> 作者：Songpengfei（真实作者署名，非占位符）

## 当前状态：格式示例（非运行产物）

本目录存放 C2G 挑战的 3 个固定 seed（42 / 314 / 999）训练日志。

**本队尚未获得 8×H100 算力**（官方算力申请流程中），因此本目录当前只有**日志格式示例**：
它演示真实运行后 stdout 的字段结构、以及回填时从哪一行取数，其中所有数值均为占位符
（`<float>` / `<int>`），**不是成绩、不是训练产物、禁止引用**。

真实日志将在算力到位后，由 `Songpengfei_C2G_RUNBOOK.md` §2 的 `tee` 命令**直接覆盖**本目录文件。

## 为什么现在不放真实日志

C2G 是打榜类挑战，成绩的价值完全来自可复现性。在没有算力的情况下，
任何"看起来像成绩"的数字都会损害交付物可信度——评审需要额外花成本判断
它是"占位"还是"虚报"。因此本目录如实保留格式示例，并把它做成**不可被误读**的形式。

## 回填机制

```bash
python Songpengfei_C2G_backfill.py --dry-run   # 先看提取结果
python Songpengfei_C2G_backfill.py             # 正式回填
```

`backfill.py` 会从每份日志中提取：

| 日志行 | 提取字段 | 说明 |
|---|---|---|
| `quantized_ttt ... val_bpb: <值>` | `val_bpb` | **唯一提交口径**（不是 `quantized`，也不是 `pre-quantization post-ema`） |
| `Total submission size ... <值> bytes` | `artifact_size_bytes` | 16MB 硬约束关键行，必须 < 16,000,000 |

然后计算 3 seed 的 mean 与样本标准差（ddof=1），写入 `submission.json`。

> ⚠️ **安全设计**：`backfill.py` 会检测日志中的模板标记（`示例` / `占位` / `待运行` 等）
> 并**拒绝回填**。这是为了防止"用示例数字回填成绩"这一历史失败重演——
> 回填必须来自真实运行。

## 日志字段含义（对应 `Songpengfei_C2G_train_gpt.py` 输出）

| 日志行 | 含义 |
|---|---|
| `train_shards` / `val_tokens` | 数据规模确认（sp8192 缓存） |
| `model_params` | 模型参数量（用于 16MB 预算审计） |
| `warmup_step` / `train_loss` | 训练过程（含循环结构 warmup 阶段） |
| `val_loss` / `val_bpb` | 训练中周期验证（`VAL_LOSS_EVERY=4000`） |
| `pre-quantization post-ema` | 量化前 EMA 权重评估 |
| `GPTQ:collecting Hessians` | 量化校准开始 |
| `Serialized model quantized+brotli` / `Total submission size` | **16MB 预算关键行** |
| `quantized` / `quantized_sliding_window` / `quantized_ttt` | 最终三条评估路径，**以 `quantized_ttt` 为提交口径** |

## 合规提醒

- 脚本 `ETLB_ENABLED=0` 恒成立，TTT 仅使用官方 Score-First Legal 路径；
- 日志须为**真实 stdout 原样**，不得编辑数值、不得删行；
- 建议用 `tee` 而非 `>` 重定向，避免中途崩溃时丢失屏幕输出。

*（本文件由 AI 辅助整理，内容经作者核对。）*
