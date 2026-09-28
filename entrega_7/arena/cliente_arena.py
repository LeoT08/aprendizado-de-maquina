"""Cliente Python da Arena de Corrida - Aula 7.

O notebook usa esta biblioteca para ler sensores e comandar o robo:

    from cliente_arena import ClienteArena

    cliente = ClienteArena(robot="A")
    cliente.conectar()
    estado = cliente.enviar("FRENTE")
    print(estado["raios"])
    cliente.fechar()
"""

import json
import socket


class ClienteArena:
    def __init__(self, host="127.0.0.1", porta=5555, robot="A", timeout=3.0):
        self.host = host
        self.porta = porta
        self.robot = robot
        self.timeout = timeout
        self.sock = None
        self.arquivo = None
        self.ultimo_estado = None

    def conectar(self):
        self.sock = socket.create_connection((self.host, self.porta), timeout=self.timeout)
        self.arquivo = self.sock.makefile("r", encoding="utf-8")
        return self.enviar(cmd="PING")

    def enviar(self, acao=None, cmd=None):
        if self.sock is None:
            raise ConnectionError("Conecte primeiro: cliente.conectar()")
        msg = {"robot": self.robot}
        if acao is not None:
            msg["acao"] = acao
        if cmd is not None:
            msg["cmd"] = cmd
        self.sock.sendall((json.dumps(msg) + "\n").encode("utf-8"))
        return self.receber()

    def receber(self):
        linha = self.arquivo.readline()
        if not linha:
            raise ConnectionError("A arena fechou a conexao.")
        self.ultimo_estado = json.loads(linha)
        return self.ultimo_estado

    def fechar(self):
        if self.sock is not None:
            self.sock.close()
            self.sock = None
            self.arquivo = None
