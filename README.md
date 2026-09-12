# Aula 1 - Problema e primeiro pipeline

## Problema escolhido pelo grupo

**Reconhecimento visual de gestos como interface de acessibilidade.**

A demanda: pessoas com mobilidade reduzida nos membros superiores, ou que nao conseguem operar
teclado, mouse e botoes fisicos, dependem de terceiros para acionar equipamentos do dia a dia.
A proposta do grupo e usar a camera como sensor e o aprendizado de maquina como tradutor: um gesto
feito pelo usuario vira um comando discreto, e esse comando aciona o dispositivo.

| Item | Definicao |
|------|-----------|
| **Entrada** | Quadros de video da camera (`cv2.VideoCapture`) |
| **Saida** | Um comando discreto de uma lista fechada |
| **Tipo de problema** | Classificacao supervisionada (multiclasse) |
| **Metrica inicial** | Acuracia por classe + matriz de confusao (aula 3) |
| **Ponte com o hardware** | Comando enviado por serial (`pyserial`) ao microcontrolador |

### Por que esta aula ja e o esqueleto do projeto

A atividade de hoje detecta um objeto colorido e responde `ESQUERDA`, `CENTRO` ou `DIREITA`.
E exatamente a mesma forma do projeto final: **quadro de video -> caracteristica -> comando discreto**.
O que muda nas proximas aulas e *como* a decisao e tomada.

| | Hoje (aula 1) | Projeto final |
|---|---|---|
| Caracteristica | Centro do maior contorno da cor-alvo | Posicao da mao / pontos do gesto |
| Decisao | Regra escrita a mao (limiar HSV + margem) | Modelo treinado com dados rotulados |
| Classes | ESQUERDA / CENTRO / DIREITA / SEM_DETECCAO | Vocabulario de gestos a definir |

A regra de hoje e fragil de proposito: ela quebra quando a iluminacao muda ou quando outro objeto
da mesma cor entra em cena. Sentir essa fragilidade e o que justifica treinar um modelo na aula 3.

### Definicoes pendentes

- [ ] Vocabulario de gestos (quantas classes, quais) e o dispositivo que sera acionado
- [ ] Publico e parceiro da atividade extensionista (cadastro no Workalove)
- [ ] Hardware de atuacao: Arduino ou ESP32
- [ ] Decidir entre classificar a imagem inteira ou extrair pontos da mao antes de classificar

A escolha definitiva sera confirmada depois de verificar dados, hardware e demanda extensionista.

## O que aprendemos nesta aula

Montar o ambiente de desenvolvimento e realizar um experimento introdutorio generico: capturar video
da camera, processar imagens e detectar um padrao visual. Ainda nao controlamos hardware nem
implementamos o projeto final.

## Ambiente

O ambiente e um virtualenv na raiz do projeto. Para recriar do zero:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Para abrir o notebook:

```powershell
.\.venv\Scripts\Activate.ps1
jupyter lab aula01_camera.ipynb
```

No VS Code, selecione o kernel `.venv` no canto superior direito do notebook.

### Versoes verificadas nesta maquina

Python 3.14.5 - NumPy 2.5.3 - OpenCV 5.0.0 - matplotlib 3.11.2 - pandas 3.0.5 -
scikit-learn 1.9.1 - seaborn 0.13.2 - joblib 1.6.0 - PyTorch 2.14.0+cpu -
torchvision 0.29.0+cpu - pyserial 3.5

PyTorch esta na versao CPU. Basta para as aulas 1 a 3; na aula 4 (MobileNetV2) o treino em CPU
funciona, apenas fica mais lento.

## Bibliotecas que vamos usar

Hoje usamos principalmente **NumPy** e **OpenCV**, mas todas serao necessarias ao longo das 9 aulas.

### Hoje (Aula 1)

| Biblioteca | Para que serve | Exemplo de uso |
|-----------|---------------|----------------|
| **NumPy** | Manipular arrays (matrizes) de numeros. Uma imagem e uma matriz NumPy. | `np.array([40, 50, 50])` para definir um intervalo de cor. |
| **OpenCV** (`cv2`) | Abrir camera, ler imagens, converter cores, detectar contornos, desenhar na tela. | `cv2.VideoCapture(0)` abre a camera; `cv2.inRange()` detecta cor. |
| **matplotlib** | Mostrar graficos e imagens dentro do notebook. | `plt.imshow(img)` exibe uma imagem no notebook. |

### Aulas seguintes (ja instaladas)

| Biblioteca | Para que serve | Quando usaremos |
|-----------|---------------|-----------------|
| **pandas** | Manipular dados em tabela (como Excel). Ler e escrever CSV. | Aula 2 (metadados do dataset) e aula 8 (feedback da comunidade). |
| **scikit-learn** | Treinar modelos de aprendizado de maquina classico. | Aula 3 (baseline: Decision Tree, Random Forest, SVM). |
| **seaborn** | Graficos bonitos, especialmente matriz de confusao. | Aula 3 e 5 (avaliar onde o modelo acerta e erra). |
| **joblib** | Salvar e carregar modelos treinados em arquivo. | Aula 3 (salvar o baseline para reusar depois). |
| **PyTorch** | Treinar redes neurais profundas. | Aula 4 (MobileNetV2 com transferencia de aprendizado). |
| **torchvision** | Modelos de visao pre-treinados e ferramentas de imagem. | Aula 4 (carregar modelo, augmentation, ImageFolder). |
| **pyserial** | Comunicar com o Arduino pela porta USB. | Aula 6 e 7 (enviar comandos ao dispositivo). |

### Analogia para entender

Pense no projeto como uma cozinha:

- **NumPy** sao os ingredientes basicos (farinha, ovos) - tudo comeca aqui.
- **OpenCV** e a faca e a tabua - corta, processa, prepara os ingredientes (imagens).
- **scikit-learn** e o forno basico - assa o bolo (treina o modelo simples).
- **PyTorch** e o forno profissional - faz receitas complexas (redes neurais).
- **matplotlib/seaborn** sao os pratos - servem para apresentar o resultado.
- **pyserial** e o entregador - leva o produto (comando) ate o Arduino.
- **pandas** e o caderno de receitas - organiza tudo em tabela.

## Objetivo

Configurar o ambiente e transformar uma imagem da camera em uma primeira decisao computacional.

## Atividade experimental do dia

Capturar video da camera e detectar uma cor, contorno ou marcador visual. O resultado e uma
visualizacao e uma classificacao generica, nao um comando para o projeto final.

## Como o notebook esta organizado

| Passo | O que faz |
|-------|-----------|
| 1 | Verifica o ambiente e as versoes das bibliotecas |
| 1b | Define o kit da aula: `abrir_camera`, `rodar_camera`, `mostrar` |
| 2 | Abre a camera e exibe o video ao vivo |
| 3 | Converte BGR para HSV e cinza; mostra os canais H, S e V separados |
| 4 | Limiariza a cor-alvo com `cv2.inRange` e acha o maior contorno |
| 5 | Aplica a regra de decisao: ESQUERDA / CENTRO / DIREITA / SEM_DETECCAO |
| 6 | Valida a regra com quadros sinteticos (teste automatizado) |
| 7 | Salva as capturas de tela em `entregas/` |

Cada celula de camera tem um tempo limite (`duracao_s`) e para sozinha, ou antes se voce pressionar
**Q** na janela de video. O notebook nunca trava esperando uma tecla.

Para executar sem abrir janelas (verificacao automatica), defina `LCML_AUTO=1` antes de abrir o
Jupyter.

### Trocar a cor-alvo

Se nao houver um objeto verde a mao, mude `COR_ALVO` na celula do passo 4. Ja estao prontas as
faixas HSV de `verde`, `vermelho`, `azul`, `amarelo` e `laranja`. O vermelho usa duas faixas porque
fica nas duas pontas do circulo de matiz.

## Arquivos

| Arquivo | O que e |
|---------|---------|
| `aula01_camera.ipynb` | Notebook com o passo a passo da aula |
| `aula01_camera.ipynb.original` | Versao original, antes da adaptacao dos loops |
| `COMO-RODAR.md` | Passo a passo para executar e gerar as prints |
| `abrir_jupyter.bat` | Duplo clique: sobe o Jupyter Lab ja no notebook |
| `ferramentas/verificar_ambiente.py` | Confere bibliotecas, camera e pipeline |
| `ferramentas/calibrar_cor.py` | Clique no objeto e descubra a faixa HSV dele |
| `ferramentas/captura_guiada.py` | Espera voce mostrar o objeto e gera as prints da entrega |
| `requirements.txt` | Dependencias congeladas com `pip freeze` |
| `entregas/` | Capturas de tela da entrega |
| `01-aula-problema-e-primeiro-pipeline.pptx` | Slides da aula |

### Nota de calibragem

A faixa HSV do `verde` foi calibrada num **coco verde** sob luz artificial fraca. A casca e escura,
entao os limites de saturacao e valor ficaram baixos (`S>=30`, `V>=25`). Com a faixa padrao de verde
vivo (`S>=60`, `V>=50`) a mascara pegava so o reflexo da luz na casca - area de ~1600 px contra
~9500 px depois da calibragem.

Isso e um bom exemplo do limite da abordagem de hoje: o mesmo objeto, sob outra luz, exige outros
numeros. Na aula 3 quem descobre esses limites e o modelo, a partir dos dados.

As funcoes de camera e deteccao estao definidas no proprio notebook (passos 1b, 4 e 5). Quando o
projeto crescer, elas devem migrar para `src/capture.py` e `src/utils.py`.

## Entrega

- [x] Notebook executado sem erros
- [x] Camera abre e detecta a cor
- [x] Classificacao (ESQUERDA/CENTRO/DIREITA) funciona
- [x] Captura de tela salva em `entregas/`
- [x] README.md atualizado com o problema escolhido pelo grupo

## Extensao

Diagnostico da demanda e definicao do publico (3 h previstas).

Para o tema escolhido, o diagnostico deve responder: quem sao os usuarios, quais gestos sao
confortaveis para eles, qual equipamento faz mais diferenca no dia a dia e em que ambiente o
sistema vai funcionar (iluminacao, distancia da camera, fundo).
