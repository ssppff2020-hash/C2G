---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: e5fb81648b27451c79943c294a107249_6f27913cc22911f1884b525400cd780f
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: e5fb81648b27451c79943c294a107249_6f27913cc22911f1884b525400cd780f
---

# C2G 参数高尔夫 —— 极限约束下的语言模型训练（统一 README）

> 作者：Songpengfei（真实作者署名，非占位符）
> 本文件是 C2G 交付目录的统一说明：环境安装、运行命令、目录结构、结果复现步骤。

## 0. 当前状态声明（重要）

> **本队尚未获得 8×H100 算力**，正处于官方「先方案、后算力」流程的**算力申请阶段**。

| 项 | 状态 |
|---|---|
| 方案草案（算力申请用） | ✅ 已定稿（经 3 轮 AI 打磨，见 `AI日志.md` §2） |
| 环境安装 / 运行命令 / 打包脚本 | ✅ 已就绪 |
| 训练代码（可审计版） | ✅ 已解包并逐模块审计 |
| 消融设计与判定门槛 | ✅ 已预注册（运行前锁定标准） |
| **真实训练成绩** | ⏳ **未运行**（阻塞项：算力券） |
| **真实 16MB artifact** | ⏳ **未运行** |

**全包唯一成绩事实源**：`Songpengfei_C2G_submission.json`。该文件中 `val_bpb`、`std`、`artifact_size_bytes` 当前均为 `null`（= 未运行，不是 0，也不是任何模拟值）。其余文档只引用该源、不复述数字。

> **为什么成绩栏是空的**：C2G 是打榜类挑战，成绩的价值完全来自可复现性——**不可复现的数字等于无效数字**。在拿到算力之前，任何"看起来像成绩"的数值都会损害交付物可信度。因此本包如实留空，同时把「拿到算力后当天跑完并全量回填」所需的一切准备好（见 §4）。

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

| 组件 | 版本要求 | 说明 |
|---|---|---|
| Python | 3.11+ | 与官方仓库 CI 对齐 |
| PyTorch | 2.9.1+cu128 | flash-attn3 依赖 |
| flash_attn_3 | cu128_torch291 wheel | 见上方 `--find-links` |
| sentencepiece | latest | 数据 tokenizer 依赖 |
| brotli | latest | artifact 压缩依赖（quality 11） |
| torchrun | standalone | `--nproc_per_node=8` 分布式启动器 |

**数据准备**：FineWeb10B 缓存，**variant 必须是 sp8192**（variant 不匹配是复现失败的头号根因）：

```bash
python cached_challenge_fineweb.py --variant sp8192
```

---

## 2. 目录结构

| 路径 | 类型 | 用途 |
|---|---|---|
| `README.md` | 文档 | 本文件：统一安装 / 运行 / 结构 / 复现说明 |
| `Songpengfei_C2G_RUNBOOK.md` | 文档 | **算力到位后的开跑手册**（环境→运行→回填→校验→排查） |
| `Songpengfei_C2G_train_gpt.py` | 代码 | 训练脚本（解压还原的可读版，含环境变量速查表与合规开关） |
| `Songpengfei_C2G_submission.json` | 数据 | **唯一成绩事实源**：架构 / 优化器 / 量化 / 运行配置 |
| `Songpengfei_C2G_submission.tar.gz` | 数据 | 打包提交物（16MB 预算内，内含 `pack_artifact.py` 与打包说明） |
| `Songpengfei_C2G_backfill.py` | 工具 | **从真实日志回填成绩**（拒绝在模板日志上运行） |
| `Songpengfei_C2G_check_submission.py` | 工具 | **提交前完整性 / 一致性自查** |
| `Songpengfei_C2G_方案草案.md` | 文档 | 方案草案（算力申请用，回答官方 4 个门槛问题） |
| `Songpengfei_C2G_方案设计.md` | 文档 | 方案设计（架构 / 优化器 / 量化 / 实验矩阵） |
| `Songpengfei_C2G_拿来说明.md` | 文档 | 拿来说明（来源 / 改动 / 动机） |
| `Songpengfei_C2G_AI日志.md` | 文档 | AI 协作日志（多轮迭代 / 决策采纳与拒绝 / 工作流） |
| `Songpengfei_C2G_AAR.md` | 文档 | 事后复盘（含 5 例真实失败的四段式分析） |
| `Songpengfei_C2G_ablation.md` | 文档 | 消融实验报告（预注册设计，成绩待运行） |
| `Songpengfei_C2G_leaderboard.md` | 文档 | BPB 对比榜单（官方公开数字 + 本队未运行状态） |
| `Songpengfei_C2G_logs/` | 日志 | 训练日志目录（当前为格式示例，见其 README） |

> **命名说明**：官方必交清单使用中文命名格式（`姓名_C2G_方案草案.md` 等）。本目录同时保留英文命名的别名文件（`Proposal_Draft` / `Design_Doc` / `AI_Log` / `Usage_Notes`），内容与中文文件**逐字节一致**；`check_submission.py` 会校验二者未发生漂移。

---

## 3. 训练运行命令

### 3.1 真实 8×H100 运行（3 个固定 seed：42 / 314 / 999）

```bash
SEED=42 QK_GAIN_INIT=5.25 TTT_ENABLED=1 TTT_LR=0.005 TTT_EPOCHS=3 \
  torchrun --standalone --nproc_per_node=8 Songpengfei_C2G_train_gpt.py \
  2>&1 | tee Songpengfei_C2G_logs/seed_42.txt
```

（seed 314 / 999 同理，改 `SEED` 与日志文件名即可；完整流程见 `RUNBOOK.md` §2）

关键环境变量：

| 变量 | 取值 | 含义 |
|---|---|---|
| `SEED` | 42 / 314 / 999 | 训练随机种子（3 个固定 seed 求 mean/std） |
| `QK_GAIN_INIT` | 5.25 | QK-Gain 初始化（官方 SOTA 配置） |
| `TTT_ENABLED` | 1 | 启用 Test-Time Training（合法路径） |
| `TTT_LR` / `TTT_EPOCHS` | 0.005 / 3 | TTT 学习率 / 迭代轮数 |
| `DATA_DIR` | `./data/`（默认） | 数据目录（FineWeb10B sp8192 缓存） |
| `ETLB_ENABLED` | 0（恒 0） | **合规开关**，保持 Score-First Legal TTT，不学习未来 token |

其他可调参数见 `Songpengfei_C2G_train_gpt.py` 头部环境变量速查表。本次提交按官方约束：20000 iterations / 600s wallclock / FineWeb10B sp8192。

### 3.2 本地冒烟验证（无 8×H100 时）

可将 `--nproc_per_node` 降为 1、缩短 `ITERATIONS` / `MAX_WALLCLOCK_SECONDS` 做**管线冒烟验证**（验证代码可运行），但**其结果不得当作正式成绩**：

```bash
SEED=42 QK_GAIN_INIT=5.25 TTT_ENABLED=1 TTT_LR=0.005 TTT_EPOCHS=3 \
  ITERATIONS=50 MAX_WALLCLOCK_SECONDS=60 \
  torchrun --standalone --nproc_per_node=1 Songpengfei_C2G_train_gpt.py
```

---

## 4. 结果复现与回填步骤

> 完整版见 `Songpengfei_C2G_RUNBOOK.md`。此处为速览。

### 4.1 回填 `submission.json`（自动）

```bash
python Songpengfei_C2G_backfill.py --dry-run   # 先看提取结果是否正确
python Songpengfei_C2G_backfill.py             # 正式回填
```

脚本从每份日志中机械提取：

| 日志行关键字 | 提取字段 | 说明 |
|---|---|---|
| `quantized_ttt ... val_bpb:` | `val_bpb` | 唯一提交口径 |
| `Total submission size ... bytes` | `artifact_size_bytes` | 16MB 硬约束，必须 < 16,000,000 |

计算 `val_bpb = mean(3 seed)`、`std = sample_std(3 seed, ddof=1)`、`artifact_size_bytes = max(3 seed)`，
写入 `submission.json` 并把状态串改为 `REAL`，同时移除 `format_reference_only` 示例块。

**校验**：`val_bpb` 与官方 SOTA 1.08100 偏差 < 0.0005 视为复现成功。

### 4.2 手工更新的文件

用真实数字替换"未运行"的文档：`leaderboard.md`（本队两行）、`ablation.md`（消融表）、`AAR.md` §4（追加真实训练阶段的失败案例，四段式）、本 README §0 状态表。

### 4.3 提交前完整性检查清单

```bash
python Songpengfei_C2G_check_submission.py
```

退出码 0 才可提交。脚本自动检查：

- [ ] C1 官方必交文件齐全且非空（按 `CHALLENGE.md` 命名格式）
- [ ] C2 `submission.json` 成绩字段口径自洽（`null`=未运行 / 数值=真实，状态串须匹配）
- [ ] C3 全包无未标注的成绩数值残留
- [ ] C4 `submission.tar.gz` < 16MB 且无空文件
- [ ] C5 各文档均指向唯一成绩事实源，无口径冲突
- [ ] C6 日志的"模板 vs 真实"与 `submission.json` 口径一致

---

## 5. 合规与诚实声明

1. 脚本 `ETLB_ENABLED=0` 恒成立，TTT 仅使用官方 Score-First Legal 路径，不学习未来 token；
2. 本包当前**不含任何真实成绩**，成绩字段统一为 `null`（未运行），并已通过 `check_submission.py` 校验无未标注数值残留；
3. 全部代码与数字来源：OpenAI parameter-golf 官方仓库公开内容（`records` 目录 README / submission.json、`train_gpt.py`）；官方 SOTA 引用 1.0810（bigbag，3-seed mean，std 0.00020），Baseline 引用 1.2244；
4. 算力到位后，按 `RUNBOOK.md` 执行运行与回填，全包成绩口径将同步更新为真实值。

*（本文件由 AI 辅助整理，内容经作者核对；不含任何未经运行的成绩数字。）*
