# O dataset nao esta neste repositorio

As 138 imagens de PEDRA, PAPEL e TESOURA que treinaram a CNN ficaram de fora de
proposito: em boa parte dos quadros da classe PEDRA o rosto de uma pessoa aparece
nitido, dentro de casa, e este repositorio e publico.

O que ficou e tudo que sustenta o resultado:

| | |
|---|---|
| Notebook executado | `../entregas/aula05_extra_jokenpo_cnn.html` |
| Matriz de confusao e curva de perda | `../entregas/matriz_confusao_baseline.png`, `../entregas/curva_perda_baseline.png` |
| Modelo treinado | `../modelos/` |
| As 10 rodadas ao vivo | `../resultados/10_rodadas_normal.csv` |
| Teste adverso, antes e depois | `../resultados/adverso_antes.csv`, `../resultados/adverso_depois.csv` |
| Analise completa | `../RESULTADOS_ENTREGA6.md` |

Para reproduzir com imagens proprias, `../coletar_gestos.bat` refaz a coleta no
mesmo formato (recorte quadrado central, `jokenpo_dataset/<GESTO>/<gesto>_000.jpg`).
