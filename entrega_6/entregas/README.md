# Entrega 6 - Jokenpo com Deep Learning em Tempo Real

> Trabalho individual.

## Por onde comecar

Abra **`aula05_extra_jokenpo_cnn.html`** no navegador: notebook executado, com todas as saidas.
Depois leia **`RESULTADOS_ENTREGA6.md`**, que tem a analise completa.

## Resultado em uma tabela

| | |
|---|---|
| Dataset | 138 imagens (45 / 45 / 48) |
| Acuracia de teste da CNN | **88,57%** |
| 10 rodadas ao vivo | 83,3% |
| Teste adverso (luz fraca) | 60,0% |
| Melhoria (augmentation) | empatou no normal, **piorou** no adverso |

## Os itens pedidos na entrega

| Item | Onde esta |
|---|---|
| Dataset em PEDRA, PAPEL e TESOURA | `jokenpo_dataset/` |
| Notebook executado | `aula05_extra_jokenpo_cnn.html` |
| Curva de perda | `curva_perda_baseline.png` |
| Matriz de confusao | `matriz_confusao_baseline.png` |
| Registro das 10 rodadas | `10_rodadas_normal.csv` (12 rodadas) |
| Teste adverso antes e depois | `adverso_antes.csv`, `adverso_depois.csv` |
| Captura da webcam com a previsao | `webcam_previsao_normal.png`, `webcam_previsao_iluminacao_fraca.png` |
| Explicacao da melhoria | `RESULTADOS_ENTREGA6.md`, Etapa 5 |
| Ganho, efeito colateral e limitacao | `RESULTADOS_ENTREGA6.md`, secao propria |
| Hipotese escrita antes do teste | `HIPOTESE.md` |

## Tres coisas que valem a leitura

**1. Doze imagens foram descartadas na revisao.** Duas maos abertas salvas na pasta PEDRA e dez
quadros sem gesto em TESOURA (parede, ombro, rosto), capturados quando o modo rajada continuou
gravando durante a troca de gesto. Foram encontradas montando folhas de contato com todas as
imagens de cada classe. Os arquivos removidos ficaram guardados, com o motivo de cada descarte
registrado.

**2. O primeiro teste adverso foi invalidado, e esta preservado.** Ele deu 94,4% - melhor que o
teste normal. Medindo, descobri que a luz tinha caido so 11% e que 13 das 18 rodadas foram
registradas em menos de 1 segundo cada, contando o mesmo quadro varias vezes. Esta em
`adverso_antes_tentativa1_invalida.csv`. A ferramenta foi corrigida para exigir 2s entre rodadas e
mostrar a luminosidade ao vivo.

**3. A melhoria piorou, e o numero ao vivo enganava.** Nas rodadas, o augmentation parecia dar
90,9% contra 60,0% - mas a sessao teve mais luz (144,1 contra 121,8), entao nao era comparavel.
No teste controlado, escurecendo as mesmas imagens de teste por fator conhecido, o augmentation
perde em todos os niveis: a 50% de brilho, 65,7% contra 88,6% do baseline. O risco estava previsto
na hipotese registrada antes.

## Limitacao principal

O dataset saiu de uma pessoa, um comodo, uma sessao, uma iluminacao. Nenhum modelo treinado assim
aprende invariancia a luz, porque nunca viu variacao de luz. A correcao nao e augmentation - e
coletar com iluminacao variada.
