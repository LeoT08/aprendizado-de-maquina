# -*- coding: utf-8 -*-
r"""Confere o dataset de jokenpo antes de treinar a CNN.

Aplica as mesmas regras da celula 6 do notebook do professor (>=45 por classe,
desbalanceamento <=2x) e ainda procura problemas que so aparecem depois:
imagens duplicadas, quadros escuros demais e quadros desfocados.

    ..\.venv\Scripts\python.exe ferramentas\validar_dataset.py
"""
import pathlib

import cv2
import numpy as np

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DATASET_DIR = RAIZ / "jokenpo_dataset"
ENTREGAS = RAIZ / "entregas"
CLASSES = ["PEDRA", "PAPEL", "TESOURA"]
META = 45


def main():
    if not DATASET_DIR.exists():
        raise SystemExit(f"Pasta nao encontrada: {DATASET_DIR}\nRode coletar_gestos.bat primeiro.")

    problemas = []
    resumo = {}
    assinaturas = {}

    for classe in CLASSES:
        arquivos = sorted((DATASET_DIR / classe).glob("*.jpg"))
        escuras, borradas = [], []
        for arq in arquivos:
            img = cv2.imread(str(arq))
            if img is None:
                problemas.append(f"nao consegui ler: {arq.name}")
                continue
            cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            if cinza.mean() < 40:
                escuras.append(arq.name)
            if cv2.Laplacian(cinza, cv2.CV_64F).var() < 25:
                borradas.append(arq.name)
            chave = cv2.resize(cinza, (16, 16)).tobytes()
            assinaturas.setdefault(chave, []).append(f"{classe}/{arq.name}")
        resumo[classe] = dict(n=len(arquivos), escuras=escuras, borradas=borradas)

    print(f"{'classe':<10} {'imagens':>8} {'status':>16}")
    for c in CLASSES:
        n = resumo[c]["n"]
        status = "ok" if n >= META else (f"faltam {META - n}" if n else "VAZIA")
        print(f"{c:<10} {n:>8} {status:>16}")

    contagens = [resumo[c]["n"] for c in CLASSES]
    total = sum(contagens)
    print(f"\nTOTAL: {total}")

    # --- as duas regras que o notebook do professor exige ---------------------
    print("\nRegras da celula 6 do notebook:")
    ok_min = min(contagens) >= META if contagens else False
    print(f"  [{'ok' if ok_min else 'X '}] pelo menos {META} imagens de cada gesto")
    if contagens and min(contagens) > 0:
        razao = max(contagens) / min(contagens)
        ok_bal = razao <= 2
        print(f"  [{'ok' if ok_bal else 'X '}] desbalanceamento <= 2x  (atual: {razao:.2f}x)")
    else:
        ok_bal = False
        print("  [X ] desbalanceamento: ha classe vazia")

    # --- avisos que nao reprovam, mas custam acuracia -------------------------
    duplicadas = {k: v for k, v in assinaturas.items() if len(v) > 1}
    if duplicadas:
        print(f"\nAVISO: {len(duplicadas)} grupo(s) de imagens identicas:")
        for v in list(duplicadas.values())[:5]:
            print("   ", " = ".join(v))
    for c in CLASSES:
        if resumo[c]["escuras"]:
            print(f"\nAVISO: {len(resumo[c]['escuras'])} imagem(ns) muito escura(s) em {c}: "
                  f"{', '.join(resumo[c]['escuras'][:4])}")
        if resumo[c]["borradas"]:
            print(f"AVISO: {len(resumo[c]['borradas'])} imagem(ns) desfocada(s) em {c}: "
                  f"{', '.join(resumo[c]['borradas'][:4])}")
    for p in problemas:
        print("ERRO:", p)

    # --- amostra visual -------------------------------------------------------
    if total:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(3, 6, figsize=(12, 6.5))
        for linha, classe in enumerate(CLASSES):
            arquivos = sorted((DATASET_DIR / classe).glob("*.jpg"))
            escolhidos = np.linspace(0, len(arquivos) - 1, 6).astype(int) if arquivos else []
            for col in range(6):
                ax = axes[linha, col]
                ax.axis("off")
                if len(arquivos) and col < len(escolhidos):
                    img = cv2.imread(str(arquivos[escolhidos[col]]))
                    ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                if col == 0:
                    ax.set_title(classe, fontsize=11, loc="left")
        fig.suptitle("Amostra do dataset (6 imagens espalhadas por classe)", fontsize=11)
        plt.tight_layout()
        ENTREGAS.mkdir(exist_ok=True)
        destino = ENTREGAS / "amostra_dataset.png"
        plt.savefig(destino, dpi=100)
        print(f"\nAmostra salva em: {destino}")

    print()
    if ok_min and ok_bal:
        print("PRONTO PARA TREINAR: as duas regras do notebook passam.")
    else:
        print("AINDA NAO DA PARA TREINAR - colete mais imagens.")


if __name__ == "__main__":
    main()
