"""Roda a entrega da Aula 7 de ponta a ponta.

Sequencia:
  1. treina o lutador rival da Copa (`treinar_rival.py`);
  2. sobe a arena sem janela (`arena_lcml.py`), que tambem salva a foto do choque;
  3. executa o notebook inteiro pelo protocolo TCP real (nbconvert --execute);
  4. exporta o HTML e copia os artefatos para `entregas/`;
  5. derruba a arena.

Uso:
    python ferramentas/executar_entrega.py
    python ferramentas/executar_entrega.py --so-notebook   # pula o treino do rival
"""

import argparse
import os
import shutil
import socket
import subprocess
import sys
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON = sys.executable
NOTEBOOK = "aula07_sumo_ia.ipynb"
PORTA = 5555

ARTEFATOS = [
    "teleop_sumo.csv",
    "lutador_equipe.joblib",
    "lutador_rival.joblib",
    NOTEBOOK,
]


def executar(comando, **kwargs):
    print(f"\n$ {' '.join(comando)}", flush=True)
    return subprocess.run(comando, cwd=RAIZ, check=True, **kwargs)


def porta_aberta(porta, tentativas=40):
    for _ in range(tentativas):
        try:
            with socket.create_connection(("127.0.0.1", porta), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.25)
    return False


def exigir_porta_livre(porta):
    """Uma arena esquecida de uma execucao anterior arruina a proxima.

    No Windows o bind usa SO_REUSEADDR, entao a arena nova sobe sem reclamar e as
    duas disputam a mesma porta: o notebook conecta numa delas e leva
    ConnectionReset quando aquela encerra. Melhor parar aqui com a mensagem certa.
    """
    if porta_aberta(porta, tentativas=1):
        raise SystemExit(
            f"ERRO: ja existe algo escutando em 127.0.0.1:{porta}.\n"
            "Feche a janela da arena (ou o processo python que a roda) e tente de novo."
        )


def principal():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--so-notebook", action="store_true")
    parser.add_argument("--timeout", type=int, default=2400, help="segundos para o notebook inteiro")
    args = parser.parse_args()

    os.makedirs(os.path.join(RAIZ, "entregas"), exist_ok=True)
    exigir_porta_livre(PORTA)

    if not args.so_notebook:
        executar([PYTHON, "ferramentas/treinar_rival.py"])

    print("\n=== subindo a arena (sem janela) ===", flush=True)
    arena = subprocess.Popen(
        [PYTHON, "ferramentas/arena_lcml.py", "--sem-janela",
         "--foto", "entregas/arena_luta.png", "--segundos", str(args.timeout)],
        cwd=RAIZ,
    )
    try:
        if not porta_aberta(PORTA):
            raise RuntimeError("a arena nao abriu a porta 5555")
        if arena.poll() is not None:
            raise RuntimeError(f"a arena morreu logo ao subir (codigo {arena.returncode})")
        print("arena no ar", flush=True)

        executar([PYTHON, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute",
                  "--inplace", NOTEBOOK, f"--ExecutePreprocessor.timeout={args.timeout}"])
        executar([PYTHON, "-m", "jupyter", "nbconvert", "--to", "html", NOTEBOOK,
                  "--output-dir", "entregas"])
    finally:
        arena.terminate()
        try:
            arena.wait(timeout=10)
        except subprocess.TimeoutExpired:
            arena.kill()
        print("arena encerrada", flush=True)

    for nome in ARTEFATOS:
        origem = os.path.join(RAIZ, nome)
        if os.path.exists(origem):
            shutil.copy2(origem, os.path.join(RAIZ, "entregas", os.path.basename(nome)))
            print("copiado para entregas/:", nome)

    print("\nEntrega executada. Confira entregas/ficha_copa.json")


if __name__ == "__main__":
    principal()
