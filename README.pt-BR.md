[English](README.md) | [简体中文](README.zh-CN.md) | [Português](README.pt-BR.md) | [日本語](README.ja.md) | [Español](README.es.md) | [Bahasa Indonesia](README.id.md)

# PulseLex

<p align="center">
  <img src="pLex-SocialPreview.png" alt="PulseLex" width="100%">
</p>

Um alfabeto de comprimento fixo inspirado no Morse com correção de erros sistemática Hamming (9,5) e SECDED estendido (10,5).

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](pyproject.toml)
[![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue.svg)](pyproject.toml)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-51%20passed-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-98%25-brightgreen.svg)](tests/)

PulseLex é um protótipo experimental de pesquisa em telecomunicações e teoria de codificação. Ele investiga a substituição dos caracteres de comprimento variável e dependentes de temporização do código Morse Internacional por cargas úteis uniformes de cinco bits, renderizando estados binários como pulsos de ponto e traço, e aplicando códigos de bloco linear para garantir a correção de erros de bit único e a detecção de erros de bit duplo.

É um artefato de pesquisa educacional e de micro-telemetria, não uma substituta para sinalização de RF de alta largura de banda operacional e não um cifrador criptográfico.

---

## Visão Geral

O código Morse Internacional tradicional (Recomendação ITU-R M.1677-1) é otimizado para tecla manual humana em canais claros. No entanto, ele depende fortemente da precisão temporal (intervalos de elemento de 1 unidade, intervalos de caractere de 3 unidades, intervalos de palavra de 7 unidades) e não fornece correção de erros de encaminhamento nativa. Jitter de temporização ou ruído de canal pode causar perda de enquadramento em palavras inteiras.

PulseLex explora um design alternativo:
- Cada caractere ocupa um bloco invariante de nove pulsos (ou dez pulsos SECDED).
- O enquadramento de caracteres é determinístico uma vez que a sincronização de fluxo é estabelecida.
- Inversões de bit único isoladas introduzidas durante a transmissão são matematicamente detectadas e corrigidas.
- O protocolo fornece um modo SECDED Hamming estendido (10,5) que detecta erros de bit duplo para eliminar correções incorretas.
- A sincronização de janela deslizante de fluxo de bits contínuo embutida recupera o bloqueio de quadro em fluxos de pulso não segmentados.
- A síntese de áudio CW acústica de dependência zero gera rajadas de tom WAV limpas e moldadas por cosseno elevado para transmissão de lacuna de ar alto-falante para microfone.

---

## Principais Funcionalidades

- **Codec Hamming Encurtado (9,5) e SECDED (10,5):** Código de bloco sistemático usando quatro bits de paridade para proteger cinco bits de dados ($d_{\min} = 3$), com um 10º bit de paridade geral opcional fornecendo Correção de Erro Único e Detecção de Erro Duplo (SECDED, $d_{\min} = 4$).
- **Sincronizador de Preâmbulo de Fluxo de Bits Contínuo:** O correlacionador de janela deslizante trava em fluxos de pulso brutos e não segmentados sem depender de separação de espaço em branco artificial.
- **Sintetizador de Forma de Onda CW Acústico:** O codificador de áudio de biblioteca padrão exporta arquivos WAV PCM mono de 16 bits com envoltórias suaves de subida/descida com janela Hann para evitar espalhamento espectral e cliques de chave.
- **Alfabeto de 32 Símbolos:** Mapeamento abrangente de 26 letras maiúsculas em inglês, espaço, três marcas de pontuação e marcadores de enquadramento de início/fim dedicados.
- **Decodificação de Síndrome Defensiva:** Distingue entre zero erros, erros de bit único e erros de bit duplo não corrigíveis, levantando `DoubleErrorDetected` em vez de corromper bits não corrompidos.
- **Simulador de Canal Simétrico Binário:** Modelo de canal Bernoulli de inversão de bit configurável para experimentos de transmissão estocástica.
- **Benchmarks Monte Carlo Reproduzíveis:** Arnês de simulação automatizado que relata taxas de erro de símbolo empíricas contra linhas de base não codificadas para CSV.
- **Manuscrito Acadêmico:** Artigo de pesquisa LaTeX completo (`paper/pulselex_paper.tex`) com derivações formais, diagramas TikZ e citações BibTeX.
- **Zero Dependências Externas:** Construído inteiramente com a Biblioteca Padrão Python.

---

## Alfabeto de Símbolos

Cada símbolo mapeia para uma carga útil binária de 5 bits ($2^5 = 32$ estados únicos):

| Valor Decimal | Carga Útil de 5 Bits | Símbolo | Descrição |
|---:|:---:|:---:|---|
| 0–25 | `00000`–`11001` | A–Z | Alfabeto latino maiúsculo |
| 26 | `11010` | Space | Delimitador de palavra |
| 27 | `11011` | `.` | Ponto final |
| 28 | `11100` | `,` | Vírgula |
| 29 | `11101` | `?` | Ponto de interrogação |
| 30 | `11110` | `START` | Marcador de preâmbulo de mensagem |
| 31 | `11111` | `END` | Marcador de pós-âmbulo de mensagem |

Um binário `0` é renderizado como um ponto (`.`), e um binário `1` é renderizado como um traço (`-`).

---

## Arquitetura Técnica

As palavras de código usam indexação sistemática baseada em 1 de 1 a 9 (ou 10 no modo SECDED). Os bits de paridade são atribuídos a potências de dois (posições 1, 2, 4, 8), e cinco bits de carga útil ocupam as posições restantes (3, 5, 6, 7, 9):

```text
Standard (9,5):
Codeword Index:   1    2    3    4    5    6    7    8    9
Content Type:    p1   p2   d1   p4   d2   d3   d4   p8   d5
Bit Allocation: [ Parity ] [Data] [Parity] [   Data   ] [Parity] [Data]

Extended SECDED (10,5):
Codeword Index:   1    2    3    4    5    6    7    8    9   10
Content Type:    p1   p2   d1   p4   d2   d3   d4   p8   d5  p0 (Overall)
```

Sob paridade par, as equações de verificação são:

$$\begin{aligned}
p_1 &= d_1 \oplus d_2 \oplus d_4 \oplus d_5 \\
p_2 &= d_1 \oplus d_3 \oplus d_4 \\
p_4 &= d_2 \oplus d_3 \oplus d_4 \\
p_8 &= d_5 \\
p_0 &= \bigoplus_{i=1}^9 c_i \quad \text{(SECDED mode only)}
\end{aligned}$$

### Fluxo de Trabalho de Ponta a Ponta

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

## Fundamentos Matemáticos

- **Taxa de Código ($R$):**
  $$R_{(9,5)} = \frac{5}{9} \approx 0.556, \quad R_{(10,5)} = \frac{5}{10} = 0.500$$
- **Sobrecarga de Redundância:**
  $$\text{Overhead}_{(9,5)} = \frac{9 - 5}{5} \times 100\% = 80\%, \quad \text{Overhead}_{(10,5)} = 100\%$$
- **Distância Mínima de Hamming e Limites de Erro:**
  - Padrão $(9,5)$: $d_{\min} = 3 \implies t = 1$ correção de bit.
  - Estendido $(10,5)$: $d_{\min} = 4 \implies t = 1$ correção de bit, $2$ bits de detecção de erro duplo não corrigível (SECDED).
- **Taxa de Erro de Símbolo Não Codificado (SER):** Para probabilidade de inversão de bit independente $p$:
  $$P_{\text{uncoded}} = 1 - (1 - p)^5$$
  Em $p = 0.01$, $P_{\text{uncoded}} \approx 0.04901$ (4,90%).
- **Taxa de Falha de Bloco Hamming ($P_{\ge 2}$):** Probabilidade de dois ou mais erros de bit em um bloco de 9 bits:
  $$P_{\ge 2} = 1 - (1 - p)^9 - 9p(1 - p)^8$$
  Em $p = 0.01$, $P_{\ge 2} \approx 0.00344$ (0,34%), proporcionando uma redução de ~14,3x na probabilidade de erro de símbolo.

---

## Instalação

### Pré-requisitos
- Python 3.10 ou mais recente.

### Instalação de Desenvolvimento Editável
```bash
git clone https://github.com/hasheramin5-cyber/pLex.git
cd pLex
python -m pip install -e .
```

### Dependências de Desenvolvimento
Para instalar utilitários de teste:
```bash
python -m pip install -e ".[dev]"
```

---

## Início Rápido e Uso

### 1. Interface de Linha de Comando

#### Codificação Padrão e SECDED
```bash
# Standard 9-bit encoding
pulselex encode "HELLO, WORLD?"

# Extended 10-bit SECDED encoding (Double-Error Detection)
pulselex encode --extended "HELLO, WORLD?"
```

#### Decodificando Blocos Separados por Espaço
```bash
pulselex decode "-------.. .....---- .-.-.-... --..-.--- --..-.--- ...----.. ..-.--... -.-.-.-.. .--..--.. ...----.. .--....-- --..-.--- .-.-..--- -.-.--.-- .--------"
```

#### Sincronização de Fluxo Contínuo e Desinquadramento
Recupere mensagens de fluxos de bits não segmentados e ruidosos com ruído inicial/final:
```bash
pulselex sync-decode "..noise..-------..-..-..-..-....-.--------...noise.." --verbose
```

#### Síntese de Áudio CW Acústico (Exportação WAV)
Gere tons de áudio de 750 Hz suaves e moldados por Hann:
```bash
pulselex audio "EMERGENCY" -o results/beacon.wav --freq 750 --dot-duration 0.050
```

### 2. Exemplo de API Python

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

## Benchmarks Empíricos

O projeto inclui uma ferramenta de benchmarking Monte Carlo empírica que avalia as taxas de erro de símbolo em diferentes taxas de ruído.

### Executar Experimento
```bash
python -m pulselex.experiment --trials 50000 --seed 7 --output results/bit_error_experiment.csv
```

### Resultados de Referência (50.000 tentativas por probabilidade, semente 7)

| Prob. de Erro de Bit ($p$) | SER de 5 Bits Não Codificado | PulseLex (9,5) SER | Blocos Corrigidos | Redução de SER |
|---:|---:|---:|---:|---:|
| 0.001 | 0.004740 | 0.000000 | 421 | Completo (0 erros) |
| 0.005 | 0.024440 | 0.001000 | 2.183 | 24,4x |
| 0.010 | 0.048720 | 0.003260 | 4.329 | 14,9x |
| 0.020 | 0.095600 | 0.012260 | 8.303 | 7,8x |
| 0.050 | 0.229600 | 0.068120 | 17.175 | 3,4x |
| 0.100 | 0.409200 | 0.211820 | 26.360 | 1,9x |

*Dados de referência armazenados em `results/bit_error_experiment.csv` e resumidos em `results/experiment_summary.txt`.*

---

## Testes

Execute o conjunto de testes automatizados usando pytest:

```bash
pytest
```

Os 51 testes unitários (98% de cobertura de linha) cobrem:
- Correção exaustiva de erro de bit único em todos os 32 payloads válidos e todas as 9 posições de bit (288 casos de teste).
- Correção de erro de bit único SECDED (320 casos de teste) e detecção exaustiva de erro de bit duplo (1.440 casos de teste).
- Sincronização de fluxo contínuo, correlação de janela deslizante de preâmbulo e desinquadramento de limite de ruído.
- Síntese de amostra de áudio, modelagem de envoltória Hann e validação de cabeçalho de arquivo WAV PCM de 16 bits padrão.
- Subcomandos de interface de linha de comando (`encode`, `decode`, `sync-decode`, `audio`) e tratamento de código de saída.
- Executador de benchmark de experimento Monte Carlo e exportação de conjunto de dados CSV.
- Casos extremos, verificação de limite de parâmetros e estados de canal sem ruído/ruído total.

---

## Compilando o Artigo de Pesquisa

O repositório contém um manuscrito acadêmico (`paper/pulselex_paper.tex`) detalhando as provas matemáticas e as descobertas do protocolo.

Para compilar usando uma distribuição LaTeX padrão:
```bash
pdflatex -output-directory=paper paper/pulselex_paper.tex
bibtex paper/pulselex_paper
pdflatex -output-directory=paper paper/pulselex_paper.tex
pdflatex -output-directory=paper paper/pulselex_paper.tex
```

---

## Estrutura do Repositório

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

## Limitações e Escopo

- **Realismo do Canal:** O simulador de canal implementa um Canal Simétrico Binário independente e sem memória.
- **Limite do Alfabeto:** O alfabeto é restrito a 32 estados (inglês maiúsculo, espaço, ponto, vírgula, ponto de interrogação, início, fim). Dígitos e letras minúsculas são normalizados ou rejeitados.
- **Detecção Acústica:** O módulo de áudio atualmente sintetiza formas de onda acústicas; a demodulação de tom de microfone definida por software está planejada para fases subsequentes.

---

## Contribuindo

Contribuições, relatórios de bugs e extensões de pesquisa são bem-vindos:

1. Faça um fork do repositório.
2. Crie um branch de funcionalidade (`git checkout -b feature/extension-name`).
3. Certifique-se de que todos os testes passam (`pytest`).
4. Faça commit de suas alterações com mensagens de commit descritivas.
5. Abra um Pull Request.

---

## Referências e Citação

Se você referenciar ou basear-se no PulseLex em trabalho acadêmico, por favor cite:

```bibtex
@misc{pulselex2026,
  author       = {{PulseLex Research Prototype}},
  title        = {PulseLex: A Morse-Inspired Fixed-Length Alphabet with Single-Bit Error Correction},
  year         = {2026},
  howpublished = {\url{https://github.com/hasheramin5-cyber/pLex}}
}
```

Literatura fundacional primária:
- International Telecommunication Union, *Recommendation ITU-R M.1677-1: International Morse Code*, 2009.
- R. W. Hamming, *Error Detecting and Error Correcting Codes*, Bell System Technical Journal, 1950.
- T. M. Cover and J. A. Thomas, *Elements of Information Theory*, Wiley, 2006.

---

## Licença

Este projeto está licenciado sob os termos da [MIT License](LICENSE).
