[English](README.md) | [简体中文](README.zh-CN.md) | [Português](README.pt-BR.md) | [日本語](README.ja.md) | [Español](README.es.md) | [Bahasa Indonesia](README.id.md)

# PulseLex

<p align="center">
  <img src="pLex-SocialPreview.png" alt="PulseLex" width="100%">
</p>

一种受 Morse 启发的固定长度字母表，配备系统化的 Hamming (9,5) 和扩展 SECDED (10,5) 前向纠错编码。

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](pyproject.toml)
[![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue.svg)](pyproject.toml)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-51%20passed-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-98%25-brightgreen.svg)](tests/)

PulseLex 是一个实验性的电信与编码理论研究原型。它研究将国际 Morse 码中可变长度、依赖时序的字符替换为统一的五位有效载荷，将二进制状态渲染为点和划脉冲，并应用线性分组码以保证单比特错误纠正和双比特错误检测。

它是一个教育性的微遥测研究工件，而非面向运营级高带宽射频信号传输的替代方案，也不是密码加密系统。

---

## 概述

传统国际 Morse 码（ITU-R 建议 M.1677-1）针对明信道上的人工手动按键进行了优化。然而，它高度依赖时序精度（1 单元元素间隔、3 单元字符间隔、7 单元字间隔），且不提供任何原生前向纠错。时序抖动或信道噪声可能导致整个单词范围内的帧同步丢失。

PulseLex 探索了一种替代设计：
- 每个字符占据一个固定的九脉冲（或十脉冲 SECDED）块。
- 一旦建立流同步，字符帧确定性地解析。
- 传输过程中引入的孤立单比特翻转在数学上可被检测并纠正。
- 该协议提供扩展 Hamming (10,5) SECDED 模式，可检测双比特错误以消除误纠正。
- 内置连续比特流滑动窗口同步机制，可在无分段脉冲流上恢复帧锁定。
- 零依赖声学 CW 音频合成器使用升余弦整形的 WAV 音调脉冲，支持通过扬声器至麦克风的空中气隙传输。

---

## 主要特性

- **缩短 Hamming (9,5) 与 SECDED (10,5) 编解码器：** 使用四个奇偶校验位保护五个数据位的系统分组码（$d_{\min} = 3$），可选第 10 个整体奇偶校验位提供单错误纠正和双错误检测（SECDED，$d_{\min} = 4$）。
- **连续比特流前导同步器：** 滑动窗口相关器锁定原始未分段的脉冲流，无需依赖人工空白分隔。
- **声学 CW 波形合成器：** 标准库音频键控器导出带有平滑 Hann 窗口升/降包络的 16 位单声道 PCM WAV 文件，以防止频谱扩散和键控咔嗒声。
- **32 符号字母表：** 全面映射 26 个大写英文字母、空格、三个标点符号以及专用的起始/结束帧标记符。
- **防御性症状解码：** 区分零错误、单比特错误和不可纠正的双比特错误，在出现不可纠正错误时抛出 `DoubleErrorDetected` 异常，而非损坏比特。
- **二进制对称信道模拟器：** 可配置的 Bernoulli 比特翻转信道模型，用于随机传输实验。
- **可重现的蒙特卡洛基准测试：** 自动仿真框架，将经验符号错误率与无编码基线对比并输出至 CSV。
- **学术论文：** 完整的 LaTeX 研究论文（`paper/pulselex_paper.tex`），包含正式推导、TikZ 图表和 BibTeX 引用。
- **零外部依赖：** 完全使用 Python 标准库构建。

---

## 符号字母表

每个符号映射到一个 5 位二进制有效载荷（$2^5 = 32$ 个唯一状态）：

| 十进制值 | 5 位有效载荷 | 符号 | 描述 |
|---:|:---:|:---:|---|
| 0–25 | `00000`–`11001` | A–Z | 大写拉丁字母 |
| 26 | `11010` | Space | 单词分隔符 |
| 27 | `11011` | `.` | 句号 |
| 28 | `11100` | `,` | 逗号 |
| 29 | `11101` | `?` | 问号 |
| 30 | `11110` | `START` | 消息前导标记 |
| 31 | `11111` | `END` | 消息后导标记 |

二进制 `0` 渲染为点（`.`），二进制 `1` 渲染为划（`-`）。

---

## 技术架构

码字使用从 1 到 9（或 SECDED 模式下从 1 到 10）的系统性 1 基索引。奇偶校验位分配到 2 的幂次位置（位置 1、2、4、8），五个有效载荷位占据其余位置（3、5、6、7、9）：

```text
Standard (9,5):
Codeword Index:   1    2    3    4    5    6    7    8    9
Content Type:    p1   p2   d1   p4   d2   d3   d4   p8   d5
Bit Allocation: [ Parity ] [Data] [Parity] [   Data   ] [Parity] [Data]

Extended SECDED (10,5):
Codeword Index:   1    2    3    4    5    6    7    8    9   10
Content Type:    p1   p2   d1   p4   d2   d3   d4   p8   d5  p0 (Overall)
```

在偶校验条件下，校验方程为：

$$\begin{aligned}
p_1 &= d_1 \oplus d_2 \oplus d_4 \oplus d_5 \\
p_2 &= d_1 \oplus d_3 \oplus d_4 \\
p_4 &= d_2 \oplus d_3 \oplus d_4 \\
p_8 &= d_5 \\
p_0 &= \bigoplus_{i=1}^9 c_i \quad \text{(SECDED mode only)}
\end{aligned}$$

### 端到端工作流程

```mermaid
flowchart LR
    A[Text Input] --> B[Normalize & Frame]
    B --> C[5-Bit Payloads]
    C --> D[Hamming 9,5 / 10,5 SECDED]
    D --> E[Pulse Stream .-.-]
    E --> F[Continuous Synchronizer / Audio WAV]
    F --> G[Channel Noise / Air Gap]
    G --> H[Syndrome & Parity Validator]
    H --> I[Single-Bit Corrector / Double Error Guard]
    I --> J[Recovered Text]
```

---

## 数学基础

- **码率（$R$）：**
  $$R_{(9,5)} = \frac{5}{9} \approx 0.556, \quad R_{(10,5)} = \frac{5}{10} = 0.500$$
- **冗余开销：**
  $$\text{Overhead}_{(9,5)} = \frac{9 - 5}{5} \times 100\% = 80\%, \quad \text{Overhead}_{(10,5)} = 100\%$$
- **最小 Hamming 距离与误差界：**
  - 标准 $(9,5)$：$d_{\min} = 3 \implies t = 1$ 位纠正。
  - 扩展 $(10,5)$：$d_{\min} = 4 \implies t = 1$ 位纠正，$2$ 位不可纠正双错误检测（SECDED）。
- **无编码符号错误率（SER）：** 对于独立比特翻转概率 $p$：
  $$P_{\text{uncoded}} = 1 - (1 - p)^5$$
  当 $p = 0.01$ 时，$P_{\text{uncoded}} \approx 0.04901$（4.90%）。
- **Hamming 块失败率（$P_{\ge 2}$）：** 在 9 位块中出现两个或更多比特错误的概率：
  $$P_{\ge 2} = 1 - (1 - p)^9 - 9p(1 - p)^8$$
  当 $p = 0.01$ 时，$P_{\ge 2} \approx 0.00344$（0.34%），实现约 14.3 倍的符号错误概率降低。

---

## 安装

### 前提条件
- Python 3.10 或更新版本。

### 可编辑开发安装
```bash
git clone https://github.com/hasheramin5-cyber/pLex.git
cd pLex
python -m pip install -e .
```

### 开发依赖
安装测试工具：
```bash
python -m pip install -e ".[dev]"
```

---

## 快速开始与使用

### 1. 命令行界面

#### 标准与 SECDED 编码
```bash
# Standard 9-bit encoding
pulselex encode "HELLO, WORLD?"

# Extended 10-bit SECDED encoding (Double-Error Detection)
pulselex encode --extended "HELLO, WORLD?"
```

#### 解码空格分隔的块
```bash
pulselex decode "-------.. .....---- .-.-.-... --..-.--- --..-.--- ...----.. ..-.--... -.-.-.-.. .--..--.. ...----.. .--....-- --..-.--- .-.-..--- -.-.--.-- .--------"
```

#### 连续流同步与去帧
从带有前导/后导噪声的未分段、含噪比特流中恢复消息：
```bash
pulselex sync-decode "..noise..-------..-..-..-..-....-.--------...noise.." --verbose
```

#### 声学 CW 音频合成（WAV 导出）
生成平滑的 Hann 整形 750 Hz 音频音调：
```bash
pulselex audio "EMERGENCY" -o results/beacon.wav --freq 750 --dot-duration 0.050
```

### 2. Python API 示例

```python
from pulselex import encode_text, decode_pulses, sync_and_decode, text_to_wav

# 1. Standard encoding & decoding
stream = encode_text("PULSELEX")
recovered = decode_pulses(stream)

# 2. Extended SECDED mode with 2-bit error detection
secded_stream = encode_text("AIR GAP MSG", extended=True)
recovered_secded = decode_pulses(secded_stream)

# 3. Synchronize continuous bitstream with arbitrary noise
raw_bitstream = "...noise..." + secded_stream.replace(" ", "") + "---noise---"
text = sync_and_decode(raw_bitstream, extended=True)
print("Deframed:", text)

# 4. Synthesize acoustic CW audio WAV file
wav_path = text_to_wav("SOS", "sos_beacon.wav", frequency_hz=800.0)
print(f"Audio exported to {wav_path}")
```

---

## 经验基准测试

该项目包含一个经验蒙特卡洛基准测试工具，用于评估不同噪声率下的符号错误率。

### 运行实验
```bash
python -m pulselex.experiment --trials 50000 --seed 7 --output results/bit_error_experiment.csv
```

### 参考结果（每概率 50,000 次试验，种子 7）

| 比特错误概率（$p$） | 无编码 5 位 SER | PulseLex (9,5) SER | 已纠正块数 | SER 降低倍数 |
|---:|---:|---:|---:|---:|
| 0.001 | 0.004740 | 0.000000 | 421 | 完全消除（0 错误）|
| 0.005 | 0.024440 | 0.001000 | 2,183 | 24.4x |
| 0.010 | 0.048720 | 0.003260 | 4,329 | 14.9x |
| 0.020 | 0.095600 | 0.012260 | 8,303 | 7.8x |
| 0.050 | 0.229600 | 0.068120 | 17,175 | 3.4x |
| 0.100 | 0.409200 | 0.211820 | 26,360 | 1.9x |

*参考数据存储于 `results/bit_error_experiment.csv`，摘要见 `results/experiment_summary.txt`。*

---

## 测试

使用 pytest 运行自动化测试套件：

```bash
pytest
```

51 个单元测试（98% 行覆盖率）涵盖：
- 对所有 32 个有效载荷和所有 9 个比特位置的穷举单比特错误纠正（288 个测试用例）。
- SECDED 单比特错误纠正（320 个测试用例）和穷举双比特错误检测（1,440 个测试用例）。
- 连续流同步、前导滑动窗口相关和噪声边界去帧。
- 音频样本合成、Hann 包络整形和标准 16 位 PCM WAV 文件头验证。
- 命令行界面子命令（`encode`、`decode`、`sync-decode`、`audio`）和退出码处理。
- 蒙特卡洛实验基准测试运行器和 CSV 数据集导出。
- 边缘情况、参数边界检查以及信道无噪声/满噪声状态。

---

## 编译研究论文

该仓库包含一份学术论文（`paper/pulselex_paper.tex`），详细阐述了协议的数学证明和研究发现。

使用标准 LaTeX 发行版编译：
```bash
pdflatex -output-directory=paper paper/pulselex_paper.tex
bibtex paper/pulselex_paper
pdflatex -output-directory=paper paper/pulselex_paper.tex
pdflatex -output-directory=paper paper/pulselex_paper.tex
```

---

## 仓库结构

```text
PulseLex/
├── .github/
│   └── workflows/
│       └── ci.yml                   # Multi-OS, multi-version GitHub Actions CI
├── docs/
│   ├── MATHEMATICAL_QUESTIONS.txt   # Analytical coding theory exercises
│   ├── PulseLex_Technical_Report.md # Full architectural report (Markdown)
│   ├── PulseLex_Technical_Report.pdf# Full architectural report (PDF)
│   └── RESEARCH_BRIEF.txt           # High-level specification & hypotheses
├── paper/
│   └── pulselex_paper.tex           # LaTeX research paper
├── pulselex/
│   ├── __init__.py                  # Public exports
│   ├── audio.py                     # Acoustic CW WAV synthesizer
│   ├── channel.py                   # Binary symmetric channel model
│   ├── cli.py                       # Command-line interface
│   ├── codec.py                     # Alphabet mappings & (9,5)/(10,5) codec
│   ├── experiment.py                # Monte Carlo benchmark runner
│   └── sync.py                      # Continuous bitstream deframer & synchronizer
├── results/
│   ├── bit_error_experiment.csv     # 50,000-trial benchmark results
│   ├── experiment_summary.txt       # Benchmark summary
│   └── test_run.txt                 # Recorded test execution log
├── tests/
│   ├── test_audio.py                # Audio waveform unit tests
│   ├── test_channel.py              # Channel unit tests
│   ├── test_cli.py                  # CLI command unit tests
│   ├── test_codec.py                # Codec unit tests
│   ├── test_experiment.py           # Experiment runner unit tests
│   ├── test_secded.py               # SECDED 10-bit unit tests
│   └── test_sync.py                 # Synchronization & deframing tests
├── CONTRIBUTING.md                  # Development & contribution guidelines
├── LICENSE                          # MIT License
├── pyproject.toml                   # Project metadata & build configuration
├── references.bib                   # BibTeX bibliographic records
└── SECURITY.md                     # Security policy & reporting guidelines
```

---

## 局限性与范围

- **信道真实性：** 信道模拟器实现了独立无记忆的二进制对称信道。
- **字母表边界：** 字母表限制为 32 个状态（大写英文字母、空格、句号、逗号、问号、起始、结束）。数字和小写字母将被规范化或拒绝。
- **声学检测：** 音频模块目前仅合成声学波形；软件定义的麦克风音调解调计划在后续阶段实现。

---

## 贡献

欢迎贡献代码、报告 Bug 和研究扩展：

1. Fork 该仓库。
2. 创建一个功能分支（`git checkout -b feature/extension-name`）。
3. 确保所有测试通过（`pytest`）。
4. 提交您的更改并附上描述性的提交消息。
5. 发起一个 Pull Request。

---

## 参考文献与引用

如果您在学术工作中引用或基于 PulseLex 进行研究，请引用：

```bibtex
@misc{pulselex2026,
  author       = {{PulseLex Research Prototype}},
  title        = {PulseLex: A Morse-Inspired Fixed-Length Alphabet with Single-Bit Error Correction},
  year         = {2026},
  howpublished = {\url{https://github.com/hasheramin5-cyber/pLex}}
}
```

主要基础文献：
- International Telecommunication Union, *Recommendation ITU-R M.1677-1: International Morse Code*, 2009.
- R. W. Hamming, *Error Detecting and Error Correcting Codes*, Bell System Technical Journal, 1950.
- T. M. Cover and J. A. Thomas, *Elements of Information Theory*, Wiley, 2006.

---

## 许可证

本项目依据 [MIT License](LICENSE) 条款授权。
