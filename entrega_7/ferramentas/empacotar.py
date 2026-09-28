"""Monta o zip de upload da Aula 7.

Junta o que a entrega pede (notebook executado, HTML, dataset, modelos, figuras,
CSVs e os documentos) mais as ferramentas escritas pelo grupo - o RESULTADOS cita
`arena_lcml.py` e `piloto_especialista.py`, entao eles precisam viajar junto.

Uso:
    python ferramentas/empacotar.py
"""

import os
import zipfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, "sumo.zip")
TOPO = "sumo"

ARQUIVOS = [
    "README.md",
    "RESULTADOS_ENTREGA7.md",
    # Copias de trabalho na raiz: o notebook le e escreve nelas quando e reexecutado.
    "aula07_sumo_ia.ipynb",
    "teleop_sumo.csv",
    "lutador_equipe.joblib",
    "lutador_rival.joblib",
    "abrir_arena.bat",
    "rodar_entrega.bat",
    "regravar_na_mao.bat",
]

PASTAS = ["entregas", "ferramentas", "arena"]

IGNORAR = ("__pycache__", ".ipynb_checkpoints", ".pyc")


def principal():
    itens = []
    for nome in ARQUIVOS:
        caminho = os.path.join(RAIZ, nome)
        if os.path.exists(caminho):
            itens.append((caminho, f"{TOPO}/{nome}"))
        else:
            print("faltando (pulado):", nome)

    for pasta in PASTAS:
        base = os.path.join(RAIZ, pasta)
        for diretorio, _, arquivos in os.walk(base):
            if any(marca in diretorio for marca in IGNORAR):
                continue
            for arquivo in arquivos:
                if arquivo.endswith(IGNORAR):
                    continue
                caminho = os.path.join(diretorio, arquivo)
                relativo = os.path.relpath(caminho, RAIZ).replace("\\", "/")
                itens.append((caminho, f"{TOPO}/{relativo}"))

    with zipfile.ZipFile(SAIDA, "w", zipfile.ZIP_DEFLATED) as zip_saida:
        for caminho, destino in itens:
            zip_saida.write(caminho, destino)

    tamanho = os.path.getsize(SAIDA) / 1024
    print(f"{SAIDA} | {len(itens)} arquivos | {tamanho:.0f} KB")


if __name__ == "__main__":
    principal()
