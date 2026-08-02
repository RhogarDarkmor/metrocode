# 🚇 MetroCode – Visualize seu código como um mapa de metrô

## 🤔 O que é isso?

**MetroCode** é uma ferramenta que transforma projetos Python em um **mapa interativo**, parecido com um mapa de metrô.

- Cada **estação** = uma **função** ou **método**
- Cada **linha** = uma **chamada** entre elas

Com ele, você pode entender rapidamente como o código se organiza, quais partes são mais conectadas e por onde começar a explorar um sistema novo ou esquecido.

---

## 🧠 Por que eu criei o MetroCode?

Quando comecei a programar, uma das maiores dificuldades era entender projetos que não eram meus. Os arquivos se espalhavam, as funções se chamavam de formas confusas, e eu passava horas tentando descobrir "por onde começar".

Pensei: **"E se fosse possível ver o código como um mapa?"**

Foi assim que nasceu o MetroCode: uma forma visual e intuitiva de enxergar a estrutura interna de qualquer projeto Python.

---

## 📜 Como o projeto evoluiu

### 🚧 Versão 0.1 – A primeira ideia (CLI)
A primeira versão funcionava no **terminal**. Você digitava um comando e ele gerava uma imagem mostrando quais **arquivos** importavam outros arquivos.

**O que ela fazia:**
- Mostrava a arquitetura geral do projeto
- Detectava importes circulares
- Gerava imagens PNG/SVG

**O que faltava:**
- Não mostrava o que acontecia *dentro* de cada arquivo
- Não era interativa
- Precisava de conhecimentos de terminal para usar

---

### 🚀 Versão 1.0 Beta – A virada (Desktop)

Esta é a versão atual. Ela é um **aplicativo com janela gráfica**, muito mais fácil de usar.

**O que mudou:**
| Antes | Agora |
|-------|-------|
| Linha de comando | Interface com janela (clique e escolha a pasta) |
| Mostrava arquivos e imports | Mostra funções e chamadas internas |
| Imagem estática | Mapa interativo (zoom, arraste, clique) |
| Foco em arquitetura externa | Foco em fluxo interno de execução |

**O que foi removido:**
- Comandos de terminal
- Análise de arquivos (agora analisa funções)
- Exportação para imagem (a visualização é apenas na tela)

**O que foi adicionado:**
- 🖥️ Interface desktop nativa
- 🔍 Análise profunda de funções, métodos e chamadas
- 🗺️ Visualização D3.js interativa
- 🧩 Código organizado em módulos (parser, graph, templates)

---

## 🎯 O que você pode fazer com o MetroCode 1.0 Beta?

- 📂 Selecionar qualquer pasta com código Python
- 🧠 Ver um mapa de todas as funções e como elas se chamam
- 🔎 Clicar em qualquer estação para ver detalhes (docstring, parâmetros)
- 🧭 Navegar pelo grafo para entender o fluxo do sistema
- 👥 Usar como ferramenta de estudo, onboarding ou refatoração

---

## 🚀 Como usar (simples)

1. **Baixe o projeto:**
   ```bash
   git clone https://github.com/RhogarDarkmor/metrocode.git
   cd metrocode
