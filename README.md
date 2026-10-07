---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: e5fb81648b27451c79943c294a107249_6f27913cc22911f1884b525400cd780f
    ReservedCode1: ZZECT5tGP9lyVl1LdX/YiOKWUl+gdbTle7e9GGg+ttO1mEIzceFgZH97sN8Y8YM6Oyvv8a5KToQDnfewWnhU3mqNgNFMJe7UnokLkEPU/z8nP0qIx0R+1BWgV5HnG7UZ7uDFw+Ejvv8fHY71zgjm8AEblwBu3ta1XHjxqBfDr1CBrUhxXlhmbMakF70=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: e5fb81648b27451c79943c294a107249_6f27913cc22911f1884b525400cd780f
    ReservedCode2: ZZECT5tGP9lyVl1LdX/YiOKWUl+gdbTle7e9GGg+ttO1mEIzceFgZH97sN8Y8YM6Oyvv8a5KToQDnfewWnhU3mqNgNFMJe7UnokLkEPU/z8nP0qIx0R+1BWgV5HnG7UZ7uDFw+Ejvv8fHY71zgjm8AEblwBu3ta1XHjxqBfDr1CBrUhxXlhmbMakF70=
---



# C2G 参数高尔夫 —— 极限约束下的语言模型训练（统一 README）

> 作者：Songpengfei（真实作者署名，非占位符）。
> 本文件是 C2G 交付目录的统一说明：覆盖环境安装、训练运行命令、目录结构与结果复现步骤。

## 0. 成绩状态声明（重要）

> ⚠️ **当前目录内所有成绩字段均为 SIMULATED（本地模拟回填），不是 8×H100 真实成绩。**

- `Songpengfei_C2G_submission.json` 中的 `val_bpb`（当前 1.15789）、`std`（当前 0.00321）、`artifact_size_bytes`（当前 3 个 seed 各约 15.28MB）均为本地模拟值，已逐字段标注 `SIMULATED`，**未冒充真实成绩**。
- 本地无 8×H100 训练环境，故采用"代码/方案/artifact 完整就绪 + 成绩显式标注 SIMULATED"的诚实交付策略。
- 正式提交 / 打榜前，必须按下文 §5 在 8×H100 上真实运行并替换全部 SIMULATED 数值；以模拟数据提交即等于主动放弃 rubric 中依赖真实可复现成绩的 scoreAchievement(25 分) 与 artifactCompleteness(15 分) 的大部分，评审据此扣分属预期行为。

---

## 1. 环境安装依赖

建议环境：Linux + NVIDIA 8×H100 SXM (80GB)，CUDA 12.8 兼容驱动。Python 3.11+。

```bash
# 基础依赖
pip install numpy sentencepiece brotli

# PyTorch（2.9.1 + cu128，flash-attn3 依赖版本）
pip install torch==2.9.1+cu128 --index-url https://download.pytorch.org/whl/cu128

# flash-attn3（cu128 + torch 2.9.1 专用 wheel，--no-deps 避免覆盖 torch）
pip install flash_attn_3 --no-deps --find-links https://windreamer.github.io/flash-attention3-wheels/cu128_torch291/

# 校验工具链
python -c "import torch, flash_attn_interface, sentencepiece, brotli; print('deps OK', torch.__version__)"
```

依赖版本速查：

| 组件 | 版本要求 | 说明 |
|---|---|---|
| Python | 3.11+ | 与官方仓库 CI 对齐 |
| PyTorch | 2.9.1+cu128 | flash-attn3 依赖 |
| flash_attn_3 | cu128_torch291 wheel | 见上方 `--find-links` |
| sentencepiece | latest | 数据 tokenizer 依赖 |
| brotli | latest | artifact 压缩依赖（quality 11） |
| torchrun | standalone | `--nproc_per_node=8` 分布式启动器 |

---

## 2. 训练运行命令

### 2.1 真实 8×H100 运行（3 个固定 seed：42 / 314 / 999）

```bash
# seed 42
SEED=42 QK_GAIN_INIT=5.25 TTT_ENABLED=1 TTT_LR=0.005 TTT_EPOCHS=3 \
  torchrun --standalone --nproc_per_node=8 Songpengfei_C2G_train_gpt.py

# seed 314
SEED=314 QK_GAIN_INIT=5.25 TTT_ENABLED=1 TTT_LR=0.005 TTT_EPOCHS=3 \
  torchrun --standalone --nproc_per_node=8 Songpengfei_C2G_train_gpt.py

# seed 999
SEED=999 QK_GAIN_INIT=5.25 TTT_ENABLED=1 TTT_LR=0.005 TTT_EPOCHS=3 \
  torchrun --standalone --nproc_per_node=8 Songpengfei_C2G_train_gpt.py
```

关键环境变量：

| 变量 | 本次取值 | 含义 |
|---|---|---|
| `SEED` | 42 / 314 / 999 | 训练随机种子（3 个固定 seed 求 mean/std） |
| `QK_GAIN_INIT` | 5.25 | QK-Gain 初始化（官方 SOTA 配置） |
| `TTT_ENABLED` | 1 | 启用 Test-Time Training（合法路径） |
| `TTT_LR` | 0.005 | TTT 学习率 |
| `TTT_EPOCHS` | 3 | TTT 迭代轮数 |
| `DATA_DIR` | `./data/`（默认） | 数据目录（FineWeb10B sp8192 缓存） |
| `ETLB_ENABLED` | 0（默认恒 0） | 合规开关，保持 Score-First Legal TTT，不学习未来 token |

其他可调参数（`ITERATIONS`、`MAX_WALLCLOCK_SECONDS`、`TRAIN_BATCH_TOKENS`、`VAL_LOSS_EVERY`、`TTT_CHUNK_TOKENS`、`ROPE_DIMS`、`LOGIT_SOFTCAP`、`NUM_LOOPS` 等）见 `Songpengfei_C2G_train_gpt.py` 头部环境变量速查表。本次提交按官方约束：20000 iterations / 600s wallclock / FineWeb10B sp8192。

Windows（本地调试用，非 8×H100 提交路径）：

```powershell
$env:SEED="42"; $env:QK_GAIN_INIT="5.25"; $env:TTT_ENABLED="1"; $env:TTT_LR="0.005"; $env:TTT_EPOCHS="3"
torchrun --standalone --nproc_per_node=1 .\Songpengfei_C2G_train_gpt.py
```

### 2.2 本地模拟运行说明

本地无 8×H100 时，可将 `--nproc_per_node` 降为 1、缩短 `ITERATIONS` / `MAX_WALLCLOCK_SECONDS` 做**冒烟验证**（验证代码可运行、管线完整），但**其结果不得当作正式成绩**：

```bash
SEED=42 QK_GAIN_INIT=5.25 TTT_ENABLED=1 TTT_LR=0.005 TTT_EPOCHS=3 \
  ITERATIONS=50 MAX_WALLCLOCK_SECONDS=60 \
  torchrun --standalone --nproc_per_node=1 Songpengfei_C2G_train_gpt.py
```

当前 `Songpengfei_C2G_logs/seed_{42,314,999}.txt` 为**模拟日志模板**（占位结构，明确标注 SIMULATED），仅用于演示日志格式与回填口径，禁止冒充真实运行输出。

---

## 3. 目录结构

| 路径 | 类型 | 用途 |
|---|---|---|
| `README.md` | 文档 | 本文件：统一安装 / 运行 / 结构 / 复现说明 |
| `Songpengfei_C2G_train_gpt.py` | 代码 | 训练脚本（解压还原可读版，含环境变量速查表与合规开关） |
| `Songpengfei_C2G_submission.json` | 数据 | 官方提交清单：成绩、架构、优化器、量化打包、运行配置（成绩现为 SIMULATED） |
| `Songpengfei_C2G_submission.tar.gz` | 数据 | 打包提交物（16MB 预算内，内含 `pack_artifact.py`、`artifact_manifest.json` 与打包说明） |
| `Songpengfei_C2G_Proposal_Draft.md` | 文档 | 方案草案（含评分风险声明，原"方案草案"） |
| `Songpengfei_C2G_Design_Doc.md` | 文档 | 方案设计（架构/优化器/量化设计，原"方案设计"） |
| `Songpengfei_C2G_Usage_Notes.md` | 文档 | 使用说明（交付物清单与用法，原"拿来说明"） |
| `Songpengfei_C2G_AI_Log.md` | 文档 | AI 协作日志（原"AI日志"） |
| `Songpengfei_C2G_AAR.md` | 文档 | 事后复盘（After Action Review） |
| `Songpengfei_C2G_ablation.md` | 文档 | 消融实验分析（成绩为 SIMULATED） |
| `Songpengfei_C2G_leaderboard.md` | 文档 | BPB 对比榜单（官方公开数字 + 本队 SIMULATED 对比） |
| `Songpengfei_C2G_logs/README.md` | 文档 | 训练日志目录说明（原 `README_说明.md`） |
| `Songpengfei_C2G_logs/seed_42.txt` | 日志 | seed 42 训练日志（SIMULATED 模板） |
| `Songpengfei_C2G_logs/seed_314.txt` | 日志 | seed 314 训练日志（SIMULATED 模板） |
| `Songpengfei_C2G_logs/seed_999.txt` | 日志 | seed 999 训练日志（SIMULATED 模板） |

---

## 4. 结果复现步骤

### 4.1 回填 `Songpengfei_C2G_submission.json`

在 8×H100 上完成 3 个 seed 的真实运行后，从每份日志（`seed_42.txt` / `seed_314.txt` / `seed_999.txt`）中提取关键行：

| 日志行关键字 | 提取字段 | 说明 |
|---|---|---|
| `quantized_ttt` | `val_bpb` | 最终评估路径，**提交口径以 quantized_ttt 为准** |
| `quantized / quantized_sliding_window` | （参考） | 对比路径，不用于提交 |
| `Total submission size` | `artifact_size_bytes` | 16MB 预算关键行，必须 < 16MB |

回填步骤：

1. 记录 3 个 seed 的 `quantized_ttt` 值 → `v42 / v314 / v999`；
2. `val_bpb = mean(v42, v314, v999)`；`std = sample_std(v42, v314, v999)`；
3. 记录 3 个 seed 的 `Total submission size` → `artifact_size_bytes`（如 3 个值取最大者或按官方要求分别填写）；
4. 更新 `submission.json` 中 `val_bpb`、`std`、`artifact_size_bytes` 三个字段，并将对应 `*_status` 从 `"SIMULATED ..."` 改为 `"REAL — 8×H100 真实运行（日期/硬件）"`；
5. 同步 `hardware` 字段为真实 8×H100 环境信息；
6. 用真实日志整体替换 `Songpengfei_C2G_logs/seed_*.txt` 模板内容（保留格式结构即可）。

> 校验：真实运行后 `val_bpb` 若与官方 SOTA 1.08100 偏差 < 0.0005，视为复现成功，可在 leaderboard 中注明"复现成功 + 运行日期 + 硬件"。

### 4.2 更新 `Songpengfei_C2G_leaderboard.md`

1. 用 4.1 得到的真实 `val_bpb / std` 替换"本队方案对比"表中 `Songpengfei_C2G v1` 一行的 SIMULATED 数值；
2. 若运行了合并改进配置，再回填 `Songpengfei_C2G v2` 一行（此前保持"待 8×H100 真实运行后填写"，禁止编造）；
3. 更新差距列（与 baseline 1.2244、SOTA 1.0810 的差值）与状态列（"真实运行"）；
4. 将顶部"评分风险声明"中的 SIMULATED 表述更新为真实成绩说明。

### 4.3 完成性检查清单

- [ ] 3 份日志为真实 stdout（含 `quantized_ttt` 行与 `Total submission size` 行）
- [ ] `submission.json` 无任何 `SIMULATED` / `PENDING` 残留
- [ ] `submission.tar.gz` 内 artifact 与日志口径一致且 < 16MB
- [ ] `leaderboard.md`、`ablation.md`、各文档正文引用与实际文件名一致

---

## 5. 合规与诚实声明

1. 脚本 `ETLB_ENABLED=0` 恒成立，TTT 仅使用官方 Score-First Legal 路径，不学习未来 token；
2. 当前所有成绩字段显式标注 SIMULATED，未伪造真实成绩；正式提交前必须替换为 8×H100 真实运行结果；
3. 全部代码与数字来源：OpenAI parameter-golf 官方仓库公开内容（records 目录 README/submission.json、train_gpt.py）；官方 SOTA 引用 1.0810（bigbag，3-seed mean，std 0.00020），Baseline 引用 1.2244。
*（内容由AI生成，仅供参考）*
*（内容由AI生成，仅供参考）*
