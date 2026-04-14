# 🏋️ Smart Gym — Sistema de Treino Inteligente

Sistema que identifica alunos via cartão RFID e acompanha seus movimentos durante o treino usando visão computacional.

## 🎥 Demonstração

🔗 [Vídeo de demonstração](https://youtube.com/shorts/nIlWluPvjMQ)

## 📋 Descrição

O Smart Gym combina um leitor RFID (Arduino + MFRC522) com rastreamento de pose em tempo real (Python + MediaPipe) para:

- Identificar o aluno ao aproximar o cartão RFID do leitor
- Detectar e contar repetições de agachamento usando a câmera
- Exibir o ângulo do joelho em tempo real em um gráfico
- Registrar o progresso até atingir o objetivo de repetições

## 🗂️ Estrutura do Projeto

```
smart-gym/
├── smart_gym.ino              # Código do Arduino (leitura RFID)
├── smart_gym.py               # Código Python (visão computacional)
├── pose_landmarker_full.task  # Modelo do MediaPipe (ver instruções abaixo)
└── README.md
```

## 🔧 Hardware Necessário

| Componente | Quantidade |
|---|---|
| Arduino Uno (ou compatível) | 1 |
| Módulo RFID MFRC522 | 1 |
| Cartões/Tags RFID 13,56 MHz | 1+ |
| Câmera USB ou webcam integrada | 1 |
| Cabo USB (Arduino → PC) | 1 |

### Conexão Arduino ↔ MFRC522

| MFRC522 | Arduino Uno |
|---|---|
| SDA | Pino 10 |
| SCK | Pino 13 |
| MOSI | Pino 11 |
| MISO | Pino 12 |
| RST | Pino 9 |
| GND | GND |
| 3.3V | **3.3V** ⚠️ |

> [!WARNING]
> **O módulo MFRC522 opera em 3.3V. Conectá-lo ao pino de 5V do Arduino danifica permanentemente o leitor.** Verifique duas vezes antes de ligar — os pinos `3.3V` e `5V` ficam lado a lado no Arduino e são fáceis de confundir.

## 💻 Dependências

### Arduino

Instale as bibliotecas pelo **Arduino IDE → Ferramentas → Gerenciar Bibliotecas**:

- `MFRC522` (por GithubCommunity)
- `SPI` (já incluída no Arduino IDE)

### Python

Versão recomendada: **Python 3.9 ou superior**

```bash
pip install opencv-python mediapipe numpy matplotlib pyserial
```

### Modelo MediaPipe

Baixe o arquivo `pose_landmarker_full.task` no link abaixo e coloque na **mesma pasta** que o `smart_gym.py`:

🔗 [Download pose_landmarker_full.task](https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task)

## 🚀 Como Executar

### 1. Carregar o código no Arduino

1. Abra o arquivo `smart_gym.ino` no Arduino IDE
2. Conecte o Arduino via USB
3. Selecione a porta correta em **Ferramentas → Porta**
4. Clique em **Upload**

### 2. Descobrir a porta serial

Após fazer o upload, anote a porta do Arduino (ex: `COM3`, `COM5` no Windows; `/dev/ttyUSB0` no Linux/Mac).

### 3. Configurar a porta no código Python

Abra o `smart_gym.py` e altere a linha abaixo com a porta correta:

```python
ser = serial.Serial('COM5', 9600, timeout=0.1)  # ← altere aqui
```

### 4. Cadastrar os alunos (opcional)

No `smart_gym.py`, edite o dicionário `ALUNOS_REGISTRADOS` com os UIDs dos cartões:

```python
ALUNOS_REGISTRADOS = {
    "XX XX XX XX": {"nome": "Seu Nome", "exercicio": "Agachamento", "objetivo": 10},
}
```

> Para descobrir o UID do seu cartão: rode o Arduino, abra o Monitor Serial (9600 baud) e aproxime o cartão.

### 5. Executar o sistema

```bash
python smart_gym.py
```

## 🎮 Uso

| Ação | Resultado |
|---|---|
| Aproximar cartão cadastrado ao leitor | Inicia treino com perfil do aluno |
| Pressionar `S` | Inicia como Convidado (sem Arduino) |
| Pressionar `Q` | Encerra o programa |
| Agachar (ângulo < 90°) e levantar (ângulo > 160°) | Conta 1 repetição |

### Estados do sistema

```
AGUARDANDO_ID → TREINO_EM_CURSO → TREINO_CONCLUIDO → AGUARDANDO_ID
```

## ⚠️ Solução de Problemas

**Arduino não conecta**
- Verifique se a porta no código Python corresponde à porta real do dispositivo
- Certifique-se de que o Monitor Serial do Arduino IDE está fechado antes de rodar o Python

**Câmera não abre**
- Verifique se outra aplicação está usando a câmera
- Troque o índice da câmera: `cv2.VideoCapture(0)` → `cv2.VideoCapture(1)`

**Erro ao carregar o modelo MediaPipe**
- Confirme que o arquivo `pose_landmarker_full.task` está na mesma pasta que o `smart_gym.py`

**Cartão não reconhecido**
- Abra o Monitor Serial do Arduino IDE para ver o UID sendo lido
- Copie o UID exatamente como aparece e adicione ao dicionário `ALUNOS_REGISTRADOS`

## 👥 Integrantes do Grupo

- Nome 1
- Nome 2
- Nome 3

## 📚 Tecnologias Utilizadas

- [MediaPipe](https://mediapipe.dev/) — Detecção de pose humana
- [OpenCV](https://opencv.org/) — Captura e processamento de vídeo
- [MFRC522](https://github.com/miguelbalboa/rfid) — Biblioteca RFID para Arduino
- [PySerial](https://pyserial.readthedocs.io/) — Comunicação serial Python ↔ Arduino
- [Matplotlib](https://matplotlib.org/) — Gráfico de ângulo em tempo real
