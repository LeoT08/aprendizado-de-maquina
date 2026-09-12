# -*- coding: utf-8 -*-
r"""Verifica se o ambiente da Aula 1 esta pronto: bibliotecas, camera e pipeline.

    .\.venv\Scripts\python.exe ferramentas\verificar_ambiente.py
"""
import importlib
import sys

BIBLIOTECAS = [
    ("numpy", "NumPy"), ("cv2", "OpenCV"), ("matplotlib", "matplotlib"),
    ("pandas", "pandas"), ("sklearn", "scikit-learn"), ("seaborn", "seaborn"),
    ("joblib", "joblib"), ("torch", "PyTorch"), ("torchvision", "torchvision"),
    ("serial", "pyserial"),
]

falhas = []

print(f"Python {sys.version.split()[0]}  ({sys.executable})\n")
print("Bibliotecas:")
for modulo, nome in BIBLIOTECAS:
    try:
        m = importlib.import_module(modulo)
        print(f"  [ok]    {nome:14s} {getattr(m, '__version__', '?')}")
    except Exception as e:
        print(f"  [FALHA] {nome:14s} {e}")
        falhas.append(nome)

if "OpenCV" not in falhas:
    import cv2
    import numpy as np

    print("\nCamera:")
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    ret, frame = False, None
    if cap.isOpened():
        for _ in range(10):
            ret, frame = cap.read()
            if ret:
                break
    cap.release()
    if ret:
        print(f"  [ok]    webcam respondendo - quadro {frame.shape[1]}x{frame.shape[0]}")
    else:
        print("  [FALHA] nao consegui ler um quadro da webcam")
        falhas.append("camera")

    print("\nPipeline de decisao (quadros sinteticos):")
    for x, esperado in [(100, "ESQUERDA"), (320, "CENTRO"), (540, "DIREITA")]:
        f = np.zeros((480, 640, 3), np.uint8)
        cv2.rectangle(f, (x - 40, 200), (x + 40, 280), (0, 255, 0), -1)
        hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
        m = cv2.inRange(hsv, np.array([35, 40, 40]), np.array([90, 255, 255]))
        cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        maior = max(cs, key=cv2.contourArea)
        M = cv2.moments(maior)
        cx = int(M["m10"] / M["m00"])
        obtido = ("ESQUERDA" if cx < 320 - 80 else "DIREITA" if cx > 320 + 80 else "CENTRO")
        ok = obtido == esperado
        print(f"  [{'ok' if ok else 'FALHA'}]{'    ' if ok else ' '}{esperado:9s} -> {obtido}")
        if not ok:
            falhas.append(f"pipeline/{esperado}")

print()
if falhas:
    print("AMBIENTE COM PROBLEMA:", ", ".join(falhas))
    sys.exit(1)
print("AMBIENTE OK")
