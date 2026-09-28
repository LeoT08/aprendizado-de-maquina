"""Copa de N lutas com largada sorteada - para a melhor de 3 dizer alguma coisa.

O problema que este script resolve
----------------------------------
A melhor de 3 da celula 7 do notebook deu 3 x 0 com as tres lutas durando
6,47s **exatamente**. Nao e coincidencia: a arena sempre recomeca na mesma
posicao, e os dois lutadores sao MLPs deterministicas (sem exploracao na hora de
decidir). Mesma largada + mesma politica = mesma luta, repetida tres vezes. O
placar 3 x 0 carrega tanta informacao quanto um placar de 1 x 0.

Aqui cada luta comeca com posicao e angulo sorteados dentro da plataforma, entao
as 20 lutas sao 20 situacoes diferentes e o placar vira uma medida.

Roda em memoria, contra a classe `Arena` importada, com o mesmo dt da arena real.

Uso:
    python ferramentas/copa_estendida.py
    python ferramentas/copa_estendida.py --lutas 40
"""

import argparse
import os
import random
import sys
from collections import Counter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "arena"))

import arena_robos as ar  # noqa: E402
import joblib  # noqa: E402
import pandas as pd  # noqa: E402

COLUNAS = [f"raio{i}" for i in range(5)] + ["vel", "bearing", "dist_inimigo", "dist_centro"]


def features(estado):
    return estado["raios"] + [estado["vel"], estado["inimigo_bearing"] / 180.0,
                              estado["inimigo_dist"], estado["dist_centro"]]


def luta(modelo_a, modelo_b, semente, limite=95.0):
    rng = random.Random(semente)
    arena = ar.Arena(modo="sumo")
    arena.a.rot = rng.uniform(-90, 90)
    arena.a.x += rng.uniform(-30, 30)
    arena.a.y += rng.uniform(-70, 70)
    arena.b.rot = 180 + rng.uniform(-90, 90)
    arena.b.x += rng.uniform(-30, 30)
    arena.b.y += rng.uniform(-70, 70)
    dt = 1.0 / ar.FPS
    while arena.fase != "FIM" and arena.tempo < limite:
        if arena.fase == "CORRIDA":
            entrada_a = pd.DataFrame([features(arena.estado(arena.a, arena.b))], columns=COLUNAS)
            entrada_b = pd.DataFrame([features(arena.estado(arena.b, arena.a))], columns=COLUNAS)
            acao_a = modelo_a.predict(entrada_a)[0]
            acao_b = modelo_b.predict(entrada_b)[0]
        else:
            acao_a, acao_b = "PARAR", "PARAR"
        arena.passo(dt, acao_bot_a=acao_a, acao_bot_b=acao_b)
    return arena.vencedor, arena.caiu, round(arena.tempo, 2)


class ModeloDePiloto:
    """Deixa o piloto por regras entrar na Copa com a mesma interface do modelo.

    Serve para responder uma pergunta que so faz sentido nas MESMAS largadas:
    a rede luta tao bem quanto o piloto que ela imitou?
    """

    def __init__(self, politica):
        self.politica = politica

    def predict(self, quadro):
        estado = {
            "raios": [float(quadro[f"raio{i}"].iloc[0]) for i in range(5)],
            "vel": float(quadro["vel"].iloc[0]),
            "inimigo_bearing": float(quadro["bearing"].iloc[0]) * 180.0,
            "inimigo_dist": float(quadro["dist_inimigo"].iloc[0]),
            "dist_centro": float(quadro["dist_centro"].iloc[0]),
        }
        return [self.politica(estado)]


def principal():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--lutas", type=int, default=20)
    parser.add_argument("--comparar-piloto", action="store_true",
                        help="roda tambem o piloto por regras nas mesmas largadas")
    parser.add_argument("--saida", default=os.path.join(RAIZ, "entregas", "copa_estendida.csv"))
    args = parser.parse_args()

    equipe = joblib.load(os.path.join(RAIZ, "lutador_equipe.joblib"))
    rival = joblib.load(os.path.join(RAIZ, "lutador_rival.joblib"))

    linhas = []
    for i in range(args.lutas):
        vencedor, caiu, duracao = luta(equipe, rival, semente=3000 + i)
        linhas.append({"luta": i + 1, "semente": 3000 + i, "vencedor": vencedor,
                       "caiu": caiu, "duracao_s": duracao})
        print(f"luta {i + 1:>2}: vencedor {str(vencedor):>4} | caiu {str(caiu):>4} | t {duracao}s")

    tabela = pd.DataFrame(linhas)
    os.makedirs(os.path.dirname(args.saida), exist_ok=True)
    tabela.to_csv(args.saida, index=False)

    contagem = Counter(tabela["vencedor"].fillna("empate"))
    print("\nPlacar:", dict(contagem))
    print(f"Nosso lutador (A): {contagem.get('A', 0)}/{args.lutas} "
          f"| rival (B): {contagem.get('B', 0)}/{args.lutas} "
          f"| sem vencedor: {contagem.get('empate', 0)}")
    print(f"Duracao mediana: {tabela['duracao_s'].median()}s | "
          f"lutas distintas (duracoes unicas): {tabela['duracao_s'].nunique()}/{args.lutas}")
    print("Salvo em", args.saida)

    if args.comparar_piloto:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from piloto_especialista import piloto_agressivo

        professor = ModeloDePiloto(piloto_agressivo)
        resultado = [luta(professor, rival, semente=3000 + i)[0] for i in range(args.lutas)]
        vitorias = sum(v == "A" for v in resultado)
        print(f"\nMesmas {args.lutas} largadas, mas com o PILOTO POR REGRAS no lugar da rede:")
        print(f"  piloto: {vitorias}/{args.lutas} | rede: {contagem.get('A', 0)}/{args.lutas}")
        print("  Se a rede fica abaixo do piloto que copiou, o problema nao e a estrategia:")
        print("  e a imitacao. Veja ferramentas/analise_imitacao.py.")


if __name__ == "__main__":
    principal()
