# Entrega 6 - Jokenpo com Deep Learning em Tempo Real

> Trabalho individual.

## Resumo

| | |
|---|---|
| Dataset | 138 imagens (PEDRA 45, PAPEL 45, TESOURA 48) |
| CNN | 2 blocos conv (16 e 32 filtros), 529.347 parametros, 12 epocas |
| Acuracia de teste | **88,57%** |
| 10 rodadas ao vivo | 83,3% (10 acertos em 12 rodadas) |
| Melhoria testada | augmentation (deslocamento + variacao de brilho) |
| Resultado da melhoria | **piorou a robustez**; empatou em condicao normal |

---

## Etapa 1 - Dataset

Coletado com `ferramentas/coletar_gestos.py`, que mantem o formato do notebook do professor
(recorte quadrado central, imagem espelhada, `jokenpo_dataset/<GESTO>/<gesto>_000.jpg`) e acrescenta
modo rajada, progresso por classe e recusa de quadros quase identicos ao anterior.

**12 imagens foram descartadas na revisao**, e isso importa:

| classe | descartadas | motivo |
|---|---|---|
| PEDRA | `045`, `046` | mao aberta - gesto de PAPEL salvo na pasta PEDRA |
| TESOURA | `048` a `057` | sem gesto no quadro: parede, ombro, rosto, braco borrado |

Foram encontradas montando folhas de contato numeradas com todas as imagens de cada classe. O
modo rajada salva a cada 0,45s e continuou gravando durante a troca de gesto. Se tivessem ficado,
a CNN aprenderia que "parede vazia = TESOURA".

Os arquivos nao foram apagados: ficaram guardados fora deste pacote, junto com um registro do
motivo de cada descarte.

Resultado final: 45 / 45 / 48, desbalanceamento de 1,07x - dentro das duas regras da celula 6 do
notebook (minimo 45 por classe, desbalanceamento <= 2x).

## Etapa 2 - Treino da CNN

| | |
|---|---|
| Treino / teste | 103 / 35 imagens |
| Epocas | 12 |
| Perda | 1,1661 -> 0,3652 |
| Acuracia de teste | **88,57%** |

Arquivos: `curva_perda_baseline.png` e `matriz_confusao_baseline.png`.

## Etapa 3 - 10 rodadas de jokenpo

`resultados/10_rodadas_normal.csv` - 12 rodadas registradas (o minimo pedido era 10).

| | |
|---|---|
| Acertos | 10 de 12 (**83,3%**) |
| Confianca media | 63,1% |
| Por gesto | PAPEL 4/4, PEDRA 3/4, TESOURA 3/4 |

Captura da webcam com a previsao: `entregas/webcam_previsao_normal.png`.

## Etapa 4 - Teste de robustez

**Condicao escolhida:** iluminacao fraca. A hipotese foi escrita **antes** de executar, em
`HIPOTESE.md`.

### A primeira tentativa nao valeu, e esta registrada

O primeiro teste adverso deu **94,4%** - melhor que o teste normal (83,3%). Em vez de comemorar,
medi o que tinha acontecido:

- a luminosidade da regiao de captura caiu apenas de **107,0 para 95,6** (11%). Nao houve condicao
  adversa de fato;
- **13 das 18 rodadas** foram registradas a 1 segundo ou menos da anterior: com a mao parada, o
  mesmo quadro foi contado varias vezes;
- 8 dessas rodadas foram PEDRA, a classe mais facil (8/8), o que puxou a media.

O arquivo esta preservado como `resultados/adverso_antes_tentativa1_invalida.csv`.

A ferramenta foi corrigida: passou a **exigir 2 segundos entre rodadas** e a **mostrar a
luminosidade ao vivo**, para que a condicao adversa seja verificavel enquanto se joga.

### Segunda tentativa

`resultados/adverso_antes.csv` - 10 rodadas com o modelo baseline.

| | |
|---|---|
| Acertos | 6 de 10 (**60,0%**) |
| Luminosidade media | 121,8 |
| Por gesto | PAPEL 2/2, PEDRA 1/4, TESOURA 3/4 |

A queda de 83,3% para 60,0% confirma a direcao da hipotese: iluminacao fraca degrada o
reconhecimento.

**Mas a previsao especifica errou.** Eu havia apostado que TESOURA seria a classe mais prejudicada,
por depender de enxergar dois dedos separados. Quem desabou foi **PEDRA (1/4)**, enquanto TESOURA
manteve 3/4. Olhando as probabilidades no CSV, os tres erros de PEDRA foram previstos como PAPEL
com confianca de 56% a 85%: com pouca luz o punho perde a sombra que define os vincos dos dedos e a
silhueta engorda, ficando parecida com uma mao espalmada. Era um mecanismo que eu nao tinha
considerado.

## Etapa 5 - A melhoria controlada

**Alteracao unica:** `augment=True` no `GestureDataset` (deslocamento aleatorio de ate 4 px e
variacao de brilho de 0,75x a 1,25x). Arquitetura, epocas, taxa de aprendizado e split ficaram
identicos.

### Em condicao normal: empate exato

| | acuracia de teste | perda final |
|---|---|---|
| baseline | 88,57% | 0,3652 |
| com augmentation | 88,57% | 0,4912 |

### Nas rodadas ao vivo, o numero enganou

`resultados/adverso_depois.csv` deu **90,9%** (10 acertos em 11), contra 60,0% do baseline. Parece
um ganho de 31 pontos - **mas nao e comparavel**: a luminosidade media foi **144,1** nessa sessao
contra **121,8** na anterior. O segundo teste teve mais luz que o primeiro, entao boa parte da
diferenca vem da lampada, nao do modelo.

Nao foi possivel repetir a sessao com a iluminacao igual.

### O teste controlado, que e o confiavel

Para comparar sem depender da luz do ambiente, escureci as **imagens do conjunto de teste** por um
fator conhecido e avaliei os dois modelos exatamente nas mesmas entradas:

| fator de brilho | baseline | augmentation | diferenca |
|---|---|---|---|
| 1,00 (original) | 88,6% | 88,6% | 0,0 |
| 0,75 | 88,6% | 80,0% | −8,6 |
| 0,50 | 88,6% | 65,7% | **−22,9** |
| 0,35 | 85,7% | 57,1% | **−28,6** |
| 0,25 | 77,1% | 34,3% | **−42,8** |
| 0,15 | 60,0% | 34,3% | −25,7 |

**O augmentation piorou a robustez em todos os niveis de escurecimento.** Grafico em
`entregas/teste_adverso_controlado.png`.

Isso estava previsto como risco na hipotese registrada: *"o augmentation reduz o sinal efetivo de um
dataset que ja e pequeno (103 imagens de treino), entao existe risco real de piorar"*.

**Por que piora.** Com 103 imagens, cada exemplo ainda e necessario para o modelo fixar o formato de
cada gesto. O augmentation multiplica a variacao que a rede precisa cobrir sem acrescentar
informacao nova, e o resultado aparece na perda final: 0,4912 contra 0,3652. O modelo terminou o
treino **menos ajustado**, e um modelo menos ajustado degrada mais rapido quando a entrada sai da
distribuicao. A faixa de brilho do augmentation (0,75x a 1,25x) tambem e estreita demais para
preparar a rede para escurecimento de 0,50x ou 0,25x.

## Um ganho, um efeito colateral e uma limitacao

**Ganho:** nenhum, na metrica que importava. O augmentation empatou em condicao normal (88,57%) e
perdeu em toda condicao adversa. O ganho real da entrega veio de outro lugar: **a revisao do
dataset**. Remover as 12 imagens com rotulo errado foi o que permitiu treinar um modelo de 88,57%.

**Efeito colateral:** a perda final subiu de 0,3652 para 0,4912. Em 12 epocas fixas, o augmentation
consome capacidade de ajuste que o dataset pequeno nao tem sobrando - o modelo fica subajustado.

**Limitacao:** o dataset saiu de **uma pessoa, um comodo, uma sessao, uma iluminacao**. Nenhum
modelo treinado assim aprende invariancia a luz, porque nunca viu variacao de luz. Foi isso que o
teste controlado mediu: aos 25% de brilho, o melhor modelo cai para 77,1%. A correcao nao e
augmentation - e coletar com iluminacao variada, em momentos e ambientes diferentes.

## O que eu faria diferente

1. **Coletar com luz variada desde o inicio**, em vez de simular variacao depois. Augmentation nao
   substitui dado real, especialmente com 103 exemplos de treino.
2. **Fixar o protocolo do teste adverso antes de jogar** - luminosidade alvo e intervalo minimo
   entre rodadas. As duas primeiras tentativas foram perdidas por nao ter feito isso.
3. **Registrar a luminosidade desde a primeira rodada.** So percebi o problema porque passei a
   medir; sem isso, teria reportado 94,4% de "robustez" que nao existia.

## Arquivos da entrega

| Arquivo | Conteudo |
|---------|----------|
| `aula05_extra_jokenpo_cnn.html` | Notebook executado - abre no navegador |
| `jokenpo_dataset/` | 138 imagens em PEDRA, PAPEL e TESOURA |
| `HIPOTESE.md` | Hipotese registrada antes do teste adverso |
| `curva_perda_baseline.png` | Curva de perda |
| `matriz_confusao_baseline.png` | Matriz de confusao |
| `comparacao_baseline_augmentation.png` | Curvas e matrizes lado a lado |
| `teste_adverso_controlado.png` | Acuracia e confianca x escurecimento |
| `10_rodadas_normal.csv` | As 12 rodadas em condicao normal |
| `adverso_antes.csv` / `adverso_depois.csv` | Teste adverso, antes e depois |
| `adverso_antes_tentativa1_invalida.csv` | A tentativa descartada, preservada |
| `webcam_previsao_*.png` | Capturas da webcam com a previsao |
