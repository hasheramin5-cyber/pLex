[English](README.md) | [简体中文](README.zh-CN.md) | [Português](README.pt-BR.md) | [日本語](README.ja.md) | [Español](README.es.md) | [Bahasa Indonesia](README.id.md)

# PulseLex

<p align="center">
  <img src="pLex-SocialPreview.png" alt="PulseLex" width="100%">
</p>

Un alfabeto de longitud fija inspirado en Morse con corrección de errores sistemática Hamming (9,5) y SECDED extendido (10,5).

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](pyproject.toml)
[![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue.svg)](pyproject.toml)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-51%20passed-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-98%25-brightgreen.svg)](tests/)

PulseLex es un prototipo experimental de investigación en telecomunicaciones y teoría de codificación. Investiga la sustitución de los caracteres de longitud variable y dependientes del tiempo del código Morse Internacional por cargas útiles uniformes de cinco bits, renderizando estados binarios como pulsos de punto y guión, y aplicando códigos de bloque lineales para garantizar la corrección de errores de un solo bit y la detección de errores de doble bit.

Es un artefacto de investigación educativo y de micro-telemetría, no un reemplazo para señalización RF de alta largura de banda operacional ni un cifrador criptográfico.

---

## Descripción General

El código Morse Internacional tradicional (Recomendación ITU-R M.1677-1) está optimizado para tecleo manual humano en canales claros. Sin embargo, depende en gran medida de la precisión temporal (intervalos de elemento de 1 unidad, intervalos de carácter de 3 unidades, intervalos de palabra de 7 unidades) y no proporciona corrección de errores de reenvío nativa. El jitter de temporización o el ruido del canal puede provocar la pérdida de trama en palabras enteras.

PulseLex explora un diseño alternativo:
- Cada carácter ocupa un bloque invariante de nueve pulsos (o diez pulsos SECDED).
- El encuadre de caracteres es determinista una vez establecida la sincronización del flujo.
- Los volteos de un solo bit aislados introducidos durante la transmisión se detectan y corrigen matemáticamente.
- El protocolo proporciona un modo SECDED Hamming extendido (10,5) que detecta errores de doble bit para eliminar correcciones incorrectas.
- La sincronización de ventana deslizante de flujo de bits continuo incorporada recupera el bloqueo de trama en flujos de pulso no segmentados.
- La síntesis de audio CW acústico de dependencia cero genera ráfagas de tono WAV limpias y formadas por coseno elevado para transmisión de brecha de aire de altavoz a micrófono.

---

## Características Principales

- **Códec Hamming Acortado (9,5) y SECDED (10,5):** Código de bloque sistemático que usa cuatro bits de paridad para proteger cinco bits de datos ($d_{\min} = 3$), con un 10º bit de paridad general opcional que proporciona Corrección de Error Único y Detección de Error Doble (SECDED, $d_{\min} = 4$).
- **Sincronizador de Preámbulo de Flujo de Bits Continuo:** El correlador de ventana deslizante se bloquea en flujos de pulso brutos y no segmentados sin depender de la separación de espacios en blanco artificiales.
- **Sintetizador de Forma de Onda CW Acústico:** El codificador de audio de biblioteca estándar exporta archivos WAV PCM mono de 16 bits con envolventes suaves de subida/bajada con ventana Hann para evitar la dispersión espectral y los clics de tecla.
- **Alfabeto de 32 Símbolos:** Mapeo completo de 26 letras mayúsculas en inglés, espacio, tres marcas de puntuación y marcadores de encuadre de inicio/fin dedicados.
- **Decodificación de Síndrome Defensiva:** Distingue entre cero errores, errores de un solo bit y errores de doble bit no corregibles, generando `DoubleErrorDetected` en lugar de corromper bits no corrompidos.
- **Simulador de Canal Simétrico Binario:** Modelo de canal Bernoulli de volteo de bits configurable para experimentos de transmisión estocástica.
- **Benchmarks de Monte Carlo Reproducibles:** Arnés de simulación automatizado que informa tasas de error de símbolo empíricas contra líneas de base no codificadas a CSV.
- **Manuscrito Académico:** Artículo de investigación LaTeX completo (`paper/pulselex_paper.tex`) con derivaciones formales, diagramas TikZ y citas BibTeX.
- **Cero Dependencias Externas:** Construido completamente con la Biblioteca Estándar de Python.

---

## Alfabeto de Símbolos

Cada símbolo se mapea a una carga útil binaria de 5 bits ($2^5 = 32$ estados únicos):

| Valor Decimal | Carga Útil de 5 Bits | Símbolo | Descripción |
|---:|:---:|:---:|---|
| 0–25 | `00000`–`11001` | A–Z | Alfabeto latino en mayúsculas |
| 26 | `11010` | Space | Delimitador de palabra |
| 27 | `11011` | `.` | Punto final |
| 28 | `11100` | `,` | Coma |
| 29 | `11101` | `?` | Signo de interrogación |
| 30 | `11110` | `START` | Marcador de preámbulo de mensaje |
| 31 | `11111` | `END` | Marcador de postámbulo de mensaje |

Un binario `0` se renderiza como un punto (`.`), y un binario `1` se renderiza como un guión (`-`).

---

## Arquitectura Técnica

Las palabras de código usan indexación sistemática basada en 1 de 1 a 9 (o 10 en modo SECDED). Los bits de paridad se asignan a potencias de dos (posiciones 1, 2, 4, 8), y cinco bits de carga útil ocupan las posiciones restantes (3, 5, 6, 7, 9):

```text
Standard (9,5):
Codeword Index:   1    2    3    4    5    6    7    8    9
Content Type:    p1   p2   d1   p4   d2   d3   d4   p8   d5
Bit Allocation: [ Parity ] [Data] [Parity] [   Data   ] [Parity] [Data]

Extended SECDED (10,5):
Codeword Index:   1    2    3    4    5    6    7    8    9   10
Content Type:    p1   p2   d1   p4   d2   d3   d4   p8   d5  p0 (Overall)
```

Bajo paridad par, las ecuaciones de verificación son:

$$\begin{aligned}
p_1 &= d_1 \oplus d_2 \oplus d_4 \oplus d_5 \\
p_2 &= d_1 \oplus d_3 \oplus d_4 \\
p_4 &= d_2 \oplus d_3 \oplus d_4 \\
p_8 &= d_5 \\
p_0 &= \bigoplus_{i=1}^9 c_i \quad \text{(SECDED mode only)}
\end{aligned}$$

### Flujo de Trabajo de Extremo a Extremo

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

- **Tasa de Código ($R$):**
  $$R_{(9,5)} = \frac{5}{9} \approx 0.556, \quad R_{(10,5)} = \frac{5}{10} = 0.500$$
- **Sobrecarga de Redundancia:**
  $$\text{Overhead}_{(9,5)} = \frac{9 - 5}{5} \times 100\% = 80\%, \quad \text{Overhead}_{(10,5)} = 100\%$$
- **Distancia Mínima de Hamming y Límites de Error:**
  - Estándar $(9,5)$: $d_{\min} = 3 \implies t = 1$ corrección de bit.
  - Extendido $(10,5)$: $d_{\min} = 4 \implies t = 1$ corrección de bit, $2$ bits de detección de error doble no corregible (SECDED).
- **Tasa de Error de Símbolo No Codificado (SER):** Para probabilidad de volteo de bit independiente $p$:
  $$P_{\text{uncoded}} = 1 - (1 - p)^5$$
  En $p = 0.01$, $P_{\text{uncoded}} \approx 0.04901$ (4,90%).
- **Tasa de Fallo de Bloque Hamming ($P_{\ge 2}$):** Probabilidad de dos o más errores de bit en un bloque de 9 bits:
  $$P_{\ge 2} = 1 - (1 - p)^9 - 9p(1 - p)^8$$
  En $p = 0.01$, $P_{\ge 2} \approx 0.00344$ (0,34%), lo que proporciona una reducción de ~14,3x en la probabilidad de error de símbolo.

---

## Instalación

### Requisitos Previos
- Python 3.10 o posterior.

### Instalación de Desarrollo Editable
```bash
git clone https://github.com/hasheramin5-cyber/pLex.git
cd pLex
python -m pip install -e .
```

### Dependencias de Desarrollo
Para instalar utilidades de prueba:
```bash
python -m pip install -e ".[dev]"
```

---

## Inicio Rápido y Uso

### 1. Interfaz de Línea de Comandos

#### Codificación Estándar y SECDED
```bash
# Standard 9-bit encoding
pulselex encode "HELLO, WORLD?"

# Extended 10-bit SECDED encoding (Double-Error Detection)
pulselex encode --extended "HELLO, WORLD?"
```

#### Decodificación de Bloques Separados por Espacios
```bash
pulselex decode "-------.. .....---- .-.-.-... --..-.--- --..-.--- ...----.. ..-.--... -.-.-.-.. .--..--.. ...----.. .--....-- --..-.--- .-.-..--- -.-.--.-- .--------"
```

#### Sincronización de Flujo Continuo y Desinmarcado
Recupere mensajes de flujos de bits no segmentados y ruidosos con ruido inicial/final:
```bash
pulselex sync-decode "..noise..-------..-..-..-..-....-.--------...noise.." --verbose
```

#### Síntesis de Audio CW Acústico (Exportación WAV)
Genere tonos de audio de 750 Hz suaves y formados por Hann:
```bash
pulselex audio "EMERGENCY" -o results/beacon.wav --freq 750 --dot-duration 0.050
```

### 2. Ejemplo de API de Python

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

El proyecto incluye una herramienta de benchmarking Monte Carlo empírica que evalúa las tasas de error de símbolo en diferentes tasas de ruido.

### Ejecutar Experimento
```bash
python -m pulselex.experiment --trials 50000 --seed 7 --output results/bit_error_experiment.csv
```

### Resultados de Referencia (50.000 ensayos por probabilidad, semilla 7)

| Prob. de Error de Bit ($p$) | SER de 5 Bits No Codificado | PulseLex (9,5) SER | Bloques Corregidos | Reducción de SER |
|---:|---:|---:|---:|---:|
| 0.001 | 0.004740 | 0.000000 | 421 | Completo (0 errores) |
| 0.005 | 0.024440 | 0.001000 | 2.183 | 24,4x |
| 0.010 | 0.048720 | 0.003260 | 4.329 | 14,9x |
| 0.020 | 0.095600 | 0.012260 | 8.303 | 7,8x |
| 0.050 | 0.229600 | 0.068120 | 17.175 | 3,4x |
| 0.100 | 0.409200 | 0.211820 | 26.360 | 1,9x |

*Datos de referencia almacenados en `results/bit_error_experiment.csv` y resumidos en `results/experiment_summary.txt`.*

---

## Pruebas

Ejecute el conjunto de pruebas automatizadas usando pytest:

```bash
pytest
```

Las 51 pruebas unitarias (98% de cobertura de línea) cubren:
- Corrección exhaustiva de errores de un solo bit en las 32 cargas útiles válidas y las 9 posiciones de bit (288 casos de prueba).
- Corrección de errores de un solo bit SECDED (320 casos de prueba) y detección exhaustiva de errores de doble bit (1.440 casos de prueba).
- Sincronización de flujo continuo, correlación de ventana deslizante de preámbulo y desinmarcado de límite de ruido.
- Síntesis de muestras de audio, formación de envolvente Hann y validación de encabezado de archivo WAV PCM de 16 bits estándar.
- Subcomandos de interfaz de línea de comandos (`encode`, `decode`, `sync-decode`, `audio`) y manejo de códigos de salida.
- Ejecutador de benchmark de experimento Monte Carlo y exportación de conjunto de datos CSV.
- Casos extremos, verificación de límites de parámetros y estados de canal sin ruido/ruido total.

---

## Compilación del Artículo de Investigación

El repositorio contiene un manuscrito académico (`paper/pulselex_paper.tex`) que detalla las pruebas matemáticas y los hallazgos del protocolo.

Para compilar usando una distribución LaTeX estándar:
```bash
pdflatex -output-directory=paper paper/pulselex_paper.tex
bibtex paper/pulselex_paper
pdflatex -output-directory=paper paper/pulselex_paper.tex
pdflatex -output-directory=paper paper/pulselex_paper.tex
```

---

## Estructura del Repositorio

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

## Limitaciones y Alcance

- **Realismo del Canal:** El simulador de canal implementa un Canal Simétrico Binario independiente y sin memoria.
- **Límite del Alfabeto:** El alfabeto está restringido a 32 estados (inglés en mayúsculas, espacio, punto, coma, signo de interrogación, inicio, fin). Los dígitos y las letras minúsculas se normalizan o rechazan.
- **Detección Acústica:** El módulo de audio actualmente sintetiza formas de onda acústicas; la demodulación de tono de micrófono definida por software está planificada para fases posteriores.

---

## Contribuir

Se agradecen contribuciones, informes de errores y extensiones de investigación:

1. Haga un fork del repositorio.
2. Cree una rama de características (`git checkout -b feature/extension-name`).
3. Asegúrese de que todas las pruebas pasen (`pytest`).
4. Confirme sus cambios con mensajes de confirmación descriptivos.
5. Abra un Pull Request.

---

## Referencias y Citación

Si hace referencia o se basa en PulseLex en trabajo académico, por favor cite:

```bibtex
@misc{pulselex2026,
  author       = {{PulseLex Research Prototype}},
  title        = {PulseLex: A Morse-Inspired Fixed-Length Alphabet with Single-Bit Error Correction},
  year         = {2026},
  howpublished = {\url{https://github.com/hasheramin5-cyber/pLex}}
}
```

Literatura fundacional primaria:
- International Telecommunication Union, *Recommendation ITU-R M.1677-1: International Morse Code*, 2009.
- R. W. Hamming, *Error Detecting and Error Correcting Codes*, Bell System Technical Journal, 1950.
- T. M. Cover and J. A. Thomas, *Elements of Information Theory*, Wiley, 2006.

---

## Licencia

Este proyecto está licenciado bajo los términos de la [MIT License](LICENSE).
