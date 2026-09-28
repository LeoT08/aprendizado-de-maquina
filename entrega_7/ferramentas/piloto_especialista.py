"""Pilotos por regras para o sumo da Aula 7.

Estes pilotos existem para gerar as demonstracoes que a rede imita na etapa 3 e
para servir de adversario na Copa. Regra de projeto que vale a nota: eles
decidem usando **apenas as 9 features que a MLP tambem enxerga**

    raios[5] + vel + inimigo_bearing + inimigo_dist + dist_centro

Se o piloto usasse informacao que a rede nao recebe (a posicao absoluta x, y,
por exemplo), a imitacao teria um teto baixo: a rede veria estados identicos com
acoes diferentes e nunca passaria dos 85% exigidos.

Detalhe importante: a direcao do centro da plataforma NAO esta nas features. O
que existe e `dist_centro` (um escalar) e os cinco raios, medidos a 0, -45, +45,
-90 e +90 graus do nariz do robo. Entao a fuga da borda e inferida dos raios:
raio curto = beirada perto naquela direcao, logo o lado mais aberto aponta para
dentro da plataforma.
"""

import random

ACOES = ("FRENTE", "ESQUERDA", "DIREITA", "FREIO")


def _lado_mais_aberto(raios):
    """Para qual lado girar para voltar ao centro, lendo so os raios."""
    _, esq45, dir45, esq90, dir90 = raios
    return "ESQUERDA" if (esq45 + esq90) > (dir45 + dir90) else "DIREITA"


def piloto_agressivo(estado, borda=0.78, raio_curto=0.30, mira=12.0):
    """Cacador: so recua quando a queda e iminente, senao mira e empurra.

    Ordem de prioridade: nao cair > apontar para o inimigo > acelerar.
    """
    raios = estado["raios"]
    if estado["dist_centro"] > borda and raios[0] < raio_curto:
        return _lado_mais_aberto(raios)
    bearing = estado["inimigo_bearing"]
    if abs(bearing) > mira:
        return "ESQUERDA" if bearing < 0 else "DIREITA"
    return "FRENTE"


def piloto_cauteloso(estado, borda=0.70, raio_curto=0.30, mira=8.0, perto=0.20):
    """Estilo oposto: abandona a borda cedo, exige mira fina e freia na chegada.

    Usado para treinar o lutador rival da Copa - dois estilos diferentes fazem a
    Copa ser uma disputa de verdade, e nao um espelho do mesmo comportamento.
    """
    raios = estado["raios"]
    if estado["dist_centro"] > borda:
        if raios[0] < raio_curto:
            return _lado_mais_aberto(raios)
        return "FRENTE"
    bearing = estado["inimigo_bearing"]
    if abs(bearing) > mira:
        return "ESQUERDA" if bearing < 0 else "DIREITA"
    if estado["inimigo_dist"] > perto and estado["vel"] > 0.75:
        return "FREIO"
    return "FRENTE"


PILOTOS = {"agressivo": piloto_agressivo, "cauteloso": piloto_cauteloso}


class PilotoRuidoso:
    """Envolve um piloto e troca a acao por uma aleatoria com probabilidade p.

    Sem esse ruido o simulador e deterministico: toda luta a partir da mesma
    largada sai identica, o CSV vira a mesma trajetoria repetida e a rede
    aprende um corredor unico em vez de uma politica. O ruido tambem gera os
    poucos exemplos de FREIO e de recuperacao de posicao ruim.
    """

    def __init__(self, politica="agressivo", ruido=0.05, semente=None):
        self.politica = PILOTOS[politica] if isinstance(politica, str) else politica
        self.ruido = ruido
        self.rng = random.Random(semente)

    def __call__(self, estado):
        acao = self.politica(estado)
        if self.ruido and self.rng.random() < self.ruido:
            return self.rng.choice(ACOES)
        return acao
