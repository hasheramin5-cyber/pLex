[English](README.md) | [简体中文](README.zh-CN.md) | [Português](README.pt-BR.md) | [日本語](README.ja.md) | [Español](README.es.md) | [Bahasa Indonesia](README.id.md)

# PulseLex

<p align="center">
  <img src="pLex-SocialPreview.png" alt="PulseLex" width="100%">
</p>

Morse にインスパイアされた固定長アルファベット。系統的な Hamming (9,5) および拡張 SECDED (10,5) 前方誤り訂正を備えます。

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](pyproject.toml)
[![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue.svg)](pyproject.toml)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-51%20passed-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-98%25-brightgreen.svg)](tests/)

PulseLex は実験的な電気通信・符号理論研究プロトタイプです。国際 Morse 符号の可変長・タイミング依存文字を均一な5ビットペイロードに置き換え、バイナリ状態を点・棒パルスとして描画し、線形ブロック符号を適用することで単一ビット誤り訂正および2ビット誤り検出を保証する手法を研究しています。

これは教育的・マイクロテレメトリ研究のためのアーティファクトであり、運用レベルの高帯域 RF 信号伝送の代替品でも、暗号システムでもありません。

---

## 概要

従来の国際 Morse 符号（ITU-R 勧告 M.1677-1）は、クリアなチャネル上での人間による手動キーイングに最適化されています。しかし、タイミング精度（1単位の要素ギャップ、3単位の文字ギャップ、7単位のワードギャップ）に大きく依存しており、ネイティブな前方誤り訂正は提供されません。タイミングジッタやチャネルノイズにより、単語全体でフレーム損失が発生する可能性があります。

PulseLex は代替設計を探求します：
- すべての文字が不変の9パルス（または10パルス SECDED）ブロックを占有します。
- ストリーム同期が確立されると、文字フレームは決定論的になります。
- 伝送中に導入された孤立した単一ビット反転は数学的に検出・訂正されます。
- プロトコルは拡張 Hamming (10,5) SECDED モードを提供し、誤訂正を排除するために2ビット誤りを検出します。
- 組み込みの連続ビットストリームスライディングウィンドウ同期により、非分割パルスストリームでフレームロックを回復します。
- ゼロ依存アコースティック CW 音声合成は、スピーカーからマイクへのエアギャップ伝送のための、クリーンな余弦整形 WAV トーンバーストを生成します。

---

## 主な機能

- **短縮 Hamming (9,5) および SECDED (10,5) コーデック：** 5つのデータビットを保護するために4つのパリティビットを使用する系統ブロック符号（$d_{\min} = 3$）。オプションの10番目の全体パリティビットにより、単一誤り訂正・2重誤り検出（SECDED、$d_{\min} = 4$）が可能です。
- **連続ビットストリームプリアンブル同期器：** スライディングウィンドウ相関器が、人工的な空白区切りに依存せず、未加工の非分割パルスストリームにロックします。
- **アコースティック CW 波形シンセサイザー：** 標準ライブラリの音声キーヤーが、スペクトル拡散とキークリックを防ぐための滑らかな Hann ウィンドウ処理された立ち上がり/立ち下がりエンベロープを持つ16ビットモノ PCM WAV ファイルをエクスポートします。
- **32シンボルアルファベット：** 26個の英語大文字、スペース、3つの句読点、専用の開始/終了フレームマーカーを包括的にマッピングします。
- **防御的シンドローム復号：** ゼロ誤り、単一ビット誤り、訂正不可能な2重ビット誤りを区別し、破損していないビットを破壊する代わりに `DoubleErrorDetected` を発生させます。
- **二進対称チャネルシミュレータ：** 確率的伝送実験のための設定可能な Bernoulli ビット反転チャネルモデル。
- **再現可能なモンテカルロベンチマーク：** 未符号化ベースラインに対する実証的なシンボル誤り率を CSV に報告する自動化シミュレーションハーネス。
- **学術論文：** 正式な導出、TikZ 図、BibTeX 引用を含む完全な LaTeX 研究論文（`paper/pulselex_paper.tex`）。
- **外部依存ゼロ：** Python 標準ライブラリのみで構築。

---

## シンボルアルファベット

各シンボルは5ビットバイナリペイロードにマッピングされます（$2^5 = 32$ 個のユニークな状態）：

| 10進数値 | 5ビットペイロード | シンボル | 説明 |
|---:|:---:|:---:|---|
| 0–25 | `00000`–`11001` | A–Z | 大文字ラテンアルファベット |
| 26 | `11010` | Space | 単語区切り |
| 27 | `11011` | `.` | ピリオド |
| 28 | `11100` | `,` | コンマ |
| 29 | `11101` | `?` | 疑問符 |
| 30 | `11110` | `START` | メッセージプリアンブルマーカー |
| 31 | `11111` | `END` | メッセージポストアンブルマーカー |

バイナリ `0` は点（`.`）として、バイナリ `1` は棒（`-`）として描画されます。

---

## 技術アーキテクチャ

コードワードは1から9まで（SECDED モードでは1から10まで）の系統的な1ベースインデックスを使用します。パリティビットは2の累乗の位置（位置1、2、4、8）に割り当てられ、5つのペイロードビットが残りの位置（3、5、6、7、9）を占有します：

```text
Standard (9,5):
Codeword Index:   1    2    3    4    5    6    7    8    9
Content Type:    p1   p2   d1   p4   d2   d3   d4   p8   d5
Bit Allocation: [ Parity ] [Data] [Parity] [   Data   ] [Parity] [Data]

Extended SECDED (10,5):
Codeword Index:   1    2    3    4    5    6    7    8    9   10
Content Type:    p1   p2   d1   p4   d2   d3   d4   p8   d5  p0 (Overall)
```

偶数パリティの下、検査方程式は以下の通りです：

$$\begin{aligned}
p_1 &= d_1 \oplus d_2 \oplus d_4 \oplus d_5 \\
p_2 &= d_1 \oplus d_3 \oplus d_4 \\
p_4 &= d_2 \oplus d_3 \oplus d_4 \\
p_8 &= d_5 \\
p_0 &= \bigoplus_{i=1}^9 c_i \quad \text{(SECDED mode only)}
\end{aligned}$$

### エンドツーエンドワークフロー

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

## 数学的基礎

- **符号率（$R$）：**
  $$R_{(9,5)} = \frac{5}{9} \approx 0.556, \quad R_{(10,5)} = \frac{5}{10} = 0.500$$
- **冗長オーバーヘッド：**
  $$\text{Overhead}_{(9,5)} = \frac{9 - 5}{5} \times 100\% = 80\%, \quad \text{Overhead}_{(10,5)} = 100\%$$
- **最小 Hamming 距離と誤り界：**
  - 標準 $(9,5)$：$d_{\min} = 3 \implies t = 1$ ビット訂正。
  - 拡張 $(10,5)$：$d_{\min} = 4 \implies t = 1$ ビット訂正、$2$ ビットの訂正不可能な2重誤り検出（SECDED）。
- **未符号化シンボル誤り率（SER）：** 独立ビット反転確率 $p$ について：
  $$P_{\text{uncoded}} = 1 - (1 - p)^5$$
  $p = 0.01$ のとき、$P_{\text{uncoded}} \approx 0.04901$（4.90%）。
- **Hamming ブロック失敗率（$P_{\ge 2}$）：** 9ビットブロック内で2つ以上のビット誤りが発生する確率：
  $$P_{\ge 2} = 1 - (1 - p)^9 - 9p(1 - p)^8$$
  $p = 0.01$ のとき、$P_{\ge 2} \approx 0.00344$（0.34%）、シンボル誤り確率が約14.3倍削減されます。

---

## インストール

### 前提条件
- Python 3.10 以降。

### 編集可能な開発インストール
```bash
git clone https://github.com/hasheramin5-cyber/pLex.git
cd pLex
python -m pip install -e .
```

### 開発依存関係
テストユーティリティのインストール：
```bash
python -m pip install -e ".[dev]"
```

---

## クイックスタートと使用方法

### 1. コマンドラインインターフェース

#### 標準および SECDED エンコーディング
```bash
# Standard 9-bit encoding
pulselex encode "HELLO, WORLD?"

# Extended 10-bit SECDED encoding (Double-Error Detection)
pulselex encode --extended "HELLO, WORLD?"
```

#### スペース区切りブロックのデコード
```bash
pulselex decode "-------.. .....---- .-.-.-... --..-.--- --..-.--- ...----.. ..-.--... -.-.-.-.. .--..--.. ...----.. .--....-- --..-.--- .-.-..--- -.-.--.-- .--------"
```

#### 連続ストリーム同期とデフレーミング
先頭/末尾のノイズを含む非分割のノイズの多いビットストリームからメッセージを回復します：
```bash
pulselex sync-decode "..noise..-------..-..-..-..-....-.--------...noise.." --verbose
```

#### アコースティック CW 音声合成（WAV エクスポート）
滑らかな Hann 整形 750 Hz 音声トーンを生成します：
```bash
pulselex audio "EMERGENCY" -o results/beacon.wav --freq 750 --dot-duration 0.050
```

### 2. Python API の例

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

## 実証的ベンチマーク

プロジェクトには、ノイズ率ごとのシンボル誤り率を評価する実証的なモンテカルロベンチマークツールが含まれています。

### 実験の実行
```bash
python -m pulselex.experiment --trials 50000 --seed 7 --output results/bit_error_experiment.csv
```

### 参照結果（確率あたり50,000試行、シード7）

| ビット誤り確率（$p$） | 未符号化5ビット SER | PulseLex (9,5) SER | 訂正ブロック数 | SER 削減率 |
|---:|---:|---:|---:|---:|
| 0.001 | 0.004740 | 0.000000 | 421 | 完全（0誤り）|
| 0.005 | 0.024440 | 0.001000 | 2,183 | 24.4x |
| 0.010 | 0.048720 | 0.003260 | 4,329 | 14.9x |
| 0.020 | 0.095600 | 0.012260 | 8,303 | 7.8x |
| 0.050 | 0.229600 | 0.068120 | 17,175 | 3.4x |
| 0.100 | 0.409200 | 0.211820 | 26,360 | 1.9x |

*参照データは `results/bit_error_experiment.csv` に保存され、`results/experiment_summary.txt` に要約されています。*

---

## テスト

pytest を使用して自動テストスイートを実行します：

```bash
pytest
```

51のユニットテスト（98%行カバレッジ）は以下をカバーします：
- すべての32個の有効ペイロードとすべての9ビット位置にわたる網羅的な単一ビット誤り訂正（288テストケース）。
- SECDED 単一ビット誤り訂正（320テストケース）および網羅的な2重ビット誤り検出（1,440テストケース）。
- 連続ストリーム同期、プリアンブルスライディングウィンドウ相関、およびノイズ境界デフレーミング。
- 音声サンプル合成、Hann エンベロープ整形、および標準16ビット PCM WAV ファイルヘッダー検証。
- コマンドラインインターフェースサブコマンド（`encode`、`decode`、`sync-decode`、`audio`）と終了コード処理。
- モンテカルロ実験ベンチマークランナーと CSV データセットエクスポート。
- エッジケース、パラメータ境界チェック、チャネルノイズなし/フルノイズ状態。

---

## 研究論文のコンパイル

リポジトリにはプロトコルの数学的証明と研究結果を詳述した学術論文（`paper/pulselex_paper.tex`）が含まれています。

標準 LaTeX ディストリビューションを使用してコンパイルする場合：
```bash
pdflatex -output-directory=paper paper/pulselex_paper.tex
bibtex paper/pulselex_paper
pdflatex -output-directory=paper paper/pulselex_paper.tex
pdflatex -output-directory=paper paper/pulselex_paper.tex
```

---

## リポジトリ構造

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

## 制限とスコープ

- **チャネルリアリズム：** チャネルシミュレータは独立な無記憶二進対称チャネルを実装しています。
- **アルファベット境界：** アルファベットは32状態（大文字英語、スペース、ピリオド、コンマ、疑問符、開始、終了）に制限されています。数字と小文字は正規化または拒否されます。
- **音響検出：** 音声モジュールは現在、音響波形を合成するのみです。ソフトウェア定義のマイクロフォントーン復調は後続フェーズで予定されています。

---

## コントリビューティング

コントリビューション、バグレポート、および研究拡張を歓迎します：

1. リポジトリをフォークします。
2. フィーチャーブランチを作成します（`git checkout -b feature/extension-name`）。
3. すべてのテストが通過することを確認します（`pytest`）。
4. 説明的なコミットメッセージで変更をコミットします。
5. プルリクエストを開きます。

---

## 参考文献と引用

学術研究で PulseLex を参照または活用する場合は、以下を引用してください：

```bibtex
@misc{pulselex2026,
  author       = {{PulseLex Research Prototype}},
  title        = {PulseLex: A Morse-Inspired Fixed-Length Alphabet with Single-Bit Error Correction},
  year         = {2026},
  howpublished = {\url{https://github.com/hasheramin5-cyber/pLex}}
}
```

主要な基礎文献：
- International Telecommunication Union, *Recommendation ITU-R M.1677-1: International Morse Code*, 2009.
- R. W. Hamming, *Error Detecting and Error Correcting Codes*, Bell System Technical Journal, 1950.
- T. M. Cover and J. A. Thomas, *Elements of Information Theory*, Wiley, 2006.

---

## ライセンス

このプロジェクトは [MIT License](LICENSE) の条件の下でライセンスされています。
