# Hipotese do teste de robustez - registrada ANTES de executar

> Escrita antes de rodar qualquer rodada adversa. Data: 26/09/2026.
> A Etapa 4 da entrega pede a hipotese antes do teste; depois de ver o resultado nao vale mais.

## Condicao adversa escolhida

**Iluminacao fraca.**

Escolhi essa entre as opcoes do enunciado (iluminacao, fundo, distancia, oclusao, inclinacao,
pessoa nova, duas maos) por ser a que mais se aproxima do caso real descrito no `PROJETO.md`: o
sistema de gestos vai rodar numa casa, e a pessoa vai usa-lo tambem a noite. Se o modelo so
funciona com luz boa, o projeto nao serve.

## O que espero que aconteca

**Espero uma queda grande, entre 30 e 50 pontos percentuais.** O baseline tem 88,57% de acuracia no
conjunto de teste; na condicao adversa espero algo entre **40% e 60%**.

## Por que

Tres razoes tecnicas, nesta ordem de peso:

1. **A rede recebe brilho absoluto, nao relativo.** O `GestureDataset` do notebook faz apenas
   `image / 255.0` - nao ha normalizacao por media nem por desvio padrao da propria imagem. Entao
   escurecer o quadro desloca todos os valores de entrada para baixo, e a rede ve numeros que nunca
   apareceram no treino. E o mesmo mecanismo que derrubou a MLP na Entrega 4: la, as minhas imagens
   tinham densidade de tinta 2,67 contra 4,89 do dataset, e a acuracia caiu de 96% para 16,83%.

2. **O dataset foi coletado numa sessao unica.** As 138 imagens sairam todas do mesmo comodo, na
   mesma hora, com a mesma luz. O modelo nao teve como aprender invariancia a iluminacao porque
   nunca viu variacao de iluminacao.

3. **O contorno da mao depende de contraste.** Com pouca luz, a diferenca entre a pele e a parede
   clara do fundo diminui, e a silhueta - que e o que separa punho de mao aberta de dois dedos -
   fica menos definida em 64x64.

## Previsao mais especifica

Espero que **TESOURA seja a classe mais prejudicada**. PEDRA e PAPEL se distinguem pela area
ocupada (punho compacto contra mao espalmada), que sobrevive melhor a perda de contraste. TESOURA
depende de enxergar **dois dedos separados** - um detalhe fino, o primeiro a sumir quando a
silhueta perde definicao.

## O que eu esperaria da melhoria (augmentation)

A melhoria planejada para a Etapa 5 e ativar `augment=True` no `GestureDataset`, que aplica
deslocamento aleatorio de ate 4 px e **variacao de brilho de 0,75x a 1,25x**.

Espero que ajude, mas **pouco**: a faixa de brilho do augmentation vai so ate 0,75x, e a condicao
adversa que vou criar sera mais escura que isso. O augmentation tambem reduz o sinal efetivo de um
dataset que ja e pequeno (103 imagens de treino), entao existe risco real de **piorar** a acuracia
no teste normal enquanto melhora um pouco na condicao adversa.

Se piorar nos dois, a conclusao sera que 103 imagens nao suportam augmentation, e o caminho certo
seria coletar com luz variada em vez de simular variacao.
