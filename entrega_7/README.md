# Entrega 7 - Sumo de robos com aprendizado por imitacao

> **Grupo:** Igor Hellman Melo, Leonardo Vieira Teixeira, Raul Prata Milan, Caio Gadotti.

## Por onde comecar

Abra **`entregas/aula07_sumo_ia.html`** no navegador: o notebook executado, com
todas as saidas. Depois leia **`RESULTADOS_ENTREGA7.md`**, que tem a analise.

## Resultado em uma tabela

| | |
|---|---|
| Demonstracoes | 1.659 amostras em 6 lutas |
| Acuracia da imitacao | **93,25%** |
| Latencia do laco cerebro-corpo | 10,6 ms (p95: 12,6 ms) |
| Torneio contra o bot | **3 x 0** |
| Copa (formato oficial) | **3 x 0** |
| Copa com largada sorteada (20 lutas) | **6 x 14 contra nos** |

## Os itens pedidos na entrega

| Item | Onde esta |
|---|---|
| Conexao e sensores testados | `entregas/aula07_sumo_ia.html`, etapa 1 |
| 300+ amostras em 3+ lutas | `entregas/teleop_sumo.csv` (1.659 em 6 lutas) |
| Imitacao com 85%+ | 93,25% - `entregas/imitacao_matriz_e_perda.png` |
| Torneio contra o bot vencido | `entregas/torneio_vs_bot.csv` |
| Copa disputada | `entregas/copa.csv` e `entregas/copa_estendida.csv` |
| Analise agressividade x risco | `RESULTADOS_ENTREGA7.md`, secao "A analise que vale ponto" |
| O que muda para o carrinho fisico | `RESULTADOS_ENTREGA7.md`, secao propria |
| Ficha da Copa preenchida | `RESULTADOS_ENTREGA7.md`, no topo |

## Tres coisas que valem a leitura

**1. O placar oficial da Copa nao mede nada.** As tres lutas duraram 6,47 s
**cada**, o mesmo tempo. A arena sempre recomeca na mesma posicao e os dois
lutadores sao redes deterministicas, entao a melhor de 3 e a mesma luta repetida
tres vezes. Refazendo a Copa com a largada sorteada, o mesmo lutador que tinha
"vencido 3 x 0" perde **14 de 20**.

**2. A rede joga pior que o piloto que ela copiou.** Nas mesmas 20 largadas, o
piloto por regras faz 12/20 e a rede faz 6/20. A acuracia de 93% nao capturou
isso: ela mede se a rede copia bem os estados que o piloto visita, nao o que
acontece quando a rede, errando, se leva a estados que ele nunca visitou.

**3. O erro da imitacao tem lado.** A rede discorda do piloto em so 5,7% dos
quadros - mas **81% dessas discordancias viram FRENTE**. Nao e ruido, e
agressividade, e faz sentido: FRENTE e 75% do dataset. Em combate cada erro muda
o estado seguinte, entao o vies nao soma, multiplica - e acaba em queda. Nas 14
derrotas, quem caiu fomos nos.

## A arena nao deixava a Copa acontecer

`arena_robos.py` pilota o robo B com o bot interno em todo quadro, ignorando
qualquer cliente conectado nele - a celula 7 do notebook carregava o lutador
rival e mandava comandos sem efeito nenhum. `ferramentas/arena_lcml.py` importa
a arena original e muda uma regra: o bot de B vira reserva e so assume quando
ninguem esta comandando B. Os arquivos do professor nao foram alterados.

## Como rodar

```powershell
# entrega inteira de ponta a ponta (treina o rival, sobe a arena, executa o notebook)
.\rodar_entrega.bat

# so a arena, com janela, para assistir
.\abrir_arena.bat

# regravar as demonstracoes na mao, com as setas
.\regravar_na_mao.bat
```

Precisa de `pygame-ce` (ja no `requirements.txt`): o `pygame` comum nao tem wheel
para o Python 3.14 deste projeto, e o `-ce` e drop-in.

## Estrutura

O pacote enviado (`sumo.zip`) abre nesta estrutura:

```
sumo/
  README.md                   este arquivo
  RESULTADOS_ENTREGA7.md      a analise completa
  entregas/                   o que a entrega pede: HTML, CSVs, figuras, modelos
  ferramentas/                o que o grupo escreveu
  arena/                      material do professor, intacto
  aula07_sumo_ia.ipynb        notebook executado (copia de trabalho)
  teleop_sumo.csv             demonstracoes (copia de trabalho)
  lutador_equipe.joblib       a rede treinada (copia de trabalho)
  lutador_rival.joblib        o adversario da Copa (copia de trabalho)
  *.bat                       atalhos de execucao
```

As copias na raiz existem porque o notebook le e escreve nelas quando e
reexecutado; as versoes congeladas da entrega estao em `entregas/`.
