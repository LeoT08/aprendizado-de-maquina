# -*- coding: utf-8 -*-
r"""Calibrador de cor - descobre a faixa HSV do objeto que voce tem em maos.

Como usar:
    .\.venv\Scripts\python.exe ferramentas\calibrar_cor.py

Clique com o mouse sobre o objeto na janela de video (pode clicar varias vezes,
em partes diferentes e com a luz que voce vai usar). O programa mostra a mascara
ao vivo e, ao sair com Q, imprime o trecho de codigo pronto para colar no notebook.
"""
import cv2
import numpy as np

amostras = []          # lista de pixels HSV clicados
raio = 4               # pega um quadradinho ao redor do clique, nao um pixel so
quadro_atual = None


def ao_clicar(evento, x, y, flags, param):
    if evento != cv2.EVENT_LBUTTONDOWN or quadro_atual is None:
        return
    hsv = cv2.cvtColor(quadro_atual, cv2.COLOR_BGR2HSV)
    altura, largura = hsv.shape[:2]
    y0, y1 = max(0, y - raio), min(altura, y + raio + 1)
    x0, x1 = max(0, x - raio), min(largura, x + raio + 1)
    bloco = hsv[y0:y1, x0:x1].reshape(-1, 3)
    amostras.extend(bloco.tolist())
    h, s, v = bloco.mean(axis=0).astype(int)
    print(f"  clique em ({x},{y}) -> H={h} S={s} V={v}   [{len(amostras)} amostras]")


def faixa_das_amostras(margem_h=12, margem_s=70, margem_v=70):
    """Devolve (baixo, alto) cobrindo as amostras, com folga."""
    a = np.array(amostras)
    h, s, v = a[:, 0], a[:, 1], a[:, 2]
    baixo = np.array([max(0, int(np.percentile(h, 5)) - margem_h),
                      max(30, int(np.percentile(s, 5)) - margem_s),
                      max(30, int(np.percentile(v, 5)) - margem_v)])
    alto = np.array([min(179, int(np.percentile(h, 95)) + margem_h),
                     255, 255])
    return baixo, alto


cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
    raise SystemExit("Nao consegui abrir a camera.")

JANELA = "Calibrador - clique no objeto | Q para sair"
cv2.namedWindow(JANELA)
cv2.setMouseCallback(JANELA, ao_clicar)

print("Clique no objeto algumas vezes. Pressione Q quando a mascara estiver boa.")
nucleo = np.ones((5, 5), np.uint8)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    quadro_atual = frame
    vis = frame.copy()

    if amostras:
        baixo, alto = faixa_das_amostras()
        mascara = cv2.inRange(cv2.cvtColor(frame, cv2.COLOR_BGR2HSV), baixo, alto)
        mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, nucleo)
        mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, nucleo)
        contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        area = max((cv2.contourArea(c) for c in contornos), default=0)
        if contornos and area > 200:
            cv2.drawContours(vis, [max(contornos, key=cv2.contourArea)], -1, (0, 255, 0), 2)
        cv2.putText(vis, f"H {baixo[0]}-{alto[0]}  S>={baixo[1]}  V>={baixo[2]}  area={area:.0f}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    else:
        mascara = np.zeros(frame.shape[:2], np.uint8)
        cv2.putText(vis, "clique no objeto", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.imshow(JANELA, np.hstack([vis, cv2.cvtColor(mascara, cv2.COLOR_GRAY2BGR)]))
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
cv2.waitKey(1)

if not amostras:
    print("\nNenhuma amostra coletada - nada a calibrar.")
else:
    baixo, alto = faixa_das_amostras()
    print("\n" + "=" * 62)
    print("COLE ISTO NO NOTEBOOK (celula do Passo 4), dentro do dicionario FAIXAS:")
    print("=" * 62)
    print(f'    "meu_objeto": [(np.array([{baixo[0]}, {baixo[1]}, {baixo[2]}]), '
          f'np.array([{alto[0]}, {alto[1]}, {alto[2]}]))],')
    print()
    print('E troque a linha da cor-alvo para:')
    print('    COR_ALVO = "meu_objeto"')
    print("=" * 62)
