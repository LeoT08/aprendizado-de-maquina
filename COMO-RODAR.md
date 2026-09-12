# Como rodar - Aula 1

Ambiente ja configurado nesta maquina. Este guia e o passo a passo para executar e gerar as prints.

## 1. Abrir o projeto

Abra o VS Code **nesta pasta** (`File > Open Folder`). O `.vscode/settings.json` ja aponta para o
interpretador `.venv`, entao o VS Code seleciona o Python certo sozinho.

No terminal do VS Code (PowerShell), ative o ambiente:

```powershell
.\.venv\Scripts\Activate.ps1
```

Se o PowerShell reclamar de politica de execucao:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## 2. Conferir que esta tudo certo

```powershell
.\.venv\Scripts\python.exe ferramentas\verificar_ambiente.py
```

Tem que terminar com `AMBIENTE OK`. Ele checa as 10 bibliotecas e abre a camera para testar.

## 3. Escolher a cor do objeto

O notebook vem configurado para **verde**. Se voce nao tiver um objeto verde, use o calibrador:

```powershell
.\.venv\Scripts\python.exe ferramentas\calibrar_cor.py
```

Abre uma janela com **video a esquerda e mascara a direita**. Clique algumas vezes sobre o objeto.
Quando ele ficar **branco na mascara** e o resto preto, a calibragem esta boa. Pressione **Q**:
o programa imprime no terminal a linha pronta para colar no notebook.

Dica: objetos grandes e de cor forte funcionam melhor. Na sua cena tem um objeto laranja que
serve bem - teste com `--cor laranja` no passo 4.

## 4. Gerar as prints da entrega

```powershell
.\.venv\Scripts\python.exe ferramentas\captura_guiada.py --cor verde --duracao 120
```

Troque `--cor` pela cor do seu objeto (`verde`, `laranja`, `vermelho`, `azul`, `amarelo`).

O que acontece: a janela abre e **espera voce**. Leve o objeto para a esquerda, para o centro e
para a direita. O texto embaixo diz quais zonas ainda faltam. Quando as tres forem capturadas,
o programa fecha sozinho e salva em `entregas/`:

| Arquivo | O que e |
|---------|---------|
| `aula01_esquerda.png` | Print da deteccao na zona ESQUERDA |
| `aula01_centro.png` | Print da deteccao na zona CENTRO |
| `aula01_direita.png` | Print da deteccao na zona DIREITA |
| `aula01_classificacao.png` | Painel com as tres lado a lado - **e esta que vai na entrega** |

Se aparecer `INCOMPLETO` e `maior area detectada` vier bem abaixo de 500, a cor nao esta sendo
pega: volte ao passo 3 e calibre.

## 5. Executar o notebook no Jupyter

**De longe o jeito mais facil:** de duplo clique em **`abrir_jupyter.bat`**.

Ele ativa o ambiente, sobe o Jupyter Lab e abre o navegador ja no notebook. A janela preta do
terminal precisa continuar aberta enquanto voce usa o Jupyter - ela **e** o servidor. Para
encerrar no fim, volte nela e pressione `Ctrl+C` duas vezes.

Pelo terminal, se preferir:

```powershell
.\.venv\Scripts\python.exe -m jupyter lab aula01_camera.ipynb
```

No VS Code, abra `aula01_camera.ipynb` e escolha o kernel **Python (LCML .venv)** no canto
superior direito.

Rode as celulas de cima para baixo com `Shift+Enter`, ou use **Run > Run All Cells** para executar
tudo de uma vez. As celulas de camera tem tempo limite e param sozinhas; da para encerrar antes
pressionando **Q** na janela de video.

Antes de rodar os passos 4 e 5, **esteja com o objeto em maos** - o passo 4 dura 12s e o passo 5
dura 20s. Se precisar de mais tempo, aumente o `duracao_s` na propria celula.

Para executar o notebook inteiro sem abrir janelas de video:

```powershell
$env:LCML_AUTO = "1"
.\.venv\Scripts\python.exe -m jupyter nbconvert --to notebook --execute --inplace aula01_camera.ipynb
```

## 5b. Tirar a print do Jupyter rodando

O professor quer ver o notebook **executado dentro do Jupyter**, com as saidas abaixo das celulas.

1. Rode o notebook inteiro (`Run > Run All Cells`) e espere terminar. Os contadores das celulas
   tem que estar numerados em sequencia (`[1]`, `[2]`, `[3]`...) - se aparecer `[ ]` ou `[*]`,
   aquela celula nao rodou ou ainda esta rodando.
2. Role ate um trecho que mostre codigo **e** resultado juntos. Os melhores para a print:
   - o **passo 1**, com a lista de versoes das bibliotecas
   - o **passo 5**, com a imagem da classificacao e os comandos observados
   - o **passo 6**, com as quatro linhas `OK` e `TODOS OS CASOS PASSARAM`
3. Capture com **`Win + Shift + S`** (recorte da tela). A imagem vai para a area de transferencia.
4. Cole no Paint (`Ctrl+V`) e salve em `entregas/` como `jupyter_passo1.png`, `jupyter_passo5.png`,
   `jupyter_passo6.png`.

Deixe a barra de endereco do navegador aparecer na print (`localhost:8888/lab`): e o que prova que
esta rodando no Jupyter, e nao uma imagem colada.

Se quiser tudo em um arquivo so, o Jupyter tambem exporta:
`File > Save and Export Notebook As > HTML`.

## 6. Conferir a entrega

- [ ] Notebook executado, com as saidas salvas (graficos aparecendo nas celulas)
- [ ] Prints do Jupyter rodando, com a barra `localhost:8888` visivel
- [ ] `entregas/aula01_classificacao.png` mostrando ESQUERDA, CENTRO e DIREITA com o objeto real
- [ ] `entregas/aula01_validacao.png` com os quatro casos do teste automatico
- [ ] `README.md` com o problema do grupo preenchido
- [ ] Tudo commitado e enviado ao GitHub

## Problemas comuns

| Sintoma | Causa provavel | O que fazer |
|---------|----------------|-------------|
| `Nao foi possivel abrir a camera` | Outro programa esta usando a webcam | Feche Teams, Meet, Zoom, OBS e navegadores com a camera aberta |
| Camera abre preta | Permissao do Windows | Configuracoes > Privacidade > Camera > permitir apps da area de trabalho |
| `SEM_DETECCAO` o tempo todo | Faixa HSV nao bate com o objeto | Rode `ferramentas/calibrar_cor.py` |
| Deteccao pisca | Pouca luz ou objeto pequeno | Aproxime o objeto, acenda mais luz, ou baixe `AREA_MINIMA` |
| Janela do OpenCV travada | Normal ao fechar pelo X | Feche sempre com **Q** |
| VS Code nao acha o kernel | Extensao Jupyter ausente | Instale `ms-toolsai.jupyter` e recarregue |
