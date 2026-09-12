# -*- coding: utf-8 -*-
r"""Captura guiada da Aula 1 - gera as prints da entrega.

Fica esperando voce mostrar o objeto e salva automaticamente uma print de cada zona
(ESQUERDA, CENTRO, DIREITA). Encerra quando tiver as tres ou quando o tempo acabar.

Como usar:
    .\.venv\Scripts\python.exe ferramentas\captura_guiada.py
    .\.venv\Scripts\python.exe ferramentas\captura_guiada.py --cor laranja
    .\.venv\Scripts\python.exe ferramentas\captura_guiada.py --cor verde --duracao 120

A janela mostra o video a esquerda e a mascara a direita: se o objeto aparece
BRANCO na mascara, a cor esta sendo detectada. Q encerra a qualquer momento.
"""
import argparse
import collections
import pathlib
import time

import cv2
import numpy as np

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ENTREGAS = RAIZ / "entregas"

# Mesmas faixas do notebook. Se voce calibrou com ferramentas/calibrar_cor.py,
# acrescente aqui a linha que o calibrador imprimiu.
FAIXAS = {
    "verde":    [(np.array([30,  30,  25]), np.array([95, 255, 255]))],  # calibrado no coco verde
    "azul":     [(np.array([95,  80,  50]), np.array([130, 255, 255]))],
    "amarelo":  [(np.array([20, 100, 100]), np.array([33, 255, 255]))],
    "laranja":  [(np.array([5,   90,  90]), np.array([22, 255, 255]))],
    "vermelho": [(np.array([0,  110,  70]), np.array([8,  255, 255])),
                 (np.array([170, 110, 70]), np.array([179, 255, 255]))],
}

ZONAS = ("ESQUERDA", "CENTRO", "DIREITA")
CORES = {"ESQUERDA": (0, 200, 255), "DIREITA": (255, 100, 0),
         "CENTRO": (0, 255, 0), "SEM_DETECCAO": (0, 0, 255)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cor", default="verde", choices=sorted(FAIXAS))
    p.add_argument("--duracao", type=int, default=120, help="segundos")
    p.add_argument("--area-minima", type=int, default=500)
    p.add_argument("--margem", type=int, default=80)
    args = p.parse_args()

    ENTREGAS.mkdir(exist_ok=True)
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        raise SystemExit("Nao consegui abrir a camera. Feche outros programas que usem a webcam.")

    nucleo = np.ones((5, 5), np.uint8)
    melhores, hist = {}, collections.Counter()
    maior_area = 0.0
    t0 = time.time()
    janela = f"Captura guiada [{args.cor}] - video | mascara  (Q para sair)"

    while time.time() - t0 < args.duracao:
        ret, frame = cap.read()
        if not ret:
            break
        altura, largura = frame.shape[:2]
        meio = largura // 2

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mascara = None
        for baixo, alto in FAIXAS[args.cor]:
            m = cv2.inRange(hsv, baixo, alto)
            mascara = m if mascara is None else cv2.bitwise_or(mascara, m)
        mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, nucleo)
        mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, nucleo)

        contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        comando, centro, area, contorno = "SEM_DETECCAO", None, 0.0, None
        if contornos:
            contorno = max(contornos, key=cv2.contourArea)
            area = cv2.contourArea(contorno)
            maior_area = max(maior_area, area)
            if area >= args.area_minima:
                M = cv2.moments(contorno)
                if M["m00"] > 0:
                    centro = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                    cx = centro[0]
                    comando = ("ESQUERDA" if cx < meio - args.margem
                               else "DIREITA" if cx > meio + args.margem else "CENTRO")
        hist[comando] += 1

        vis = frame.copy()
        cor = CORES[comando]
        for x in (meio - args.margem, meio + args.margem):
            cv2.line(vis, (x, 0), (x, altura), (200, 200, 200), 1)
        if centro is not None:
            cv2.drawContours(vis, [contorno], -1, cor, 2)
            cv2.circle(vis, centro, 20, cor, 3)
            cv2.line(vis, (centro[0], 0), (centro[0], altura), cor, 1)
            cv2.putText(vis, f"x={centro[0]}  area={area:.0f}", (10, altura - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, cor, 2)
            if area > melhores.get(comando, (0, None))[0]:
                melhores[comando] = (area, vis.copy())
        cv2.putText(vis, comando, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, cor, 3)

        faltam = [z for z in ZONAS if z not in melhores]
        dica = "PRONTO - pode fechar com Q" if not faltam else "leve o objeto para: " + ", ".join(faltam)
        cv2.putText(vis, dica, (10, altura - 45), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
        cv2.putText(vis, f"{args.duracao - (time.time() - t0):.0f}s", (largura - 70, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow(janela, np.hstack([vis, cv2.cvtColor(mascara, cv2.COLOR_GRAY2BGR)]))
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        if not faltam and time.time() - t0 > 5:
            break

    cap.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1)

    print("zonas capturadas:", sorted(melhores) or "nenhuma")
    print("maior area detectada:", round(maior_area))
    print("histograma:", dict(hist))

    for zona, (area, img) in melhores.items():
        destino = ENTREGAS / f"aula01_{zona.lower()}.png"
        cv2.imwrite(str(destino), img)
        print(f"  {zona:9s} area={area:7.0f} -> entregas/{destino.name}")

    if len(melhores) == 3:
        grade = np.hstack([cv2.resize(melhores[z][1], (426, 320)) for z in ZONAS])
        destino = ENTREGAS / "aula01_classificacao.png"
        cv2.imwrite(str(destino), grade)
        print(f"\nPAINEL FINAL -> entregas/{destino.name}")
        print("SUCESSO: as tres zonas foram detectadas com objeto real.")
    else:
        print("\nINCOMPLETO - faltaram:", [z for z in ZONAS if z not in melhores])
        if maior_area < args.area_minima:
            print("A cor nao foi detectada. Rode ferramentas/calibrar_cor.py para")
            print("descobrir a faixa HSV do objeto que voce tem, ou tente --cor laranja.")


if __name__ == "__main__":
    main()
