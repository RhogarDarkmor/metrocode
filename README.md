# MetroCode

MetroCode é um aplicativo desktop em Python que analisa um projeto em Python selecionado pelo usuário e transforma a estrutura de funções e chamadas em um mapa visual tipo “rede de metrô”. A ideia é representar funções como estações e as relações entre elas como conexões, facilitando a compreensão do fluxo de um código.

## O que o projeto faz

O aplicativo realiza as seguintes etapas:

1. Abre uma janela de seleção de pasta para o usuário.
2. Percorre os arquivos `.py` do projeto escolhido.
3. Usa o módulo `ast` do Python para analisar o código.
4. Extrai informações como:
   - funções e métodos
   - docstrings
   - imports
   - chamadas entre funções
5. Monta um grafo visual com nós (estações) e arestas (conexões).
6. Exibe o resultado em uma janela web embutida usando `webview`.

## Objetivo

O projeto serve como uma ferramenta visual para entender rapidamente:

- quais funções existem no projeto
- como elas se relacionam
- quais módulos ou arquivos estão mais conectados
- onde a lógica do sistema está concentrada

## Tecnologias utilizadas

- Python
- `ast` para parsing de código fonte
- `tkinter` para seleção de pasta
- `webview` para exibir a interface em uma janela desktop
- HTML/CSS/JavaScript para renderização do mapa
- D3.js (presente em uma versão alternativa da interface em `templates/index.html`)

## Estrutura do projeto

- `main.py` — ponto de entrada da aplicação. Controla a execução principal, escolhe a pasta do projeto e gera a visualização.
- `parser/python_parser.py` — responsável por percorrer os arquivos Python e extrair funções, imports, chamadas e docstrings.
- `graph/metro_graph.py` — responsável por transformar os dados extraídos em um grafo visual com estações e conexões.
- `templates/index.html` — modelo alternativo/experimental de interface para renderização do mapa.

## Como executar

### 1. Ativar o ambiente virtual

No Windows, em PowerShell:

```powershell
cd C:\Users\rhoga\MetroCode
.\venv\Scripts\Activate.ps1
```

Se o PowerShell bloquear a ativação, execute:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

### 2. Instalar dependências

Se ainda não estiverem instaladas:

```powershell
python -m pip install pywebview
```

### 3. Rodar o projeto

```powershell
python main.py
```

## Fluxo de uso

1. O programa abre uma janela para você selecionar uma pasta com um projeto Python.
2. O sistema analisa os arquivos `.py` dentro dessa pasta.
3. O mapa é montado automaticamente.
4. Uma janela com o mapa é aberta.

## Como interpretar o resultado

- Cada nó/estação representa uma função ou método encontrado no código.
- Cada conexão representa uma relação de chamada entre funções.
- Cores diferentes podem indicar arquivos ou grupos diferentes.
- Ao passar o mouse sobre uma estação, é possível ver o resumo/docstring associado.

## Limitações atuais

Este projeto é uma implementação inicial e possui algumas limitações importantes:

- A análise é baseada em parsing estático com `ast`, então não resolve completamente cenários dinâmicos.
- Importações muito indiretas, metaprogramação e chamadas geradas dinamicamente podem não ser detectadas corretamente.
- A interface é simples e tem foco em demonstrar a ideia do mapa visual.
- O projeto depende de uma estrutura de código bem formada para funcionar corretamente.

## Possíveis problemas e solução

### Erro de sintaxe ao iniciar

Se o programa não subir, verifique se os arquivos principais não foram alterados acidentalmente com texto inválido ou caracteres estranhos.

### Biblioteca ausente

Se aparecer erro relacionado a `webview`, instale novamente:

```powershell
python -m pip install pywebview
```

### Pasta não selecionada

Se você fechar a janela de seleção de pasta, o programa encerra sem continuar.

## Próximos passos possíveis

Algumas melhorias que podem ser feitas no futuro:

- melhorar a detecção de relações entre funções
- adicionar suporte a classes e métodos com melhor organização visual
- incluir filtros por arquivo, módulo ou nível de profundidade
- criar uma interface mais interativa e responsiva
- exportar o grafo para JSON, SVG ou imagem

## Resumo

MetroCode é um protótipo de visualização de projetos Python como um mapa interativo de funções e dependências. Ele transforma código estático em uma representação visual intuitiva, facilitando a exploração de projetos maiores.
