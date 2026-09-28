# Entrega 7 - Sumo de robos: o notebook comanda a arena

> **Grupo:** Igor Hellman Melo, Leonardo Vieira Teixeira, Raul Prata Milan, Caio Gadotti.

## Resumo

| | |
|---|---|
| Demonstracoes | 1.659 amostras em 6 lutas (minimo pedido: 300 em 3) |
| Imitacao (MLP 32/16) | **93,25%** de acuracia (exigencia: 85%) |
| Latencia do laco cerebro-corpo | **10,6 ms** de media, 12,6 ms no p95 |
| Torneio contra o bot | **3 x 0**, as tres por queda do adversario |
| Copa (melhor de 3, formato oficial) | **3 x 0** |
| Copa com largada sorteada (20 lutas) | **6 x 14 contra nos** |
| Causa das derrotas | agressividade - caimos da plataforma nas 14 |

As duas ultimas linhas sao o assunto deste documento. O formato oficial da Copa
nos deu 3 x 0; quando a largada deixa de ser sempre a mesma, o mesmo lutador
perde 14 de 20. A secao [A analise que vale ponto](#a-analise-que-vale-ponto)
explica por que, com a medida que prova a causa.

---

## Ficha da Copa

| Item | Valor |
|---|---|
| Amostras de teleoperacao | 1.659, em 6 lutas |
| Acuracia da imitacao | 93,25% |
| Torneio vs bot (2 de 3?) | **sim** - 3 x 0 |
| Latencia media | 10,6 ms (p95: 12,6 ms) |
| Copa: vitorias/derrotas | 3 x 0 no formato oficial; 6 x 14 com largada sorteada |
| Causa das derrotas (agressivo x medroso) | **agressivo** - 81% dos erros da rede viram FRENTE |

- [x] Conexao e sensores testados.
- [x] 300+ amostras em pelo menos 3 lutas. (1.659 em 6)
- [x] Imitacao com 85%+. (93,25%)
- [x] Torneio contra o bot vencido (2 de 3). (3 x 0)
- [x] Copa disputada.
- [x] Analise agressividade x risco documentada.
- [x] Resposta: o que muda para o carrinho fisico?

---

## Etapa 1 - Conexao e sensores

O notebook conecta em `127.0.0.1:5555` e recebe, a cada ciclo, um JSON com cinco
raios (0, -45, +45, -90 e +90 graus do nariz do robo), a velocidade normalizada,
o rumo e a distancia do adversario e a distancia do centro da plataforma. Esse
vetor de 9 numeros e tudo que a rede enxerga.

Uma restricao importante veio dai: **a direcao do centro nao esta nas features**.
Existe `dist_centro`, que e um escalar, e nao um rumo. Entao a fuga da borda tem
que ser deduzida dos raios - raio curto significa beirada perto naquela direcao,
logo o lado mais aberto aponta para dentro. Isso define como o piloto foi escrito.

## Etapa 2 - As demonstracoes

| | |
|---|---|
| Lutas | 6 |
| Amostras | 1.659 |
| FRENTE / ESQUERDA / DIREITA / FREIO | 1.243 / 263 / 129 / 24 |
| Vitorias nas lutas gravadas | 6 de 6 |

As demonstracoes foram geradas por `ferramentas/piloto_especialista.py`, um piloto
por regras que joga pelo mesmo protocolo TCP da teleoperacao manual. A celula 2
mantem o caminho manual intacto (`PILOTO_AUTOMATICO = False` abre a janela com as
setas), e `regravar_na_mao.bat` refaz coleta e treino em um clique.

Duas decisoes de projeto que valem registro:

**O piloto so pode usar o que a rede tambem ve.** Se ele decidisse com a posicao
absoluta `x, y` - que o JSON traz, mas que nao entra no vetor de features - a rede
veria estados identicos rotulados com acoes diferentes e nunca chegaria aos 85%.
O piloto usa os mesmos 9 numeros.

**Ruido de 5% nas acoes.** Sem isso o simulador e deterministico: mesma largada e
mesma politica produzem a mesma luta, e as 6 lutas seriam uma so, repetida. O
ruido tambem e a origem dos 24 exemplos de FREIO.

**Um conserto no pareamento.** O notebook original gravava `features(estado)`
*depois* de enviar a acao, isto e, o estado seguinte. Ao vivo (etapa 4) a rede
decide olhando o estado atual. Treinar com o pareamento defasado ensina a acao
errada justamente na fronteira de decisao, onde um quadro de 33 ms muda o rumo em
ate 5 graus. A celula 2 passou a gravar o estado que gerou a acao.

## Etapa 3 - Imitacao

| | |
|---|---|
| Treino / teste | 1.244 / 415 amostras (nenhum PARAR foi gravado) |
| Arquitetura | `StandardScaler` + MLP (32, 16), 916 parametros |
| Treino | 354 epocas, perda final 0,2278 |
| **Acuracia** | **93,25%** |

Por classe, que e onde a media global esconde coisa:

| classe | acertos | observacao |
|---|---|---|
| FRENTE | 305 / 311 (98%) | e 75% do dataset |
| ESQUERDA | 56 / 66 (85%) | |
| DIREITA | 26 / 32 (81%) | classe mais rara das tres uteis |
| FREIO | 0 / 6 (0%) | 24 exemplos no total; a rede nunca preve FREIO |

Figura: `entregas/imitacao_matriz_e_perda.png`.

## Etapa 4 - A IA lutando sozinha

Latencia do ciclo completo (montar o vetor, consultar a rede, mandar pela rede e
receber o estado novo): **10,6 ms de media, 12,6 ms no p95**. A arena roda a 30
quadros por segundo, ou seja, 33 ms por quadro - o laco de decisao cabe com folga
dentro de um quadro. E esse o numero que decide se o mesmo codigo serve para um
carrinho real.

## Etapa 5 - Torneio contra o bot

| luta | vencedor | caiu | duracao |
|---|---|---|---|
| 1 | IA | bot | 6,23 s |
| 2 | IA | bot | 6,10 s |
| 3 | IA | bot | 6,17 s |

**3 x 0.** Nas tres, quem caiu foi o bot. Arquivo: `entregas/torneio_vs_bot.csv`.

## Etapa 6 - Analise por zona

A celula 6 classifica cada amostra gravada em tres zonas e mede quanto de FRENTE
tem em cada uma (`entregas/analise_zonas.csv`):

| zona | amostras | FRENTE |
|---|---|---|
| combate (inimigo a menos de 0,15) | 1.127 | 78,3% |
| manobra | 210 | 93,3% |
| risco_borda (`dist_centro` > 0,7) | 322 | **50,9%** |

Lido isolado, o numero parece bom: na zona de risco o piloto corta FRENTE quase
pela metade - freia e gira em vez de acelerar para o vazio. O problema e que esse
numero descreve o **piloto**, nao a rede que foi treinada com ele. A secao a
seguir mede a diferenca entre os dois.

## Etapa 7 - Copa

Formato oficial, melhor de 3, contra `lutador_rival.joblib`: **3 x 0**, com as
lutas durando **6,47 s cada - exatamente o mesmo tempo, tres vezes**.

Isso nao e sorte, e um defeito do formato: a arena recomeca sempre na mesma
posicao e os dois lutadores sao MLPs deterministicas. Mesma largada mais mesma
politica e igual a mesma luta. O placar 3 x 0 carrega a mesma informacao que um
placar de 1 x 0.

Arquivo: `entregas/copa.csv`.

### O rival

O enunciado manda receber o `lutador_rival.joblib` de outra equipe. Como esse
arquivo nao chegou, o rival foi treinado pelo proprio grupo
(`ferramentas/treinar_rival.py`) a partir de um piloto de **estilo oposto ao
nosso**: abandona a borda antes (limiar 0,70 contra 0,78), exige mira mais fina
(8 graus contra 12) e freia na aproximacao. Acuracia de imitacao de 92,6%, e vence
o bot interno em 12 de 12 largadas sorteadas. Quando o arquivo da outra equipe
chegar, basta substituir o `.joblib` e rodar a celula 7 de novo.

---

## A analise que vale ponto

> *"Suas derrotas vieram de excesso de agressividade ou de excesso de medo?"*

### O teste que o formato oficial nao faz

`ferramentas/copa_estendida.py` repete a Copa 20 vezes sorteando posicao e angulo
iniciais dentro da plataforma. As 20 lutas tem 20 duracoes diferentes - sao 20
situacoes, nao uma repetida.

| | |
|---|---|
| Nosso lutador | **6 vitorias em 20** |
| Rival | 14 |
| Derrotas em que **nos** caimos | **14 de 14** |

Das 20 lutas nenhuma terminou por tempo: sempre alguem caiu. E em toda derrota
nossa, quem caiu fomos nos. A resposta a pergunta da aula e **agressividade**.

### Mas a culpa nao e da estrategia

Rodando as **mesmas 20 largadas** com o piloto por regras no lugar da rede:

| piloto que ensinou | rede que aprendeu |
|---|---|
| **12 / 20** | **6 / 20** |

A rede joga pior que o piloto que ela copiou, na mesma estrategia e nas mesmas
situacoes. Entao o problema esta na imitacao, nao no plano de jogo.

O mesmo aparece contra o bot interno, em 12 largadas sorteadas que nenhum dos dois
modelos tinha visto:

| | contra o bot interno |
|---|---|
| Rival (estilo cauteloso) | **12 / 12** |
| Nosso lutador | **7 / 12** |

Ou seja: o 3 x 0 do torneio oficial tambem era efeito da largada fixa. Com a
largada sempre igual, uma unica trajetoria vencedora basta para ganhar tres vezes.

### Onde a imitacao vaza

`ferramentas/analise_imitacao.py` compara, **nos mesmos 1.659 estados gravados**,
a acao do piloto com a acao que a rede escolheria:

| zona | amostras | FRENTE (piloto) | FRENTE (rede) | delta |
|---|---|---|---|---|
| combate | 1.127 | 78,3% | 82,4% | **+4,1 pp** |
| manobra | 210 | 93,3% | 100,0% | **+6,7 pp** |
| risco_borda | 322 | 50,9% | 52,5% | +1,6 pp |
| **total** | 1.659 | 74,9% | 78,8% | **+3,9 pp** |

A rede discorda do piloto em apenas **5,7% dos quadros**. O que importa e o
destino dessas discordancias:

| o piloto queria | ESQUERDA 34, DIREITA 25, FREIO 24, FRENTE 11 |
|---|---|
| **a rede escolheu** | **FRENTE 76**, ESQUERDA 14, DIREITA 4 |

**81% das discordancias viram FRENTE.** O erro da imitacao nao e ruido: e vies, e
o vies tem uma direcao so. Faz sentido - FRENTE e 75% do dataset, entao chutar
FRENTE e a aposta barata que maximiza a acuracia de treino. Na zona de manobra a
rede chega a 100% de FRENTE: nunca corrige.

E aqui esta o mecanismo que transforma 5,7% de erro em 14 derrotas: no treino,
cada erro custa uma linha da matriz de confusao e acaba ali. **Em combate, cada
erro muda o estado seguinte.** Um quadro a mais de aceleracao coloca o robo mais
perto da borda, com mais velocidade e menos margem para virar - e o proximo estado
ja e um estado que o piloto nunca visitou, sobre o qual a rede nao foi treinada.
O erro nao soma, multiplica.

### Por que a acuracia de 93% nao avisou nada

Ela avisou, mas na linha que e facil ignorar: **FREIO, 0 de 6**. A rede nunca
aprendeu a frear. Numa metrica ponderada por 1.659 amostras, perder 24 exemplos
de FREIO custa 1,4% de acuracia. Numa luta em que a plataforma encolhe, nao saber
frear custa a partida.

Uma acuracia alta em dados coletados pelo proprio especialista mede se a rede
copia bem **os estados que o especialista visita**. Nao mede o que acontece quando
a rede, errando, se leva a estados que ele nunca visitou.

---

## Tres problemas encontrados no material da aula

**1. A Copa nao funciona com a arena original.** Em `arena_robos.py`, a funcao
`principal()` calcula `acao_bot_b = arena.decidir_bot(...)` em todo quadro em que a
fase e `CORRIDA`, e `Arena.passo()` da prioridade a esse valor sobre o `robo.acao`
recebido pela rede. O robo B e **sempre** o bot interno: a celula 7 carrega o
lutador rival, manda comandos e nenhum deles tem efeito.

A correcao esta em `ferramentas/arena_lcml.py`, que importa `Arena`, `Servidor` e
`desenhar` do arquivo original e muda uma regra so - o bot interno de B vira
reserva, e so assume quando nenhum cliente esta comandando B, usando o mesmo
`TIMEOUT_COMANDO` que a arena ja aplica:

```python
b_tem_piloto = time.time() - arena.b.ultimo_comando < ar.TIMEOUT_COMANDO
acao_bot_b = None if (arena.fase != "CORRIDA" or b_tem_piloto) else arena.decidir_bot(arena.b, arena.a)
```

Uma regra que atende as duas situacoes sem trocar de modo: no torneio ninguem
conecta em B e o bot pilota, como no original; na Copa o cliente do rival comanda
e o bot sai de cena. Nenhum arquivo do professor foi alterado.

**2. `sys.path.insert(0, "../arena")`** na celula 1 nao resolve no layout do zip: o
notebook fica *ao lado* de `arena/`, nao dentro de uma subpasta. Corrigido para
`"arena"`.

**3. `pygame` nao tem wheel para Python 3.14**, que e a versao do `.venv` deste
projeto. `pygame-ce` tem (`pygame_ce-2.5.8-cp314-cp314-win_amd64.whl`) e e
drop-in: `import pygame` continua funcionando sem mudar uma linha. Acrescentado ao
`requirements.txt`.

---

## Do simulador para o carrinho fisico

O contrato permanece; o que muda e quem preenche cada lado dele.

| | Na arena | No carrinho |
|---|---|---|
| Entrada | 5 raios sinteticos + rumo do adversario | sensores de distancia (ultrassom/ToF) + visao |
| Saida | FRENTE / ESQUERDA / DIREITA / FREIO | PWM nos dois motores |
| Transporte | TCP + JSON, 10,6 ms | serial com o Arduino, ~2 ms a 115200 baud |
| Fim de luta | o simulador declara | sensor de linha na borda, ou nada declara |

O que **nao** viaja junto e o que esta medido aqui: a rede aprendeu com raios que
nunca erram, distancia do inimigo com precisao perfeita e uma borda que o
simulador conhece com exatidao. Um sensor real devolve leitura ruidosa, perde
medida e tem angulo morto. Como ja sabemos que essa rede erra para o lado de
FRENTE quando esta incerta, ruido de sensor tende a **piorar exatamente o vies
que ja custou 14 lutas**.

A ponte honesta nao e portar o `.joblib`: e recoletar demonstracoes com os
sensores reais no laco, porque o vies que interessa nasce da distribuicao dos
dados, nao da arquitetura.

## O que eu faria diferente

1. **Balancear a coleta por acao, nao por tempo.** 75% de FRENTE e o que torna
   "chutar FRENTE" a estrategia otima para o treino. Gravar as manobras a taxa
   cheia e as retas a taxa reduzida atacaria o vies na origem.
2. **Sortear a largada desde a primeira luta.** Todo numero deste relatorio que
   informa alguma coisa veio de largadas sorteadas. O formato de largada fixa
   produziu um 3 x 0 que nao significava nada.
3. **Medir a politica jogando, nao so a acuracia.** A acuracia de 93% e o placar
   de 6/20 convivem sem contradicao. Se so a acuracia fosse reportada, a entrega
   pareceria melhor do que e.
4. **Realimentar os proprios erros no treino** (DAgger): deixar a rede jogar,
   gravar os estados em que ela se meteu, perguntar ao piloto o que fazer neles e
   retreinar. E o conserto direto do "o erro nao soma, multiplica".

## Arquivos da entrega

| Arquivo | Conteudo |
|---|---|
| `entregas/aula07_sumo_ia.html` | Notebook executado - abre no navegador |
| `entregas/aula07_sumo_ia.ipynb` | O mesmo notebook, com as saidas |
| `entregas/teleop_sumo.csv` | 1.659 demonstracoes, com a coluna `luta` |
| `entregas/lutador_equipe.joblib` | A rede treinada por imitacao |
| `entregas/lutador_rival.joblib` | O adversario da Copa |
| `entregas/imitacao_matriz_e_perda.png` | Matriz de confusao e curva de perda |
| `entregas/arena_luta.png` | Captura da arena no momento do choque |
| `entregas/torneio_vs_bot.csv` | As 3 lutas contra o bot |
| `entregas/copa.csv` | A Copa no formato oficial |
| `entregas/copa_estendida.csv` | As 20 lutas com largada sorteada |
| `entregas/vies_imitacao.csv` | Piloto x rede nos mesmos estados |
| `entregas/analise_zonas.csv` | FRENTE por zona (celula 6) |
| `entregas/ficha_copa.json` | Os numeros da ficha, gerados pelo notebook |
| `ferramentas/piloto_especialista.py` | Os dois pilotos por regras |
| `ferramentas/arena_lcml.py` | Arena com o robo B liberado para clientes |
| `ferramentas/treinar_rival.py` | Treino do adversario da Copa |
| `ferramentas/copa_estendida.py` | Copa de 20 lutas com largada sorteada |
| `ferramentas/analise_imitacao.py` | A medida do vies da imitacao |
| `ferramentas/executar_entrega.py` | Roda tudo de ponta a ponta |
| `ferramentas/alternar_piloto.py` | Troca entre piloto por regras e as setas |
| `ferramentas/empacotar.py` | Monta o zip de upload |
