# -*- coding: utf-8 -*-
r"""Coleta as imagens de PEDRA, PAPEL e TESOURA para a Entrega 6.

Baseado na celula 4 do notebook do professor, mantendo exatamente o mesmo formato de saida
(jokenpo_dataset/<GESTO>/<gesto>_000.jpg, recorte quadrado central, imagem espelhada), com
tres acrescimos que o enunciado pede na pratica:

  - modo rajada: salva sozinho a cada N segundos enquanto voce move a mao,
    em vez de 45 toques no espaco por gesto
  - progresso por classe na tela, com a meta de 45
  - recusa imagens quase identicas a anterior ("evitar imagens quase identicas")

Como usar:
    ..\.venv\Scripts\python.exe ferramentas\coletar_gestos.py

Teclas:
    1 / 2 / 3   troca o gesto (PEDRA / PAPEL / TESOURA) sem fechar a janela
    ESPACO      salva um quadro
    A           liga/desliga o modo rajada
    Q           encerra
"""
import argparse
import pathlib
import time

import cv2
import numpy as np

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DATASET_DIR = RAIZ / "jokenpo_dataset"
CLASSES = ["PEDRA", "PAPEL", "TESOURA"]
META = 45

COR_OK = (0, 170, 0)
COR_FALTA = (0, 120, 220)
COR_ZERO = (0, 0, 220)


def contar(gesto):
    return len(list((DATASET_DIR / gesto).glob("*.jpg")))


def diferenca(a, b):
    """Diferenca media por pixel entre dois recortes, em cinza e reduzidos."""
    if a is None or b is None:
        return 255.0
    pa = cv2.resize(cv2.cvtColor(a, cv2.COLOR_BGR2GRAY), (32, 32)).astype(float)
    pb = cv2.resize(cv2.cvtColor(b, cv2.COLOR_BGR2GRAY), (32, 32)).astype(float)
    return float(np.abs(pa - pb).mean())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--intervalo", type=float, default=0.45,
                   help="segundos entre capturas no modo rajada")
    p.add_argument("--diferenca-minima", type=float, default=6.0,
                   help="recusa o quadro se for parecido demais com o anterior")
    p.add_argument("--camera", type=int, default=0)
    args = p.parse_args()

    for c in CLASSES:
        (DATASET_DIR / c).mkdir(parents=True, exist_ok=True)

    camera = cv2.VideoCapture(args.camera, cv2.CAP_DSHOW)
    if not camera.isOpened():
        raise SystemExit("Camera nao encontrada. Feche outros programas que usem a webcam.")

    gesto = CLASSES[0]
    rajada = False
    ultimo_salvo = None
    proxima = 0.0
    recusadas = 0
    janela = "Coleta Jokenpo - 1/2/3 troca gesto | ESPACO salva | A rajada | Q sai"

    print(__doc__)
    print(f"Salvando em: {DATASET_DIR}")

    while True:
        ok, frame = camera.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)                       # espelhado, como no notebook
        altura, largura = frame.shape[:2]
        lado = min(altura, largura) // 2
        esq, topo = (largura - lado) // 2, (altura - lado) // 2
        roi = frame[topo:topo + lado, esq:esq + lado].copy()

        agora = time.time()
        salvar = False
        if rajada and agora >= proxima:
            salvar = True
            proxima = agora + args.intervalo

        tecla = cv2.waitKey(1) & 0xFF
        if tecla == ord(" "):
            salvar = True
        elif tecla in (ord("q"), 27):
            break
        elif tecla == ord("a"):
            rajada = not rajada
            proxima = agora + args.intervalo
        elif tecla in (ord("1"), ord("2"), ord("3")):
            gesto = CLASSES[tecla - ord("1")]
            ultimo_salvo = None

        if salvar:
            d = diferenca(roi, ultimo_salvo)
            if d < args.diferenca_minima:
                recusadas += 1
            else:
                n = contar(gesto)
                cv2.imwrite(str(DATASET_DIR / gesto / f"{gesto.lower()}_{n:03d}.jpg"), roi)
                ultimo_salvo = roi
                print(f"  {gesto.lower()}_{n:03d}.jpg   (diferenca {d:.1f})")

        # ------------------------------------------------ interface
        cv2.rectangle(frame, (esq, topo), (esq + lado, topo + lado),
                      (0, 255, 0) if not rajada else (0, 200, 255), 2)
        cv2.putText(frame, f"{gesto}", (esq, topo - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        if rajada:
            cv2.putText(frame, "RAJADA", (esq + lado - 110, topo - 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 2)

        y = altura - 78
        total = 0
        for i, c in enumerate(CLASSES):
            n = contar(c)
            total += n
            cor = COR_OK if n >= META else (COR_ZERO if n == 0 else COR_FALTA)
            barra = int(160 * min(n / META, 1.0))
            x = 14 + i * 210
            cv2.putText(frame, f"{c} {n}/{META}", (x, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, cor, 1 + (c == gesto))
            cv2.rectangle(frame, (x, y + 8), (x + 160, y + 20), (90, 90, 90), 1)
            if barra:
                cv2.rectangle(frame, (x, y + 8), (x + barra, y + 20), cor, -1)

        faltam = sum(max(0, META - contar(c)) for c in CLASSES)
        rodape = (f"total {total} | faltam {faltam}" if faltam
                  else f"total {total} | META ATINGIDA nas 3 classes")
        if recusadas:
            rodape += f" | {recusadas} recusadas por repeticao"
        cv2.putText(frame, rodape, (14, altura - 16),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (240, 240, 240), 1)
        cv2.putText(frame, "1/2/3 gesto   ESPACO salva   A rajada   Q sai", (14, 26),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (240, 240, 240), 1)

        cv2.imshow(janela, frame)

    camera.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1)

    print("\nResumo:")
    for c in CLASSES:
        n = contar(c)
        print(f"  {c:8s} {n:3d}  ({'ok' if n >= META else f'faltam {META - n}'})")
    if recusadas:
        print(f"  {recusadas} quadros recusados por serem quase identicos ao anterior")
    print("\nConfira com: validar_dataset.bat")


if __name__ == "__main__":
    main()
