"""Lancador da arena da Aula 7 com o robo B liberado para clientes.

Por que este arquivo existe
---------------------------
A arena do professor NAO permite disputar a Copa. Em `arena_robos.py`, a funcao
`principal()` calcula, em todo quadro:

    acao_bot_b = arena.decidir_bot(arena.b, arena.a) if arena.fase == "CORRIDA" else None

e `Arena.passo()` da prioridade a esse valor sobre o `robo.acao` que chegou pela
rede. Resultado: o robo B e SEMPRE o bot interno e ignora qualquer cliente
conectado nele - a celula 7 do notebook (Copa) roda sem efeito nenhum, com o
lutador rival carregado e sem comandar coisa alguma.

Aqui o bot interno de B vira reserva: ele so assume quando nenhum cliente
esta comandando B, usando o mesmo TIMEOUT_COMANDO que a arena ja aplica.
Uma regra so, e ela atende as duas situacoes da aula sem trocar de modo:

- torneio contra o bot: ninguem conecta em B, o bot interno pilota (igual ao original);
- Copa: o cliente do rival comanda B e o bot sai de cena.

Nada do material original e alterado: `Arena`, `Servidor` e `desenhar` sao
importados de `arena_robos`.

Uso:
    python ferramentas/arena_lcml.py                  # janela
    python ferramentas/arena_lcml.py --sem-janela     # sem janela (automacao)
    python ferramentas/arena_lcml.py --foto luta.png  # salva o primeiro choque
"""

import argparse
import math
import os
import sys
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "arena"))

import arena_robos as ar  # noqa: E402


def principal():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--modo", choices=["sumo", "corrida"], default="sumo")
    parser.add_argument("--porta", type=int, default=5555)
    parser.add_argument("--sem-janela", action="store_true")
    parser.add_argument("--foto", default=None, help="salva um PNG no primeiro choque entre os robos")
    parser.add_argument("--segundos", type=float, default=None, help="encerra a arena depois de N segundos")
    args = parser.parse_args()

    if args.sem_janela:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

    import pygame

    pygame.init()
    tela = pygame.display.set_mode((ar.LARGURA, ar.ALTURA))
    pygame.display.set_caption("LCML - Arena de Robos (Aula 7) - B liberado para clientes")
    relogio = pygame.time.Clock()

    arena = ar.Arena(modo=args.modo)
    servidor = ar.Servidor(arena, args.porta)
    rodando = True
    inicio = time.time()

    while rodando:
        dt = 1.0 / ar.FPS
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                rodando = False

        teclas = pygame.key.get_pressed()
        acao_teclado = None
        if teclas[pygame.K_LEFT]:
            acao_teclado = "ESQUERDA"
        elif teclas[pygame.K_RIGHT]:
            acao_teclado = "DIREITA"
        elif teclas[pygame.K_UP]:
            acao_teclado = "FRENTE"
        elif teclas[pygame.K_DOWN]:
            acao_teclado = "FREIO"
        if acao_teclado and arena.fase == "CORRIDA":
            arena.a.acao = acao_teclado
            arena.a.ultimo_comando = time.time()

        servidor.aceitar()
        servidor.receber()

        # A unica diferenca para o arena_robos.py original: o bot interno de B e reserva.
        b_tem_piloto = time.time() - arena.b.ultimo_comando < ar.TIMEOUT_COMANDO
        acao_bot_b = None
        if arena.fase == "CORRIDA" and not b_tem_piloto:
            acao_bot_b = arena.decidir_bot(arena.b, arena.a)

        arena.passo(dt, acao_bot_a=None, acao_bot_b=acao_bot_b)

        ar.desenhar(tela, arena, pygame)
        pygame.display.flip()

        if args.foto and arena.fase == "CORRIDA":
            distancia = math.hypot(arena.b.x - arena.a.x, arena.b.y - arena.a.y)
            if distancia < ar.TAM_ROBO * 2.2:
                pygame.image.save(tela, args.foto)
                print(f"Foto do choque salva em {args.foto}", flush=True)
                args.foto = None

        if args.segundos is not None and time.time() - inicio > args.segundos:
            rodando = False

        relogio.tick(ar.FPS)

    servidor.fechar()
    pygame.quit()


if __name__ == "__main__":
    principal()
