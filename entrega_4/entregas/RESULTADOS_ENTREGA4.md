# Entrega 4 - Numeros com Redes Neurais

Treinar uma rede neural (MLP) para reconhecer digitos, comparar com o k-NN, e testar os dois em
digitos desenhados a mao.


## Resultado principal

| Modelo | Treinado em | Testado em | Acuracia |
|---|---|---|---|
| Rede neural MLP | `digits` | `digits` | 96,00% |
| k-NN (k=3) | `digits` | `digits` | 98,44% |
| **Rede neural MLP** | **`digits`** | **minhas imagens** | **16,83%** |
| **k-NN (k=3)** | **`digits`** | **minhas imagens** | **38,61%** |
| Rede neural MLP | minhas imagens | minhas imagens | 65,38% |
| k-NN (k=3) | minhas imagens | minhas imagens | 80,77% |

**A rede neural perdeu para o k-NN nas duas comparacoes que importam.** No dataset de origem os dois
empatam na pratica (96% e 98%). Fora dele, a distancia abre: 16,83% contra 38,61%.

## A previsao registrada antes estava errada

O notebook pede registrar uma previsao antes de rodar, e a minha ficou gravada na secao
"Planejamento": apostei que a MLP faria entre 50% e 65% nas minhas imagens, porque fronteiras de
decisao flexiveis deveriam generalizar melhor que comparar distancia com exemplos memorizados.

Deu 16,83%. A hipotese estava invertida: **a flexibilidade da rede a tornou mais fragil**, nao mais
robusta, quando o dominio mudou.

## Por que a MLP desaba

Ela colapsa para poucas classes. Das 101 previsoes:

- **57 foram "4"** (56% de tudo)
- usou apenas **7 das 10 classes** - nunca respondeu 3, 5 nem 9
- as tres classes mais previstas concentram 85% das respostas

O k-NN, no mesmo teste, distribuiu entre as 10 classes.

A causa esta na densidade de tinta, medida no formato 8x8:

| | media do pixel | desvio | pixels zerados |
|---|---|---|---|
| `digits` | 4,89 | 6,02 | 49% |
| minhas imagens | 2,67 | 4,65 | 46% |

Meu traco tem quase **metade da tinta** do dataset original - mouse produz linha fina e de espessura
constante, o `digits` vem de caneta em papel digitalizada em 1990. Com menos ativacao entrando na
rede, ela desaba sempre para o mesmo canto do espaco de saida. O k-NN so mede distancia euclidiana,
entao degrada de forma mais suave.

**Descartei a hipotese do `StandardScaler`:** sem ele, a MLP faz 18,81% nas minhas imagens, contra
16,83% com. Nao e problema de normalizacao, e diferenca de dominio.

## Confianca nao serve de filtro aqui

| | confianca media |
|---|---|
| quando a MLP acerta | 86,1% |
| quando a MLP erra | 63,7% |

Existe sinal, mas com sobreposicao demais. **Das cinco previsoes mais confiantes, tres estao
erradas.** A mais confiante de todas (`7_leonardo_01.png`, 98,3%) acertou; a segunda
(`2_leonardo_10.png`, 97,9%) errou.

## O erro mais interessante

`2_leonardo_10.png` - previsto **4**, com **97,9%** de confianca.

E a mesma imagem que o k-NN errou na Aula 2, quando respondeu **0**. Um 2 em letra cursiva, com laco
fechado na base. Em 8x8 o laco vira um miolo claro cercado de tinta: o k-NN leu a rosquinha do 0, a
MLP leu o cruzamento de tracos do 4. Dois modelos, dois erros diferentes, os dois confiantes.

O defeito nao esta no algoritmo - esta na entrada. 8x8 nao guarda a diferenca entre um laco fechado
e um cruzamento de retas.

## A melhoria que mais rende nao e trocar de modelo

Ablacao do pre-processamento, mudando um fator por vez (k-NN treinado no `digits`):

| fator alterado | efeito |
|---|---|
| threshold 0,20 -> 0,25 | +0,00 pontos |
| filtro LANCZOS -> BILINEAR | +1,98 pontos |
| **margem 20% -> 15%** | **+13,86 pontos** (38,61% -> 52,48%) |

A funcao `preprocess_external_digit` do notebook usa `margin = side // 5` (20%). Trocar por
`side // 7` (~14%) vale 14 pontos.

Com 20% de margem de cada lado o digito ocupa ~71% da largura do quadro; com 15%, ~77%. Em 8x8 isso
e a diferenca entre o traco cair sobre 5 ou 6 pixels. O `digits` tem os digitos preenchendo quase
todo o quadro, entao margem menor aproxima as distribuicoes.

Para dimensionar: trocar de modelo (k-NN -> MLP) **custou** 22 pontos; mudar um numero no
pre-processamento **ganhou** 14.

> A funcao original do notebook **nao foi alterada**. A ablacao reimplementa o mesmo pipeline com os
> parametros expostos, para poder varia-los sem mexer no codigo da aula.

## Conclusao para o projeto

Duas coisas que levo para o projeto de gestos:

1. **Modelo treinado no contexto de uso vence modelo generico**, e por muito: 16,83% -> 65,38% na
   MLP, 38,61% -> 80,77% no k-NN. Reforca a decisao registrada no `PROJETO.md` de coletar gestos
   das pessoas que vao usar o sistema, em vez de usar um dataset pronto.
2. **Preparar a entrada rende mais que trocar de algoritmo.** Na coleta da Aula 3, padronizar
   enquadramento, distancia e iluminacao vale mais esforco que testar arquiteturas.

## Limitacoes

1. **Autor unico** - as 101 imagens sao minhas. O 65,38% mede "reconhece o meu traco".
2. **Teste pequeno** no bloco treinado nas minhas imagens: 26 exemplos, 2 ou 3 por classe.
3. **Traco de mouse nao e traco de caneta** - e essa e exatamente a variavel que derruba a
   transferencia, como a tabela de densidade mostra.

## Arquivos

| Arquivo | Conteudo |
|---------|----------|
| `aula04_rede_digitos.html` | Notebook executado - abre no navegador |
| `aula04_rede_digitos.ipynb` | O mesmo, para reexecutar |
| `digitos_desafio/` | As 101 imagens |
