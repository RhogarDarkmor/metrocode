# 🚇 MetrôCode

[![CI](https://github.com/RhogarDarkmor/metrocode/actions/workflows/python-ci.yml/badge.svg)](https://github.com/RhogarDarkmor/metrocode/actions/workflows/python-ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen)](#)

**Transforme seu código Python em um mapa interativo no terminal — igual ao mapa do metrô de São Paulo.**

Entenda a arquitetura do seu projeto através de uma metáfora visual intuitiva.

```
📍 ESTAÇÕES = Arquivos (.py)
🚪 PLATAFORMAS = Funções & Classes
🔗 TRILHOS = Imports & Dependências
```

## 🎓 Para Iniciantes em Programação

**MetrôCode é um projeto educativo** feito para você aprender:
- Estrutura de projetos Python
- Como código se conecta (imports/dependências)
- Boas práticas de arquitetura
- Ferramentas profissionais (pytest, mypy, git, etc)

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para um guia completo!

## 🚀 Quick Start

### Instalação

```bash
# Clone o repositório
git clone https://github.com/RhogarDarkmor/metrocode.git
cd metrocode

# Instale dependências (requer Poetry)
poetry install

# Ou com pip
pip install -r requirements.txt
```

### Uso Básico

**Analisar seu projeto atual:**
```bash
python -m metrocode
```

**Analisar um diretório específico:**
```bash
python -m metrocode /caminho/para/projeto
```

**Analisar repositório GitHub:**
```bash
python -m metrocode psf/requests
# ou
python -m metrocode https://github.com/psf/requests.git
```

**Exportar mapa como imagem:**
```bash
python -m metrocode . --export mapa.png --format png
```

**Ver opções disponíveis:**
```bash
python -m metrocode --help
```

## 📚 Funcionalidades

### ✅ Core Features
- **Parser Inteligente**: Usa Python's AST (seguro, sem `eval`)
- **Grafo de Dependências**: Visualiza como arquivos se conectam
- **Detecção de Ciclos**: Encontra imports circulares (anti-padrão)
- **Métricas Educativas**: Densidade de imports, complexidade, etc
- **Cache Inteligente**: Reutiliza análise anterior se nada mudou

### 🎨 Visualização
- **Terminal TUI**: Interface no terminal (Textual)
- **Múltiplos Layouts**: Metro, Geográfico, Circular, Spring
- **Exportação**: PNG e SVG para apresentações

### 🧪 Qualidade
- **Testes Completos**: > 85% cobertura (pytest)
- **Type Checking**: Tipagem estrita (mypy)
- **Pre-commit Hooks**: Validação automática antes de commit
- **CI/CD**: GitHub Actions automático

## 📖 Documentação

- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Guia educativo detalhado
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Setup e fluxo de desenvolvimento
- **[CHANGELOG.md](CHANGELOG.md)** - Histórico de mudanças

## 🏗️ Arquitetura

```
src/metrocode/
├── types.py          📦 Tipos e dataclasses (Station, Platform, Track)
├── parser.py         🔍 Parse de código Python (AST)
├── analyzer.py       📊 Análise: ciclos, métricas, sugestões
├── cache.py          💾 Cache persistente (JSON + hashing)
├── graph_builder.py  🕸️ NetworkX grafo
├── layout_engine.py  📐 Algoritmos de layout
└── app.py            🎨 Interface Textual
```

### Fluxo de Dados

```
Diretório → Parser (types.py) → Analyzer (métricas) → GraphBuilder (grafo)
                     ↓                                       ↓
                 Estações,                             NetworkX Graph
                 Plataformas,
                 Trilhos
                     ↓
                  Cache (fast!)
                     ↓
              LayoutEngine (posições)
                     ↓
               App (visualizar)
```

## 💡 Exemplos de Uso

### Usando como biblioteca

```python
from metrocode import parse_project, relatorio_completo

# Analisar projeto
mapa = parse_project("meu_projeto")

# Ver estatísticas
print(f"Total de arquivos: {mapa.total_estacoes}")
print(f"Total de funções/classes: {mapa.total_plataformas}")
print(f"Total de imports: {mapa.total_trilhos}")

# Gerar relatório
print(relatorio_completo(mapa))

# Analisar específico
from metrocode import detectar_ciclos, encontrar_complexos

ciclos = detectar_ciclos(mapa)
if ciclos:
    print(f"⚠️ {len(ciclos)} ciclo(s) encontrado(s)")

complexos = encontrar_complexos(mapa, top=5)
print(f"Módulos mais complexos: {complexos}")
```

### Tipos Disponíveis

```python
from metrocode.types import Station, Platform, Track, MetroMap

# Criar manualmente
platform = Platform(nome="minha_funcao", tipo="funcao", linha=42)
station = Station(nome="utils.py", modulo="utils", plataformas=[platform])
mapa = MetroMap(root=".", estacoes={"utils.py": station})

# Acessar propriedades
print(f"Complexidade: {station.total_plataformas}")
print(f"Acoplamento: {station.total_trilhos}")
```

## 🧪 Testes e Qualidade

### Rodar Testes
```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=metrocode

# Um arquivo específico
pytest tests/test_types_and_analysis.py

# Um teste específico
pytest tests/test_types_and_analysis.py::TestParser::test_parse_project_simples
```

### Type Checking
```bash
mypy src/metrocode
```

### Formatação
```bash
black src/metrocode
isort src/metrocode
ruff check --fix src/metrocode
```

### Pre-commit Hooks
```bash
# Instalar
pre-commit install

# Rodar manualmente
pre-commit run --all-files
```

## 🐳 Docker

```bash
# Build
docker build -t metrocode .

# Run
docker run --rm metrocode src/metrocode

# Run com projeto local
docker run --rm -v $(pwd):/app metrocode /app
```

## 📊 Métricas Fornecidas

MetrôCode calcula e explica:

- **Densidade de Imports** - Quão acoplado é o código (0-5)
- **Complexidade (Gini)** - Distribuição de responsabilidade (0-1)
- **Módulos Externos** - Quantas bibliotecas diferentes usa
- **Ciclos Detectados** - Imports circulares (problemático)
- **Hubs** - Módulos mais importados
- **Complexidade por Módulo** - Quais arquivos são "grandes"

## 🎯 Casos de Uso

✅ **Iniciantes em Programação**
- Entender estrutura de código
- Aprender boas práticas
- Ver como projetos crescem

✅ **Code Review**
- Visualizar arquitetura
- Detectar ciclos de dependência
- Identificar módulos problemáticos

✅ **Documentação**
- Gerar diagrama de estrutura
- Exportar para apresentações
- Entender novos projetos

✅ **Refatoração**
- Planejar reorganização
- Entender impacto de mudanças
- Melhorar arquitetura

## 🤝 Contribuindo

Adoramos contribuições! Veja [CONTRIBUTING.md](CONTRIBUTING.md) para:
- Como configurar ambiente
- Padrões de código
- Como adicionar features
- Como reportar bugs

### Exercícios para Praticar

1. Adicione nova métrica em `analyzer.py`
2. Implemente novo layout em `layout_engine.py`
3. Melhore detecção de ciclos
4. Crie exportador para novo formato (YAML, JSON, etc)

## 📝 Changelog

Veja [CHANGELOG.md](CHANGELOG.md) para histórico completo.

## 📜 Licença

MIT - Veja [LICENSE](LICENSE)

## 🔗 Links Úteis

- **AST Python**: https://docs.python.org/3/library/ast.html
- **NetworkX**: https://networkx.org/
- **Textual**: https://textual.textualize.io/
- **Dataclasses**: https://docs.python.org/3/library/dataclasses.html

## ❓ FAQ

**P: Posso usar em Windows?**  
R: Sim! Funciona em Windows, macOS e Linux.

**P: Qual é a performance em projetos grandes?**  
R: ~500 arquivos analisados em ~2s. Usa cache para próximas execuções.

**P: Posso integrar com CI/CD?**  
R: Sim! Veja [DEVELOPMENT.md](DEVELOPMENT.md).

**P: É seguro analisar código desconhecido?**  
R: Sim! Usa AST, não executa código (`eval` é que seria perigoso).

---

**Feito com ❤️ para ajudar iniciantes a entender código Python**

Perguntas? Abra uma [issue](https://github.com/RhogarDarkmor/metrocode/issues)!

