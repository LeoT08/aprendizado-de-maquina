# Aprendizado de Máquina

> **Grupo:** Igor Hellman Melo, Leonardo Vieira Teixeira, Raul Prata Milan, Caio Gadotti.

Três atividades da disciplina, cada uma com o notebook executado, os dados, os modelos treinados e
um relatório com a análise. Todas rodam de ponta a ponta no ambiente descrito em
[Como rodar](#como-rodar).

---

## 1. Números com redes neurais

**[`entrega_4/`](entrega_4/)** · [relatório](entrega_4/RESULTADOS_ENTREGA4.md) ·
[notebook](entrega_4/entregas/aula04_rede_digitos.html)

Treinar uma MLP para reconhecer dígitos, comparar com o k-NN e testar os dois em dígitos
desenhados à mão.

| Modelo | Treinado em | Testado em | Acurácia |
|---|---|---|---|
| MLP | `digits` | `digits` | 96,00% |
| k-NN (k=3) | `digits` | `digits` | 98,44% |
| **MLP** | **`digits`** | **dígitos desenhados** | **16,83%** |
| **k-NN (k=3)** | **`digits`** | **dígitos desenhados** | **38,61%** |

O resultado que interessa não é o da primeira linha. Dentro do dataset de origem os dois modelos
empatam na prática; fora dele a rede neural despenca para 16,83% e perde feio para um k-NN. Trocar
de dataset custou mais desempenho do que trocar de modelo jamais devolveria.

## 2. Jokenpô com uma CNN em tempo real

**[`entrega_6/`](entrega_6/)** · [relatório](entrega_6/RESULTADOS_ENTREGA6.md) ·
[notebook](entrega_6/entregas/aula05_extra_jokenpo_cnn.html)

Coletar um dataset próprio de gestos pela webcam, treinar uma CNN, jogar contra ela ao vivo e
tentar quebrá-la de propósito.

| | |
|---|---|
| Dataset | 138 imagens (PEDRA 45 / PAPEL 45 / TESOURA 48) |
| Acurácia de teste | **88,57%** |
| 10 rodadas ao vivo | 83,3% |
| Melhoria testada (augmentation) | **piorou** a robustez |

Duas coisas valem a leitura. **Doze imagens tinham rótulo errado** e só apareceram ao montar folhas
de contato numeradas — havia mão aberta na pasta PEDRA e quadros sem gesto nenhum em TESOURA. E o
**primeiro teste adverso foi invalidado pelos próprios números**: deu 94,4%, melhor que a condição
normal, porque a luz tinha caído só 11% e metade das rodadas contou o mesmo quadro várias vezes.
Está preservado no repositório, junto com a versão corrigida.

## 3. Sumô de robôs por imitação

**[`entrega_7/`](entrega_7/)** · [relatório](entrega_7/RESULTADOS_ENTREGA7.md) ·
[notebook](entrega_7/entregas/aula07_sumo_ia.html)

Um simulador de sumô roda em um processo; o notebook conecta por TCP, lê sensores e comanda o robô.
Um piloto joga, cada ciclo grava `(sensores, ação)`, e uma MLP aprende a repetir as escolhas dele.

| | |
|---|---|
| Demonstrações | 1.659 amostras em 6 lutas |
| Acurácia da imitação | **93,25%** |
| Latência do laço cérebro-corpo | 10,6 ms (p95: 12,6 ms) |
| Torneio contra o bot | **3 x 0** |
| Copa com largada sorteada (20 lutas) | **6 x 14 contra nós** |

O placar oficial da Copa foi 3 x 0 — com as três lutas durando **6,47 s cada**, o mesmo tempo. A
arena sempre recomeça na mesma posição e os dois lutadores são redes determinísticas, então a
melhor de 3 é a mesma luta repetida. Sorteando a largada, o mesmo lutador perde 14 de 20, caindo da
plataforma em todas.

E a culpa não é da estratégia: nas mesmas 20 largadas, o piloto por regras faz 12/20 e a rede que o
copiou faz 6/20. A rede discorda dele em só 5,7% dos quadros, mas **81% dessas discordâncias viram
"acelerar"** — o erro tem lado, e em combate cada erro muda o estado seguinte.

---

## Como rodar

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
jupyter lab
```

Testado em Python 3.14.5 (Windows). A atividade 3 precisa de `pygame-ce` — o `pygame` comum ainda
não tem pacote para o 3.14, e o `-ce` é compatível linha a linha.

Cada pasta tem um `README.md` ou `RESULTADOS_*.md` explicando o que rodar e em que ordem.

## O que não está aqui

- **Slides e materiais das aulas** (`Aulas/`, `*.pptx`): são do professor, não nossos para
  republicar.
- **As 138 imagens do dataset de jokenpô**, os quadros de tela cheia da webcam e as imagens
  descartadas da atividade 2. Em boa parte dos quadros da classe PEDRA o rosto de uma pessoa
  aparece nítido, dentro de casa, e este repositório é público. Ficou tudo que sustenta o
  resultado: notebook executado, matriz de confusão, curva de perda, o modelo treinado, as 10
  rodadas ao vivo e o teste adverso. Detalhes em
  [`entrega_6/jokenpo_dataset/LEIA-ME.md`](entrega_6/jokenpo_dataset/LEIA-ME.md).

A Aula 1, que montou o ambiente e o primeiro pipeline de visão, está em [`AULA1.md`](AULA1.md).
