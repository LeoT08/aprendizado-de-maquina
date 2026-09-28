# -*- coding: utf-8 -*-
r"""Procura imagens sem mao no dataset e monta folhas de contato para revisao.

O modo rajada salva a cada 0,45s, entao quadros capturados durante a troca de gesto
ou com a mao fora da caixa acabam gravados com o rotulo errado. O enunciado pede
"conferir se cada imagem foi salva na pasta correta" - e disso que esta ferramenta trata.

Ela NAO apaga nada. Mede a area de pele de cada imagem, lista as suspeitas e gera
um mosaico numerado por classe para conferencia visual.

    ..\.venv\Scripts\python.exe ferramentas\revisar_dataset.py
"""
import pathlib

import cv2
import numpy as np

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DATASET_DIR = RAIZ / "jokenpo_dataset"
ENTREGAS = RAIZ / "entregas"
CLASSES = ["PEDRA", "PAPEL", "TESOURA"]
LIMIAR_PELE = 12.0        # % da area; abaixo disso, provavelmente nao ha mao


def area_pele(img):
    """% de pixels na faixa de pele, em YCrCb (mais estavel que HSV para isso)."""
    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    mascara = cv2.inRange(ycrcb, np.array([0, 133, 77]), np.array([255, 173, 127]))
    nucleo = np.ones((5, 5), np.uint8)
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, nucleo)
    return 100.0 * (mascara > 0).mean(), mascara


def main():
    ENTREGAS.mkdir(exist_ok=True)
    suspeitas = []
    todas = {}

    for classe in CLASSES:
        arquivos = sorted((DATASET_DIR / classe).glob("*.jpg"))
        medidas = []
        for arq in arquivos:
            img = cv2.imread(str(arq))
            pele, _ = area_pele(img)
            medidas.append((arq, pele))
            if pele < LIMIAR_PELE:
                suspeitas.append((classe, arq.name, pele))
        todas[classe] = medidas
        peles = [p for _, p in medidas]
        print(f"{classe:8s} {len(arquivos):3d} imagens | pele: "
              f"min {min(peles):5.1f}%  mediana {np.median(peles):5.1f}%  max {max(peles):5.1f}%")

    print(f"\nSUSPEITAS (menos de {LIMIAR_PELE:.0f}% de pele - provavelmente sem mao):")
    if suspeitas:
        for classe, nome, pele in sorted(suspeitas, key=lambda t: t[2]):
            print(f"  {classe:8s} {nome:20s} {pele:5.1f}%")
    else:
        print("  nenhuma")
    print(f"\ntotal de suspeitas: {len(suspeitas)} de {sum(len(v) for v in todas.values())}")

    # folha de contato numerada, uma por classe
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    for classe in CLASSES:
        medidas = todas[classe]
        cols = 10
        rows = int(np.ceil(len(medidas) / cols))
        fig, axes = plt.subplots(rows, cols, figsize=(cols * 1.3, rows * 1.45))
        axes = np.atleast_1d(axes).ravel()
        for ax in axes:
            ax.axis("off")
        for ax, (arq, pele) in zip(axes, medidas):
            ax.imshow(cv2.cvtColor(cv2.imread(str(arq)), cv2.COLOR_BGR2RGB))
            n = arq.stem.split("_")[-1]
            ax.set_title(f"{n} | {pele:.0f}%", fontsize=6,
                         color="red" if pele < LIMIAR_PELE else "black")
            ax.axis("off")
        fig.suptitle(f"{classe} - numero do arquivo | % de pele "
                     f"(vermelho = suspeita de nao ter mao)", fontsize=10)
        plt.tight_layout()
        destino = ENTREGAS / f"revisao_{classe.lower()}.png"
        plt.savefig(destino, dpi=110)
        plt.close()
        print(f"folha de contato: {destino.name}")

    print("\nPara remover uma imagem errada:")
    print(r"  del jokenpo_dataset\TESOURA\tesoura_042.jpg")


if __name__ == "__main__":
    main()
