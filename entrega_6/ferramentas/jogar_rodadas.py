# -*- coding: utf-8 -*-
r"""Joga jokenpo contra a CNN e registra cada rodada num CSV.

Serve tanto para as 10 rodadas normais (Etapa 3) quanto para o teste adverso
(Etapa 4) - muda so o parametro --condicao.

Para cada rodada grava: gesto real, gesto previsto, confianca, acerto e condicao.

    ..\.venv\Scripts\python.exe ferramentas\jogar_rodadas.py --rodadas 10 --condicao normal
    ..\.venv\Scripts\python.exe ferramentas\jogar_rodadas.py --rodadas 10 --condicao iluminacao_fraca
    ..\.venv\Scripts\python.exe ferramentas\jogar_rodadas.py --modelo modelos/cnn_augmentation.pt --condicao iluminacao_fraca --saida adverso_depois

Como funciona: a previsao da CNN aparece ao vivo. Faca o gesto e pressione a tecla
do gesto que VOCE esta fazendo - e isso que define o "gesto real". O programa anota
o que a CNN respondeu naquele instante.

Teclas:
    1  registra rodada com gesto real = PEDRA
    2  registra rodada com gesto real = PAPEL
    3  registra rodada com gesto real = TESOURA
    S  salva uma captura de tela da previsao atual
    Q  encerra e grava o CSV
"""
import argparse
import csv
import datetime
import pathlib

import cv2
import numpy as np
import time
import torch
import torch.nn as nn

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CLASSES = ["PEDRA", "PAPEL", "TESOURA"]


class JokenpoCNN(nn.Module):
    """Mesma arquitetura da celula 10 do notebook."""

    def __init__(self, filters_1=16, filters_2=32):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, filters_1, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(filters_1, filters_2, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(), nn.Linear(filters_2 * 16 * 16, 64), nn.ReLU(), nn.Linear(64, 3))

    def forward(self, image):
        return self.classifier(self.features(image))


def carregar(caminho):
    dados = torch.load(caminho, map_location="cpu", weights_only=False)
    modelo = JokenpoCNN(*dados.get("filters", (16, 32)))
    modelo.load_state_dict(dados["state_dict"])
    modelo.eval()
    return modelo, dados.get("acuracia_teste")


def prever(modelo, roi):
    cinza = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    img = cv2.resize(cinza, (64, 64), interpolation=cv2.INTER_AREA)
    t = torch.tensor(img / 255.0, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
    with torch.no_grad():
        prob = torch.softmax(modelo(t), dim=1)[0].numpy()
    return CLASSES[int(prob.argmax())], float(prob.max()), prob


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--modelo", default="modelos/cnn_baseline.pt")
    p.add_argument("--rodadas", type=int, default=10)
    p.add_argument("--condicao", default="normal",
                   help="normal, iluminacao_fraca, fundo_diferente, mao_distante...")
    p.add_argument("--saida", default=None, help="nome do CSV (sem extensao)")
    p.add_argument("--camera", type=int, default=0)
    p.add_argument("--intervalo-minimo", type=float, default=2.0,
                   help="segundos minimos entre rodadas; evita contar o mesmo quadro varias vezes")
    p.add_argument("--luz-alvo", type=float, default=None,
                   help="luminosidade maxima da ROI aceita (para garantir a condicao adversa)")
    args = p.parse_args()

    caminho = RAIZ / args.modelo
    if not caminho.exists():
        raise SystemExit(f"Modelo nao encontrado: {caminho}\nTreine a CNN no notebook primeiro.")
    modelo, acc_treino = carregar(caminho)
    print(f"Modelo: {args.modelo}" + (f" (acuracia de teste {acc_treino:.2%})" if acc_treino else ""))
    print(f"Condicao: {args.condicao} | rodadas alvo: {args.rodadas}")
    print(__doc__)

    resultados = pathlib.Path(RAIZ / "resultados"); resultados.mkdir(exist_ok=True)
    entregas = pathlib.Path(RAIZ / "entregas"); entregas.mkdir(exist_ok=True)
    nome = args.saida or f"rodadas_{args.condicao}"

    camera = cv2.VideoCapture(args.camera, cv2.CAP_DSHOW)
    if not camera.isOpened():
        raise SystemExit("Camera nao encontrada.")

    linhas = []
    capturas = 0
    ultimo_registro = 0.0
    bloqueios = 0
    janela = f"Jokenpo CNN [{args.condicao}] - 1/2/3 registra | S captura | Q sai"

    while True:
        ok, frame = camera.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        lado = min(h, w) // 2
        esq, topo = (w - lado) // 2, (h - lado) // 2
        roi = frame[topo:topo + lado, esq:esq + lado]

        gesto, conf, prob = prever(modelo, roi)
        luz = float(cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY).mean())

        vis = frame.copy()
        cv2.rectangle(vis, (esq, topo), (esq + lado, topo + lado), (0, 255, 0), 2)
        cv2.putText(vis, f"{gesto}  {conf:.0%}", (esq, topo - 14),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        # barras de probabilidade
        for i, c in enumerate(CLASSES):
            larg = int(150 * prob[i])
            y = 30 + i * 26
            cv2.putText(vis, f"{c:8s}", (14, y + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (230, 230, 230), 1)
            cv2.rectangle(vis, (95, y), (95 + 150, y + 14), (90, 90, 90), 1)
            if larg:
                cv2.rectangle(vis, (95, y), (95 + larg, y + 14), (0, 200, 120), -1)
            cv2.putText(vis, f"{prob[i]:.0%}", (255, y + 11), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (230, 230, 230), 1)

        acertos = sum(1 for r in linhas if r["acertou"])
        cv2.putText(vis, f"rodada {len(linhas)}/{args.rodadas}   acertos {acertos}",
                    (14, h - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        espera = max(0.0, args.intervalo_minimo - (time.time() - ultimo_registro))
        cor_luz = (0, 210, 0) if (args.luz_alvo is None or luz <= args.luz_alvo) else (0, 140, 255)
        cv2.putText(vis, f"luz {luz:.0f}" + (f" / alvo <= {args.luz_alvo:.0f}" if args.luz_alvo else ""),
                    (w - 210, h - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.55, cor_luz, 2)
        if espera > 0:
            cv2.putText(vis, f"aguarde {espera:.1f}s", (w - 210, h - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 140, 255), 2)
        cv2.putText(vis, f"condicao: {args.condicao}   |  1/2/3 registra  S captura  Q sai",
                    (14, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (210, 210, 210), 1)

        cv2.imshow(janela, vis)
        tecla = cv2.waitKey(1) & 0xFF

        if tecla in (ord("q"), 27):
            break
        elif tecla == ord("s"):
            capturas += 1
            destino = entregas / f"webcam_previsao_{args.condicao}_{capturas}.png"
            cv2.imwrite(str(destino), vis)
            print(f"  captura salva: {destino.name}")
        elif tecla in (ord("1"), ord("2"), ord("3")):
            if time.time() - ultimo_registro < args.intervalo_minimo:
                bloqueios += 1
                print(f"  ignorado: espere {args.intervalo_minimo:.0f}s entre rodadas "
                      f"(rodadas coladas contam o mesmo quadro duas vezes)")
                continue
            ultimo_registro = time.time()
            real = CLASSES[tecla - ord("1")]
            acertou = real == gesto
            linhas.append({
                "rodada": len(linhas) + 1,
                "gesto_real": real,
                "gesto_previsto": gesto,
                "confianca": round(conf, 4),
                "acertou": acertou,
                "condicao": args.condicao,
                "luminosidade_roi": round(luz, 1),
                "prob_pedra": round(float(prob[0]), 4),
                "prob_papel": round(float(prob[1]), 4),
                "prob_tesoura": round(float(prob[2]), 4),
                "momento": datetime.datetime.now().strftime("%H:%M:%S"),
            })
            print(f"  rodada {len(linhas):2d}: real={real:8s} previsto={gesto:8s} "
                  f"conf={conf:5.1%}  {'ACERTOU' if acertou else 'ERROU'}")
            if len(linhas) == 1:                      # guarda a 1a como evidencia
                cv2.imwrite(str(entregas / f"webcam_previsao_{args.condicao}.png"), vis)

    camera.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1)

    if not linhas:
        print("\nNenhuma rodada registrada - nada foi gravado.")
        return

    destino = resultados / f"{nome}.csv"
    with open(destino, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        escritor.writeheader()
        escritor.writerows(linhas)

    acertos = sum(1 for r in linhas if r["acertou"])
    acc = acertos / len(linhas)
    conf_media = sum(r["confianca"] for r in linhas) / len(linhas)
    print(f"\n{'='*52}")
    print(f"condicao        : {args.condicao}")
    print(f"rodadas         : {len(linhas)}")
    print(f"acertos         : {acertos}  ({acc:.1%})")
    luz_media = sum(r["luminosidade_roi"] for r in linhas) / len(linhas)
    print(f"confianca media : {conf_media:.1%}")
    print(f"luminosidade    : {luz_media:.1f} (media da ROI nas rodadas)")
    if bloqueios:
        print(f"registros ignorados por virem rapido demais: {bloqueios}")
    print(f"CSV             : resultados/{destino.name}")
    if len(linhas) < args.rodadas:
        print(f"\nATENCAO: a entrega pede {args.rodadas} rodadas e voce registrou {len(linhas)}.")
    print("=" * 52)


if __name__ == "__main__":
    main()
