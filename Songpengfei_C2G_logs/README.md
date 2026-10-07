---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: e5fb81648b27451c79943c294a107249_0689a593c22711f1887c525400de85a5
    ReservedCode1: 45C5WXjyIWBhoEvtCMKH6gAwBH/1wB1ui86/o1v5AhpzSIvk9qNcbzjrP+TJQOWk0xHKY1/+txVIRaBHW0fEl7UrhDfpElZYQERaDS2M8Z5YPxPo3RlpqgebFwnCMRF6K//GsdaFxoVyN4/YUsbv0TItqD9RlTZjFc0vpJB8l0KvAYmCQ1Dm7bmc7ik=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: e5fb81648b27451c79943c294a107249_0689a593c22711f1887c525400de85a5
    ReservedCode2: 45C5WXjyIWBhoEvtCMKH6gAwBH/1wB1ui86/o1v5AhpzSIvk9qNcbzjrP+TJQOWk0xHKY1/+txVIRaBHW0fEl7UrhDfpElZYQERaDS2M8Z5YPxPo3RlpqgebFwnCMRF6K//GsdaFxoVyN4/YUsbv0TItqD9RlTZjFc0vpJB8l0KvAYmCQ1Dm7bmc7ik=
---

---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: e5fb81648b27451c79943c294a107249_28ef8adbc22411f1884b525400cd780f
    ReservedCode1: PSNawHqIBeekAyV1wngB15MQr5hE0pGZ2Fn2pBnDUQ9/mKuOxmp5QEAGgNxNiCE1jdRCtDBeaCJMppt1I+vSHIcNDcD2XJZbc1DHKooCt6BYt0Xq/RAmmOobxVKBDFr713fWD6GgU0OSs1Bklhj7tiTTfbSNhYEt7ZYNOuds3ukYV8ml0X1xjrSysto=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: e5fb81648b27451c79943c294a107249_28ef8adbc22411f1884b525400cd780f
    ReservedCode2: PSNawHqIBeekAyV1wngB15MQr5hE0pGZ2Fn2pBnDUQ9/mKuOxmp5QEAGgNxNiCE1jdRCtDBeaCJMppt1I+vSHIcNDcD2XJZbc1DHKooCt6BYt0Xq/RAmmOobxVKBDFr713fWD6GgU0OSs1Bklhj7tiTTfbSNhYEt7ZYNOuds3ukYV8ml0X1xjrSysto=
---

# Songpengfei_C2G_logs/README.md — 训练日志目录说明

> 作者：Songpengfei（真实作者署名，非占位符）。

## 用途

本目录存放 Parameter Golf (C2G) 挑战的**真实训练日志**（3 个固定 seed：42 / 314 / 999），供评审核验成绩。

## 当前状态：仅模板，禁止编造

- 由于本地环境无 8×H100，本目录目前只提供**日志结构模板**（`seed_42.txt` / `seed_314.txt` / `seed_999.txt`）。
- 模板中所有 `val_bpb / val_loss / train_loss / 时长 / 字节数` 均为占位符，**未真实运行前严禁替换为虚构数字**。
- 提交成绩前必须：
  1. 在 8×H100 SXM 上按模板头部命令运行 `Songpengfei_C2G_train_gpt.py`（SEED 分别为 42/314/999）；
  2. 用脚本真实 stdout 覆盖模板占位内容；
  3. 从 `quantized_ttt` 行提取最终 BPB，3 个 seed 计算 mean/std 后回填 `Songpengfei_C2G_submission.json`。

## 日志格式说明（对应 Songpengfei_C2G_train_gpt.py 输出）

| 日志行 | 含义 |
|---|---|
| `train_shards / val_tokens` | 数据规模确认（sp8192 缓存） |
| `model_params` | 模型参数量（用于 16MB 预算审计） |
| `warmup_step / train_loss` | 训练过程（含循环结构 warmup 阶段） |
| `val_loss / val_bpb` | 训练中周期验证（VAL_LOSS_EVERY=4000） |
| `pre-quantization post-ema` | 量化前 EMA 权重评估 |
| `GPTQ:collecting Hessians` | 量化校准开始（预留 12s） |
| `Serialized model quantized+brotli / Total submission size` | **16MB 预算关键行**，必须 < 16MB |
| `quantized / quantized_sliding_window / quantized_ttt` | 最终三条评估路径，**以 quantized_ttt 为提交口径** |

## 合规提醒

- 脚本 `ETLB_ENABLED=0` 恒成立，TTT 仅使用官方 Score-First Legal 路径；
- 日志中若出现 `nvidia-smi` 输出（脚本会在主进程打印），保留其环境信息即可，不影响成绩。
*（内容由AI生成，仅供参考）*
*（内容由AI生成，仅供参考）*
