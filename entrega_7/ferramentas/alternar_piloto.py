"""Troca quem pilota na etapa 2 do notebook: o piloto por regras ou as setas.

    python ferramentas/alternar_piloto.py --manual      # setas (janela tkinter)
    python ferramentas/alternar_piloto.py --automatico  # piloto_especialista
    python ferramentas/alternar_piloto.py               # so mostra como esta

Existe para nao precisar caçar a linha dentro do JSON do notebook na hora de
regravar as demonstracoes na mao.
"""

import argparse
import io
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTEBOOK = os.path.join(RAIZ, "aula07_sumo_ia.ipynb")
LINHA_AUTO = "PILOTO_AUTOMATICO = True"
LINHA_MANUAL = "PILOTO_AUTOMATICO = False"


def principal():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    grupo = parser.add_mutually_exclusive_group()
    grupo.add_argument("--manual", action="store_true", help="pilotar com as setas")
    grupo.add_argument("--automatico", action="store_true", help="piloto por regras")
    args = parser.parse_args()

    nb = json.load(io.open(NOTEBOOK, encoding="utf-8"))
    alvo = None
    for celula in nb["cells"]:
        if celula["cell_type"] != "code":
            continue
        for i, linha in enumerate(celula["source"]):
            if linha.startswith(("PILOTO_AUTOMATICO = True", "PILOTO_AUTOMATICO = False")):
                alvo = (celula, i, linha)
    if alvo is None:
        raise SystemExit("ERRO: nao achei a linha PILOTO_AUTOMATICO no notebook.")

    celula, indice, linha = alvo
    atual = "manual" if linha.startswith(LINHA_MANUAL) else "automatico"
    if not (args.manual or args.automatico):
        print(f"A etapa 2 esta em modo {atual}.")
        return

    novo = LINHA_MANUAL if args.manual else LINHA_AUTO
    comentario = "   # False = janela com as setas, para pilotar na mao\n"
    celula["source"][indice] = novo + comentario
    with io.open(NOTEBOOK, "w", encoding="utf-8") as saida:
        json.dump(nb, saida, indent=1, ensure_ascii=False)
        saida.write("\n")
    print(f"Etapa 2 agora em modo {'manual' if args.manual else 'automatico'} (antes: {atual}).")


if __name__ == "__main__":
    principal()
