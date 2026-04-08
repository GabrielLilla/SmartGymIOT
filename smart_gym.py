import cv2
import time
import mediapipe as mp
import numpy as np
import serial
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os

# --- 1. CONFIGURACOES INICIAIS ---
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# ---------------------------------------------------------------
#  Conexão com o Arduino (MFRC522 via SPI)
#  O Arduino envia o UID do cartão RFID via Serial quando
#  um cartão é aproximado ao leitor.
# ---------------------------------------------------------------
arduino_conectado = False
ser = None
try:
    ser = serial.Serial('COM5', 9600, timeout=0.1)
    time.sleep(2)  # Aguarda o Arduino reiniciar após conexão serial
    arduino_conectado = True
    print("Arduino + MFRC522 ON - Aproxime o cartao ao leitor.")
except Exception as e:
    print(f"Arduino OFF ({e}) - Apenas modo Convidado disponivel (Tecla 'S')")

# Setup MediaPipe
model_path = 'pose_landmarker_full.task'
base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO
)
detector = vision.PoseLandmarker.create_from_options(options)

# --- 2. GRAFICO ---
fig = plt.figure(figsize=(7, 2.5), dpi=100)
ax = fig.add_subplot(111)
ax.set_facecolor('black')
fig.set_facecolor('black')
canvas = FigureCanvas(fig)

# --- 3. DATABASE E LOGICA ---
ALUNOS_REGISTRADOS = {
    "2A 63 4C 73": {"nome": "Lucas", "exercicio": "Agachamento", "objetivo": 5},
    "43 B6 49 05": {"nome": "Maria", "exercicio": "Agachamento", "objetivo": 8}
}

PERFIL_CONVIDADO = {"nome": "Convidado", "exercicio": "Agachamento", "objetivo": 3}

estado_app        = "AGUARDANDO_ID"
perfil_ativo      = None
contador_reps     = 0
estagio_exercicio = ""
historico_angulo  = []

# ---------------------------------------------------------------
#  Buffer acumulador — garante leitura robusta de UIDs com espaços
#  ex: "4A B9 3B 1B" que podem chegar fragmentados via serial
# ---------------------------------------------------------------
serial_buffer = ""


def ler_id_serial(ser) -> str | None:
    """
    Lê bytes disponíveis na serial, acumula em buffer e retorna
    uma linha completa (terminada em '\\n') sem espaços extras.
    Normaliza para MAIÚSCULAS para casar com o dicionário.
    Retorna None enquanto a linha ainda não estiver completa.
    """
    global serial_buffer
    if ser is None or ser.in_waiting == 0:
        return None

    serial_buffer += ser.read(ser.in_waiting).decode('utf-8', errors='ignore')

    if '\n' in serial_buffer:
        linha, serial_buffer = serial_buffer.split('\n', 1)
        id_lido = linha.strip().upper()  # MFRC522 pode enviar minúsculas
        return id_lido if id_lido else None

    return None


def calcular_angulo(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radianos = (np.arctan2(c[1] - b[1], c[0] - b[0])
                - np.arctan2(a[1] - b[1], a[0] - b[0]))
    angulo = np.abs(radianos * 180.0 / np.pi)
    if angulo > 180.0:
        angulo = 360 - angulo
    return angulo


# --- 4. LOOP PRINCIPAL ---
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    tecla = cv2.waitKey(1) & 0xFF

    # ==============================================================
    #  ESTADO: AGUARDANDO_ID
    # ==============================================================
    if estado_app == "AGUARDANDO_ID":

        if arduino_conectado:
            id_lido = ler_id_serial(ser)
            if id_lido:
                print(f"[RFID] UID recebido: '{id_lido}'")
                if id_lido in ALUNOS_REGISTRADOS:
                    perfil_ativo      = ALUNOS_REGISTRADOS[id_lido]
                    historico_angulo  = []
                    contador_reps     = 0
                    estado_app        = "TREINO_EM_CURSO"
                    print(f"Aluno identificado: {perfil_ativo['nome']}")
                else:
                    print(f"Cartao '{id_lido}' nao cadastrado.")

        if tecla == ord('s'):
            perfil_ativo      = PERFIL_CONVIDADO
            historico_angulo  = []
            contador_reps     = 0
            estado_app        = "TREINO_EM_CURSO"
            print("Iniciando como Aluno Convidado.")

        if arduino_conectado:
            msg = "APROXIME O CARTAO AO LEITOR OU APERTE 'S' (CONVIDADO)"
        else:
            msg = "ARDUINO DESCONECTADO — APERTE 'S' PARA CONTINUAR COMO CONVIDADO"

        cv2.putText(frame, msg, (20, h // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    # ==============================================================
    #  ESTADO: TREINO_EM_CURSO
    # ==============================================================
    elif estado_app == "TREINO_EM_CURSO":
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image  = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        resultado = detector.detect_for_video(mp_image, int(time.time() * 1000))

        if resultado.pose_landmarks:
            marcos = resultado.pose_landmarks[0]

            quadril   = [int(marcos[23].x * w), int(marcos[23].y * h)]
            joelho    = [int(marcos[25].x * w), int(marcos[25].y * h)]
            tornozelo = [int(marcos[27].x * w), int(marcos[27].y * h)]

            angulo = calcular_angulo(quadril, joelho, tornozelo)
            historico_angulo.append(angulo)
            if len(historico_angulo) > 50:
                historico_angulo.pop(0)

            cv2.line(frame, tuple(quadril),   tuple(joelho),    (255, 255, 255), 2)
            cv2.line(frame, tuple(joelho),    tuple(tornozelo), (255, 255, 255), 2)
            for p in [quadril, joelho, tornozelo]:
                cv2.circle(frame, tuple(p), 8, (0, 0, 255), -1)

            if angulo > 160:
                estagio_exercicio = "em_pe"
            if angulo < 90 and estagio_exercicio == "em_pe":
                estagio_exercicio = "agachado"
                contador_reps    += 1

            ax.clear()
            ax.plot(historico_angulo, color='#00FFFF', linewidth=2)
            ax.set_ylim(0, 180)
            ax.set_title("ANGULO DO JOELHO EM TEMPO REAL", color='white', fontsize=10)
            canvas.draw()
            grafico_img = cv2.cvtColor(
                np.asarray(canvas.buffer_rgba()), cv2.COLOR_RGBA2BGR)
            grafico_img = cv2.resize(grafico_img, (w, 200))
            frame = np.vstack((frame, grafico_img))

            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (w, 50), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

            status = (f"ALUNO: {perfil_ativo['nome']} | "
                      f"REPS: {contador_reps}/{perfil_ativo['objetivo']}")
            cv2.putText(frame, status, (15, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            if contador_reps >= perfil_ativo['objetivo']:
                estado_app = "TREINO_CONCLUIDO"

    # ==============================================================
    #  ESTADO: TREINO_CONCLUIDO
    # ==============================================================
    elif estado_app == "TREINO_CONCLUIDO":
        cv2.putText(frame, "TREINO CONCLUIDO!", (w // 2 - 150, h // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
        cv2.imshow('Academia Inteligente', frame)
        cv2.waitKey(3000)
        estado_app = "AGUARDANDO_ID"

    cv2.imshow('Academia Inteligente', frame)
    if tecla == ord('q'):
        break

cap.release()
if ser:
    ser.close()
cv2.destroyAllWindows()
