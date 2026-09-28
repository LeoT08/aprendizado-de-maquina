"""Arena de robos LCML - Aula 7.

Simulador com dois robos-cubo. O notebook do aluno conecta por TCP e comanda
um robo: le sensores (JSON), decide e envia acoes. Arquitetura cerebro-corpo:
a IA vive no notebook, o corpo vive na arena.

Modo SUMO (padrao): plataforma circular. Ande, encontre o adversario e
derrube-o da plataforma. Quem cai, perde a disputa.
Modo CORRIDA (opcional): circuito com checkpoints contra o relogio.

Uso:
    python arena_robos.py                     # sumo com janela
    python arena_robos.py --modo corrida      # corrida com janela
    python arena_robos.py --teste             # autoteste sem janela
    python arena_robos.py --teste --foto arena.png
"""

import argparse
import json
import math
import select
import socket
import time

LARGURA, ALTURA = 960, 640
BORDA = 20
FPS = 30
TAM_ROBO = 24
VEL_MAX = 170.0
ACEL = 150.0
GIRO = 150.0
ALCANCE_RAIO = 200.0
TIMEOUT_COMANDO = 0.6

# Sumo
CENTRO = (LARGURA / 2, ALTURA / 2)
RAIO_PLATAFORMA = 240.0
RAIO_MINIMO = 110.0
ENCOLHE_APOS = 15.0
ENCOLHE_TAXA = 4.0
OBSTACULOS_SUMO = [(420, 170, 120, 26), (420, 464, 120, 26)]
POS_SUMO_A = (CENTRO[0] - 130, CENTRO[1])
POS_SUMO_B = (CENTRO[0] + 130, CENTRO[1])
TEMPO_LIMITE_SUMO = 90.0

# Corrida
OBSTACULOS_CORRIDA = [
    (300, 220, 120, 180),
    (540, 220, 120, 180),
]
PERCURSO = [
    (770, 150), (820, 320), (770, 500), (480, 570),
    (190, 500), (140, 320), (190, 150), (480, 95),
]
POS_CORRIDA_A = (430, 95)
POS_CORRIDA_B = (530, 95)


def paredes(modo):
    parede = BORDA
    base = [
        (0, 0, LARGURA, parede),
        (0, ALTURA - parede, LARGURA, parede),
        (0, 0, parede, ALTURA),
        (LARGURA - parede, 0, parede, ALTURA),
    ]
    if modo == "sumo":
        return base + OBSTACULOS_SUMO
    return base + OBSTACULOS_CORRIDA


class Robo:
    def __init__(self, nome, pos, rot):
        self.nome = nome
        self.resetar(pos, rot)

    def resetar(self, pos, rot):
        self.x, self.y = pos
        self.rot = rot
        self.vel = 0.0
        self.empuxo_x = 0.0
        self.empuxo_y = 0.0
        self.acao = "PARAR"
        self.ultimo_comando = 0.0
        self.cp = 0
        self.voltas = 0
        self.melhor = None
        self.ultimo = None
        self.inicio_volta = None
        self.caiu = False


class Arena:
    def __init__(self, modo="sumo", voltas=2, teste=False):
        self.modo = modo
        self.paredes = paredes(modo)
        self.voltas_alvo = voltas
        self.tempo = 0.0
        self.fase = "CONTAGEM" if not teste else "CORRIDA"
        self.contagem = 3.0 if not teste else 0.0
        self.vencedor = None
        self.caiu = None
        self.contato = None
        if modo == "sumo":
            self.a = Robo("A", POS_SUMO_A, 0.0)
            self.b = Robo("B", POS_SUMO_B, 180.0)
        else:
            self.a = Robo("A", POS_CORRIDA_A, 0.0)
            self.b = Robo("B", POS_CORRIDA_B, 0.0)

    def resetar(self):
        if self.modo == "sumo":
            self.a.resetar(POS_SUMO_A, 0.0)
            self.b.resetar(POS_SUMO_B, 180.0)
        else:
            self.a.resetar(POS_CORRIDA_A, 0.0)
            self.b.resetar(POS_CORRIDA_B, 0.0)
        self.tempo = 0.0
        self.fase = "CONTAGEM"
        self.contagem = 3.0
        self.vencedor = None
        self.caiu = None
        self.contato = None

    # ---------- sensores ----------

    def raio_atual(self):
        """A plataforma encolhe com o tempo: ninguem pode esperar para sempre."""
        return max(RAIO_MINIMO, RAIO_PLATAFORMA - max(0.0, self.tempo - ENCOLHE_APOS) * ENCOLHE_TAXA)

    def lancar_raio(self, x, y, ang):
        passo = 8.0
        dx, dy = math.cos(ang) * passo, math.sin(ang) * passo
        px, py = x, y
        dist = 0.0
        while dist < ALCANCE_RAIO:
            px += dx
            py += dy
            dist += passo
            for r in self.paredes:
                if r[0] <= px <= r[0] + r[2] and r[1] <= py <= r[1] + r[3]:
                    return dist / ALCANCE_RAIO
            if self.modo == "sumo":
                if math.hypot(px - CENTRO[0], py - CENTRO[1]) > self.raio_atual():
                    return dist / ALCANCE_RAIO
        return 1.0

    def sensores(self, robo):
        return [self.lancar_raio(robo.x, robo.y, math.radians(robo.rot + delta))
                for delta in (0, -45, 45, -90, 90)]

    def estado(self, robo, inimigo):
        base = {
            "robo": robo.nome,
            "modo": self.modo,
            "fase": self.fase,
            "t": round(self.tempo, 2),
            "x": round(robo.x, 1),
            "y": round(robo.y, 1),
            "rot": round(robo.rot, 1),
            "vel": round(robo.vel / VEL_MAX, 3),
            "raios": [round(r, 3) for r in self.sensores(robo)],
            "vencedor": self.vencedor,
            "caiu": self.caiu,
        }
        if self.modo == "sumo":
            distancia = math.hypot(inimigo.x - robo.x, inimigo.y - robo.y)
            angulo = math.degrees(math.atan2(inimigo.y - robo.y, inimigo.x - robo.x))
            direcao = (angulo - robo.rot + 540) % 360 - 180
            base.update({
                "inimigo_bearing": round(direcao, 1),
                "inimigo_dist": round(min(distancia / (2 * RAIO_PLATAFORMA), 1.0), 3),
                "dist_centro": round(min(math.hypot(robo.x - CENTRO[0], robo.y - CENTRO[1]) / self.raio_atual(), 1.2), 3),
                "raio_plataforma": round(self.raio_atual(), 1),
            })
        else:
            alvo = PERCURSO[robo.cp]
            dist = math.hypot(alvo[0] - robo.x, alvo[1] - robo.y)
            angulo_alvo = math.degrees(math.atan2(alvo[1] - robo.y, alvo[0] - robo.x))
            direcao = (angulo_alvo - robo.rot + 540) % 360 - 180
            base.update({
                "checkpoint": robo.cp,
                "dist_checkpoint": round(min(dist / 600.0, 1.0), 3),
                "direcao_checkpoint": round(direcao, 1),
                "voltas": robo.voltas,
                "alvo_voltas": self.voltas_alvo,
                "melhor_volta": robo.melhor,
                "ultima_volta": robo.ultimo,
            })
        return base

    # ---------- decisao do bot interno ----------

    def decidir_bot(self, robo, inimigo):
        if self.modo == "corrida":
            alvo = PERCURSO[robo.cp]
            angulo_alvo = math.degrees(math.atan2(alvo[1] - robo.y, alvo[0] - robo.x))
            direcao = (angulo_alvo - robo.rot + 540) % 360 - 180
            if direcao < -10:
                return "ESQUERDA"
            if direcao > 10:
                return "DIREITA"
            return "FRENTE"

        # Bot de sumo: caça o inimigo, mas hesita perto da borda.
        # A hesitação é defasada por robô: nunca param ao mesmo tempo.
        hesitacao = (self.tempo + (3.0 if robo.nome == "A" else 0.0)) % 4.0 < 0.5
        dist_centro = math.hypot(robo.x - CENTRO[0], robo.y - CENTRO[1]) / self.raio_atual()
        if dist_centro > 0.85:
            angulo_centro = math.degrees(math.atan2(CENTRO[1] - robo.y, CENTRO[0] - robo.x))
            direcao = (angulo_centro - robo.rot + 540) % 360 - 180
            if direcao < -10:
                return "ESQUERDA"
            if direcao > 10:
                return "DIREITA"
            return "FRENTE"
        if hesitacao:
            return "PARAR"
        direcao_inimigo = (math.degrees(math.atan2(inimigo.y - robo.y, inimigo.x - robo.x)) - robo.rot + 540) % 360 - 180
        if abs(direcao_inimigo) <= 14:
            return "FRENTE"
        return "ESQUERDA" if direcao_inimigo < 0 else "DIREITA"

    # ---------- fisica ----------

    def aplicar(self, robo, acao, dt):
        if self.fase != "CORRIDA":
            robo.vel = 0.0
            return
        if acao == "FRENTE":
            robo.vel = min(robo.vel + ACEL * dt, VEL_MAX)
        elif acao == "FREIO":
            robo.vel = max(robo.vel - ACEL * 1.5 * dt, 0.0)
        elif acao in ("ESQUERDA", "DIREITA"):
            sinal = 1 if acao == "DIREITA" else -1
            robo.rot = (robo.rot + sinal * GIRO * dt) % 360
            robo.vel = max(robo.vel - ACEL * 0.4 * dt, 0.0)
        else:
            robo.vel = max(robo.vel - ACEL * 0.8 * dt, 0.0)

    def mover(self, robo, dt):
        dx = math.cos(math.radians(robo.rot)) * robo.vel * dt + robo.empuxo_x * dt
        dy = math.sin(math.radians(robo.rot)) * robo.vel * dt + robo.empuxo_y * dt
        robo.empuxo_x *= 0.88
        robo.empuxo_y *= 0.88
        robo.x = min(max(robo.x + dx, BORDA + TAM_ROBO / 2), LARGURA - BORDA - TAM_ROBO / 2)
        robo.y = min(max(robo.y + dy, BORDA + TAM_ROBO / 2), ALTURA - BORDA - TAM_ROBO / 2)

        if self.modo == "sumo":
            caixa = (robo.x - TAM_ROBO / 2, robo.y - TAM_ROBO / 2, TAM_ROBO, TAM_ROBO)
            for r in OBSTACULOS_SUMO:
                if not (caixa[0] + caixa[2] < r[0] or caixa[0] > r[0] + r[2] or
                        caixa[1] + caixa[3] < r[1] or caixa[1] > r[1] + r[3]):
                    robo.vel = 0.0
                    robo.x -= dx
                    robo.y -= dy
                    break
            if math.hypot(robo.x - CENTRO[0], robo.y - CENTRO[1]) > self.raio_atual() - 4:
                robo.caiu = True
            return

        caixa = (robo.x - TAM_ROBO / 2, robo.y - TAM_ROBO / 2, TAM_ROBO, TAM_ROBO)
        for r in self.paredes:
            if not (caixa[0] + caixa[2] < r[0] or caixa[0] > r[0] + r[2] or
                    caixa[1] + caixa[3] < r[1] or caixa[1] > r[1] + r[3]):
                robo.vel = 0.0
                return
        robo.x, robo.y = min(max(robo.x, BORDA + TAM_ROBO / 2), LARGURA - BORDA - TAM_ROBO / 2), \
            min(max(robo.y, BORDA + TAM_ROBO / 2), ALTURA - BORDA - TAM_ROBO / 2)
        alvo = PERCURSO[robo.cp]
        if math.hypot(alvo[0] - robo.x, alvo[1] - robo.y) < 46.0:
            robo.cp += 1
            if robo.cp >= len(PERCURSO):
                robo.cp = 0
                robo.voltas += 1
                if robo.inicio_volta is not None:
                    robo.ultimo = round(self.tempo - robo.inicio_volta, 2)
                    if robo.melhor is None or robo.ultimo < robo.melhor:
                        robo.melhor = robo.ultimo
                robo.inicio_volta = self.tempo
                if robo.voltas >= self.voltas_alvo and self.vencedor is None:
                    self.vencedor = robo.nome
                    self.fase = "FIM"

    def interacoes(self):
        dx = self.b.x - self.a.x
        dy = self.b.y - self.a.y
        d = math.hypot(dx, dy)
        if d == 0:
            return
        if d > TAM_ROBO * 1.25:
            self.contato = None
            return
        nx, ny = dx / d, dy / d
        if d < TAM_ROBO * 0.92:
            # Aproxima somente ate o ponto de contato estavel (colam-se).
            recuo = (TAM_ROBO * 0.92 - d) / 2
            self.a.x -= nx * recuo
            self.a.y -= ny * recuo
            self.b.x += nx * recuo
            self.b.y += ny * recuo
        if self.modo != "sumo" or self.fase != "CORRIDA":
            return
        # Forca de cada robo na direcao do inimigo (so conta quem aponta para ele).
        forca_a = self.a.vel * max(0.0, math.cos(math.radians(self.angulo_para(self.a, self.b))))
        forca_b = self.b.vel * max(0.0, math.cos(math.radians(self.angulo_para(self.b, self.a))))
        # Empurrador com histerese: troca somente se o outro supera com folga.
        if self.contato is None:
            self.contato = {"pusher": "A" if forca_a >= forca_b else "B"}
        elif self.contato["pusher"] == "A" and forca_b > forca_a + 30:
            self.contato["pusher"] = "B"
        elif self.contato["pusher"] == "B" and forca_a > forca_b + 30:
            self.contato["pusher"] = "A"
        empurrador = self.a if self.contato["pusher"] == "A" else self.b
        empurrado = self.b if self.contato["pusher"] == "A" else self.a
        sinal = 1 if self.contato["pusher"] == "A" else -1
        empurrado.vel *= 0.97  # preso no empurrao: perde aderencia aos poucos
        forca_empurrador = forca_a if self.contato["pusher"] == "A" else forca_b
        forca = 700.0 * (forca_empurrador / VEL_MAX) + 160.0
        empurrado.empuxo_x += sinal * nx * forca * 0.033
        empurrado.empuxo_y += sinal * ny * forca * 0.033

    @staticmethod
    def angulo_para(de, para):
        return (math.degrees(math.atan2(para.y - de.y, para.x - de.x)) - de.rot + 540) % 360 - 180

    def verificar_fim_sumo(self):
        if self.a.caiu and self.b.caiu:
            self.vencedor = None
            self.caiu = "AMBOS"
        elif self.a.caiu:
            self.vencedor = "B"
            self.caiu = "A"
        elif self.b.caiu:
            self.vencedor = "A"
            self.caiu = "B"
        elif self.tempo > TEMPO_LIMITE_SUMO:
            self.vencedor = None
            self.caiu = None
        if self.a.caiu or self.b.caiu or self.tempo > TEMPO_LIMITE_SUMO:
            self.fase = "FIM"

    def passo(self, dt, acao_bot_a=None, acao_bot_b=None):
        self.tempo += dt
        if self.fase == "CONTAGEM":
            self.contagem -= dt
            if self.contagem <= 0:
                self.fase = "CORRIDA"
                self.a.inicio_volta = 0.0
                self.b.inicio_volta = 0.0
            return
        agora = time.time()
        for robo, acao_bot in ((self.a, acao_bot_a), (self.b, acao_bot_b)):
            acao = robo.acao
            if robo.nome == "A" and acao_bot_a is not None:
                acao = acao_bot
            if robo.nome == "B" and acao_bot_b is not None:
                acao = acao_bot
            if agora - robo.ultimo_comando > TIMEOUT_COMANDO and acao_bot is None:
                acao = "PARAR"
            self.aplicar(robo, acao, dt)
        self.mover(self.a, dt)
        self.mover(self.b, dt)
        if self.modo == "sumo":
            self.interacoes()
            self.verificar_fim_sumo()


class Servidor:
    def __init__(self, arena, porta):
        self.arena = arena
        self.clientes = {}
        self.ouvinte = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ouvinte.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.ouvinte.bind(("127.0.0.1", porta))
        self.ouvinte.listen(2)
        self.ouvinte.setblocking(False)
        print(f"Arena aguardando o notebook em 127.0.0.1:{porta}")

    def aceitar(self):
        prontos, _, _ = select.select([self.ouvinte], [], [], 0)
        if not prontos:
            return
        conn, endereco = self.ouvinte.accept()
        conn.setblocking(False)
        self.clientes[conn] = {"buffer": ""}
        print(f"Conectado: {endereco}")

    def receber(self):
        for conn in list(self.clientes):
            try:
                dados = conn.recv(4096)
            except BlockingIOError:
                continue
            except ConnectionResetError:
                conn.close()
                self.clientes.pop(conn, None)
                continue
            if not dados:
                conn.close()
                self.clientes.pop(conn, None)
                continue
            self.clientes[conn]["buffer"] += dados.decode("utf-8")
            while "\n" in self.clientes[conn]["buffer"]:
                linha, self.clientes[conn]["buffer"] = self.clientes[conn]["buffer"].split("\n", 1)
                self.tratar(conn, linha)

    def tratar(self, conn, linha):
        try:
            msg = json.loads(linha)
        except json.JSONDecodeError:
            return
        if "cmd" in msg and msg["cmd"] == "RESET":
            self.arena.resetar()
        robo = self.arena.a if msg.get("robot", "A") == "A" else self.arena.b
        inimigo = self.arena.b if robo.nome == "A" else self.arena.a
        if "acao" in msg:
            robo.acao = msg["acao"]
            robo.ultimo_comando = time.time()
        try:
            conn.sendall((json.dumps(self.arena.estado(robo, inimigo)) + "\n").encode("utf-8"))
        except OSError:
            pass

    def fechar(self):
        self.ouvinte.close()
        for conn in self.clientes:
            conn.close()


def desenhar(tela, arena, pygame):
    tela.fill((16, 18, 24))
    fonte = pygame.font.Font(None, 26)
    if arena.modo == "sumo":
        raio = int(arena.raio_atual())
        pygame.draw.circle(tela, (58, 64, 74), (int(CENTRO[0]), int(CENTRO[1])), raio + 10)
        pygame.draw.circle(tela, (198, 196, 188), (int(CENTRO[0]), int(CENTRO[1])), raio)
        pygame.draw.circle(tela, (120, 118, 112), (int(CENTRO[0]), int(CENTRO[1])), raio, 4)
        for r in OBSTACULOS_SUMO:
            pygame.draw.rect(tela, (90, 105, 115), r)
        for robo, cor in ((arena.a, (70, 130, 230)), (arena.b, (220, 90, 80))):
            if robo.caiu:
                continue
            pygame.draw.rect(tela, cor, (robo.x - TAM_ROBO / 2, robo.y - TAM_ROBO / 2, TAM_ROBO, TAM_ROBO))
            pygame.draw.line(tela, (255, 255, 255), (robo.x, robo.y),
                             (robo.x + 18 * math.cos(math.radians(robo.rot)),
                              robo.y + 18 * math.sin(math.radians(robo.rot))), 3)
            tela.blit(fonte.render(robo.nome, True, (255, 255, 255)), (robo.x - 8, robo.y - TAM_ROBO / 2 - 24))
        painel = f"A {arena.a.nome}: vitorias na sessao | {arena.fase} | t {arena.tempo:.1f}s"
        texto = f"SUMO | {arena.fase} | t {arena.tempo:.1f}s"
        if arena.caiu:
            texto += f" | caiu: {arena.caiu}"
    else:
        for i, r in enumerate(arena.paredes):
            cor = (200, 200, 200) if i < 4 else (90, 105, 115)
            pygame.draw.rect(tela, cor, r)
        for i, ponto in enumerate(PERCURSO):
            pygame.draw.circle(tela, (60, 130, 120), ponto, 6)
            tela.blit(fonte.render(str(i + 1), True, (140, 200, 190)), (ponto[0] + 8, ponto[1] - 20))
        pygame.draw.circle(tela, (230, 200, 60), PERCURSO[-1], 46, 3)
        for robo, cor in ((arena.a, (70, 130, 230)), (arena.b, (220, 90, 80))):
            pygame.draw.rect(tela, cor, (robo.x - TAM_ROBO / 2, robo.y - TAM_ROBO / 2, TAM_ROBO, TAM_ROBO))
            pygame.draw.line(tela, (255, 255, 255), (robo.x, robo.y),
                             (robo.x + 18 * math.cos(math.radians(robo.rot)),
                              robo.y + 18 * math.sin(math.radians(robo.rot))), 3)
            tela.blit(fonte.render(robo.nome, True, (255, 255, 255)), (robo.x - 8, robo.y - TAM_ROBO / 2 - 24))
        texto = f"A: {arena.a.voltas}/{arena.voltas_alvo} voltas | B: {arena.b.voltas}/{arena.voltas_alvo} | {arena.fase}"
    tela.blit(fonte.render(texto, True, (240, 240, 240)), (24, ALTURA - 34))
    if arena.fase == "CONTAGEM":
        grande = pygame.font.Font(None, 120)
        tela.blit(grande.render(str(max(1, int(arena.contagem) + 1)), True, (240, 220, 90)), (LARGURA / 2 - 30, ALTURA / 2 - 60))


def principal():
    parser = argparse.ArgumentParser()
    parser.add_argument("--modo", choices=["sumo", "corrida"], default="sumo")
    parser.add_argument("--porta", type=int, default=5555)
    parser.add_argument("--voltas", type=int, default=2)
    parser.add_argument("--teste", action="store_true")
    parser.add_argument("--sem-janela", action="store_true")
    parser.add_argument("--bot-a", action="store_true")
    parser.add_argument("--foto", default=None)
    parser.add_argument("--segundos", type=float, default=None)
    args = parser.parse_args()

    if args.teste or args.sem_janela:
        import os
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

    import pygame

    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("LCML - Arena de Robos (Aula 7)")
    relogio = pygame.time.Clock()

    arena = Arena(modo=args.modo, voltas=args.voltas, teste=args.teste)
    servidor = Servidor(arena, args.porta)
    rodando = True
    inicio = time.time()

    while rodando:
        dt = 1.0 / FPS
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

        acao_bot_a = arena.decidir_bot(arena.a, arena.b) if (args.teste or args.bot_a) else None
        acao_bot_b = arena.decidir_bot(arena.b, arena.a) if arena.fase == "CORRIDA" else None
        servidor.aceitar()
        servidor.receber()
        arena.passo(dt, acao_bot_a=acao_bot_a, acao_bot_b=acao_bot_b)

        desenhar(tela, arena, pygame)
        pygame.display.flip()

        if args.foto and time.time() - inicio > (args.segundos or 10) * 0.5:
            pygame.image.save(tela, args.foto)
            args.foto = None
        if args.segundos is not None and time.time() - inicio > args.segundos:
            rodando = False
        if args.teste and arena.fase == "FIM" and time.time() - inicio > 6:
            rodando = False
        if args.teste and time.time() - inicio > 55:
            rodando = False

        relogio.tick(FPS)

    if args.teste:
        if arena.modo == "sumo":
            engajou = arena.fase == "FIM" or arena.caiu is not None
            print("ARENA_TESTE_OK" if engajou else "ARENA_TESTE_FALHOU")
        else:
            avancou = arena.a.cp != 0 or arena.b.cp != 0 or arena.vencedor is not None
            print("ARENA_TESTE_OK" if avancou else "ARENA_TESTE_FALHOU")
    servidor.fechar()
    pygame.quit()


if __name__ == "__main__":
    principal()
