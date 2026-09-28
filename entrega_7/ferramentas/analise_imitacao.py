"""Onde a rede discorda do piloto que ela copiou - e para que lado ela erra.

A acuracia de imitacao (93%) diz quanto a rede acerta, mas nao diz se os 7% de
erro sao ruido ou viés. Esta analise responde isso comparando, **nos mesmos
estados gravados**, a acao do piloto com a acao que a rede escolheria.

O numero que importa nao e a taxa de erro: e o destino dos erros. Se as
discordancias apontarem todas para a mesma acao, a rede nao e uma copia com
ruido - e uma copia enviesada, e o viés se acumula quando ela fecha o laco com o
mundo (cada acao errada muda o estado seguinte).

Gera `entregas/vies_imitacao.csv`.

Uso:
    python ferramentas/analise_imitacao.py
"""

import os
import sys

import joblib
import numpy as np
import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLUNAS = [f"raio{i}" for i in range(5)] + ["vel", "bearing", "dist_inimigo", "dist_centro"]


def classificar_zonas(dados):
    """Mesma regra da celula 6 do notebook."""
    return np.select(
        [dados["dist_centro"] > 0.7, dados["dist_inimigo"] < 0.15],
        ["risco_borda", "combate"],
        default="manobra",
    )


def principal():
    dados = pd.read_csv(os.path.join(RAIZ, "teleop_sumo.csv"))
    modelo = joblib.load(os.path.join(RAIZ, "lutador_equipe.joblib"))
    dados["prev"] = modelo.predict(dados[COLUNAS])
    dados["zona"] = classificar_zonas(dados)

    linhas = []
    for zona, grupo in dados.groupby("zona"):
        piloto = (grupo["acao"] == "FRENTE").mean()
        rede = (grupo["prev"] == "FRENTE").mean()
        discordancias = grupo["acao"] != grupo["prev"]
        linhas.append({
            "zona": zona,
            "amostras": len(grupo),
            "frente_piloto": round(float(piloto), 4),
            "frente_rede": round(float(rede), 4),
            "delta_frente": round(float(rede - piloto), 4),
            "discordancias": int(discordancias.sum()),
            "discordancias_pct": round(float(discordancias.mean()), 4),
            "discordancias_viram_frente": int((grupo.loc[discordancias, "prev"] == "FRENTE").sum()),
        })
    piloto = (dados["acao"] == "FRENTE").mean()
    rede = (dados["prev"] == "FRENTE").mean()
    discordancias = dados["acao"] != dados["prev"]
    linhas.append({
        "zona": "TOTAL",
        "amostras": len(dados),
        "frente_piloto": round(float(piloto), 4),
        "frente_rede": round(float(rede), 4),
        "delta_frente": round(float(rede - piloto), 4),
        "discordancias": int(discordancias.sum()),
        "discordancias_pct": round(float(discordancias.mean()), 4),
        "discordancias_viram_frente": int((dados.loc[discordancias, "prev"] == "FRENTE").sum()),
    })

    tabela = pd.DataFrame(linhas)
    saida = os.path.join(RAIZ, "entregas", "vies_imitacao.csv")
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    tabela.to_csv(saida, index=False)

    pd.set_option("display.width", 140)
    print(tabela.to_string(index=False))
    erradas = dados.loc[discordancias]
    print("\nO piloto queria:", erradas["acao"].value_counts().to_dict())
    print("A rede escolheu:", erradas["prev"].value_counts().to_dict())
    virou_frente = (erradas["prev"] == "FRENTE").mean()
    print(f"\n{virou_frente:.0%} das discordancias viraram FRENTE: "
          f"o erro da imitacao nao e ruido, e agressividade.")
    print("Salvo em", saida)


if __name__ == "__main__":
    principal()
