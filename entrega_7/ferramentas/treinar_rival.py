"""Treina o lutador rival da Copa (etapa 7).

O enunciado manda receber o `lutador_rival.joblib` de outra equipe. Enquanto esse
arquivo nao chega, este script treina um adversario com estilo DIFERENTE do nosso
(`piloto_cauteloso`: abandona a borda cedo, exige mira fina, freia na chegada),
para que a Copa seja uma disputa entre duas politicas distintas e nao um espelho
do mesmo comportamento. Quando o arquivo da outra equipe chegar, basta substituir
`lutador_rival.joblib` e rodar a celula 7 do notebook de novo.

Diferenca em relacao ao lutador da equipe: aqui as demonstracoes sao geradas
direto contra a classe `Arena` importada, sem passar pelo TCP. O rival e material
de apoio, nao a entrega avaliada - e rodar em memoria leva segundos em vez de
minutos. O lutador da equipe, esse sim, e coletado e testado pelo protocolo real
dentro do notebook.

Uso:
    python ferramentas/treinar_rival.py
"""

import argparse
import os
import random
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "arena"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import arena_robos as ar  # noqa: E402
import joblib  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.metrics import accuracy_score, classification_report  # noqa: E402
from sklearn.model_selection import train_test_split  # noqa: E402
from sklearn.neural_network import MLPClassifier  # noqa: E402
from sklearn.pipeline import Pipeline  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402

from piloto_especialista import PilotoRuidoso  # noqa: E402

COLUNAS = [f"raio{i}" for i in range(5)] + ["vel", "bearing", "dist_inimigo", "dist_centro"]


def features(estado):
    return estado["raios"] + [estado["vel"], estado["inimigo_bearing"] / 180.0,
                              estado["inimigo_dist"], estado["dist_centro"]]


def simular(politica, semente, registros=None, sortear_largada=True, limite=95.0):
    """Roda uma luta contra o bot interno reproduzindo a fisica real da arena.

    O laco e o mesmo de `principal()` em arena_robos.py: dt fixo de 1/FPS e o bot
    interno decidindo por B. A diferenca e que nao ha janela nem socket, entao a
    luta roda tao rapido quanto o processador permite.
    """
    rng = random.Random(semente)
    arena = ar.Arena(modo="sumo")
    if sortear_largada:
        # Sem variar a largada a simulacao e deterministica e todas as lutas saem iguais.
        arena.a.rot = rng.uniform(-90, 90)
        arena.a.x += rng.uniform(-30, 30)
        arena.a.y += rng.uniform(-70, 70)
        arena.b.rot = 180 + rng.uniform(-90, 90)
        arena.b.x += rng.uniform(-30, 30)
        arena.b.y += rng.uniform(-70, 70)
    dt = 1.0 / ar.FPS
    while arena.fase != "FIM" and arena.tempo < limite:
        if arena.fase == "CORRIDA":
            estado = arena.estado(arena.a, arena.b)
            acao = politica(estado)
            if registros is not None:
                registros.append(features(estado) + [acao])
            acao_b = arena.decidir_bot(arena.b, arena.a)
        else:
            acao, acao_b = "PARAR", None
        arena.passo(dt, acao_bot_a=acao, acao_bot_b=acao_b)
    return arena.vencedor, round(arena.tempo, 1)


def principal():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--lutas", type=int, default=16)
    parser.add_argument("--saida", default=os.path.join(RAIZ, "lutador_rival.joblib"))
    parser.add_argument("--estilo", default="cauteloso")
    args = parser.parse_args()

    piloto = PilotoRuidoso(args.estilo, ruido=0.05, semente=99)
    registros = []
    vitorias = 0
    for luta in range(args.lutas):
        vencedor, duracao = simular(piloto, semente=500 + luta, registros=registros)
        vitorias += vencedor == "A"
        print(f"demonstracao {luta + 1}: vencedor {vencedor} | t {duracao}s")
    print(f"Piloto {args.estilo}: {vitorias}/{args.lutas} vitorias | {len(registros)} amostras")

    dados = pd.DataFrame(registros, columns=COLUNAS + ["acao"])
    dados = dados.loc[dados["acao"] != "PARAR"]
    X_treino, X_teste, y_treino, y_teste = train_test_split(
        dados[COLUNAS], dados["acao"], test_size=0.25, random_state=42, stratify=dados["acao"])
    rival = Pipeline([
        ("escala", StandardScaler()),
        ("mlp", MLPClassifier(hidden_layer_sizes=(32, 16), max_iter=600, random_state=42)),
    ])
    rival.fit(X_treino, y_treino)
    acuracia = accuracy_score(y_teste, rival.predict(X_teste))
    print(f"Acuracia do rival: {acuracia:.2%}")
    print(classification_report(y_teste, rival.predict(X_teste), zero_division=0))

    joblib.dump(rival, args.saida)
    print("Rival salvo em", args.saida)

    def politica_rival(estado):
        return rival.predict(pd.DataFrame([features(estado)], columns=COLUNAS))[0]

    aferidas = [simular(politica_rival, semente=900 + i)[0] for i in range(4)]
    print("Aferindo o rival contra o bot interno:", aferidas)


if __name__ == "__main__":
    principal()
