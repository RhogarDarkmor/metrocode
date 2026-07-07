# 📚 Guia Educativo - MetrôCode

> Um projeto para **iniciantes em programação** entenderem a estrutura e arquitetura de código Python através de uma metáfora visual.

## 🎓 O que você vai aprender

Este projeto é educativo. Enquanto usa o MetrôCode, você aprende sobre:

### 1. **Estrutura de Projeto Python** 📁

Um projeto Python típico é organizado assim:

```
meu_projeto/
├── src/
│   └── meu_modulo/
│       ├── __init__.py    ← Marca como pacote
│       ├── parser.py      ← Módulo
│       └── utils.py       ← Módulo
├── tests/
│   └── test_parser.py     ← Testes
└── pyproject.toml         ← Configuração
```

**Analogia do Metrô:**
- 📁 Pasta = Linha do metrô
- 📄 Arquivo = Estação
- ⚡ Função = Plataforma
- 📦 Classe = Complexo de estações
- 🔗 Import = Trilho conectando estações

### 2. **Tipos e Tipo Checking** 🔍

O MetrôCode usa `dataclasses` para estruturar dados:

```python
from dataclasses import dataclass

@dataclass
class Platform:
    nome: str
    tipo: str
    linha: int
```

**Por que?**
- Clareza: Você sabe exatamente quais dados existem
- Segurança: Menos erros em tempo de execução
- IDE: Autocomplete funciona melhor

### 3. **Abstract Syntax Tree (AST)** 🌳

O módulo `parser.py` usa Python's `ast` para analisar código **com segurança**:

```python
import ast

codigo = "def hello(): print('oi')"
arvore = ast.parse(codigo)

for nodo in ast.walk(arvore):
    if isinstance(nodo, ast.FunctionDef):
        print(f"Encontrei função: {nodo.name}")
```

**Por que AST é importante:**
- ❌ `eval(codigo)` é perigoso (executa código arbitrário)
- ✅ `ast.parse()` apenas analisa (seguro)
- Permite entender estrutura sem executar

### 4. **Grafos e Redes** 🕸️

O MetrôCode constrói um **grafo dirigido** de dependências:

```
parser.py ─→ types.py ─→ analyzer.py
    ↓              ↓
cache.py     graph_builder.py
```

Cada nó = arquivo
Cada aresta = "arquivo A importa de arquivo B"

**Conceitos aprendidos:**
- Nós e arestas
- Componentes conexas
- Detecção de ciclos (imports circulares)

### 5. **Métricas de Código** 📊

MetrôCode calcula métricas educativas:

```
Densidade de imports (acoplamento):
  Baixa (< 1.0) = Módulos independentes ✅
  Alta (> 3.0)  = Muito acoplado ⚠️

Complexidade (Gini):
  0 = Tudo igualmente complexo
  1 = Muito desigual (alguns módulos gigantes)
```

**Por que estudar:**
- Arquitetura limpa necessita baixo acoplamento
- Complexidade deve ser distribuída

### 6. **Cache e Performance** ⚡

ParaProjectos grandes, reparsar tudo é lento. MetrôCode usa:

```python
cache = CacheManager()
mapa = cache.carregar("meu_projeto")  # Fast!

if mapa is None:
    mapa = parse_project("meu_projeto")  # Slow, first time
    cache.salvar(mapa)  # Save for next time
```

**Aprendizado:**
- Trade-off entre memória e velocidade
- Hash para detectar mudanças
- JSON para serialização

### 7. **Padrões de Design** 🏗️

Alguns padrões no MetrôCode:

#### **Dataclass** ✅
```python
@dataclass
class Station:
    nome: str
    modulo: str
    plataformas: list = field(default_factory=list)
```
Ponto de entrada para **imutabilidade** e **clareza**.

#### **Factory Pattern**
```python
def parse_project(path: str) -> MetroMap:
    """Factory: cria objetos complexos (MetroMap)"""
    ...
```

#### **Strategy Pattern**
```python
def calcular_layout(grafo, modo="metro"):
    if modo == "metro":
        return _layout_metro(...)
    elif modo == "geografico":
        return nx.kamada_kawai_layout(...)
```

### 8. **Testing & Coverage** 🧪

Testes são forma de **documentação executável**:

```python
def test_platform_criacao():
    plat = Platform(nome="minha_funcao", tipo="funcao", linha=42)
    assert plat.nome == "minha_funcao"
    # Este teste DOCUMENTA como criar Platform!
```

**Rodando com cobertura:**
```bash
pytest --cov=metrocode tests/
```

Objetivo: > 80% cobertura = código bem testado

### 9. **Logging e Debugging** 🔧

```python
import logging

logger = logging.getLogger(__name__)

logger.info(f"🚇 Analisando projeto: {root}")
logger.warning(f"⚠️  Ciclos detectados: {len(ciclos)}")
logger.debug(f"Ignorando: {arquivo}")
```

**Níveis:**
- DEBUG: Detalhes de diagnóstico (muito barulho)
- INFO: Informações normais de execução
- WARNING: Algo suspeito
- ERROR: Erro que pode ser recuperado
- CRITICAL: Falha fatal

### 10. **Type Hints e Mypy** 🏆

```python
def parse_project(root_path: str | Path | None = ".") -> MetroMap:
    """Type hints para IDE e static analysis."""
    ...
```

**Mypy verifica tipos sem executar:**
```bash
mypy src/metrocode
```

## 🚀 Exercícios para Praticar

### Exercício 1: Adicione uma nova métrica
Edite `analyzer.py` e adicione uma função que conta linhas de código totais:

```python
def contar_linhas_totais(mapa: MetroMap) -> int:
    """Soma linhas de código de todos os arquivos."""
    ...
```

### Exercício 2: Detecte um novo padrão
Estenda `analyzer.py` para detectar "orphan files" (arquivos que ninguém importa):

```python
def encontrar_orfaos(mapa: MetroMap) -> list[str]:
    """Encontra arquivos que ninguém importa."""
    ...
```

### Exercício 3: Novo modo de layout
Adicione em `layout_engine.py` um layout "hierárquico":

```python
def _layout_hierarquico(grafo, estacoes, plataformas):
    """Disposição em árvore (root → children)."""
    ...
```

## 🏛️ Arquitetura do MetrôCode

```
┌─────────────────────────────────────────────────┐
│              Aplicação (app.py)                  │
│        Interface Textual (Textual TUI)          │
└────────────┬────────────────────────────────────┘
             │
     ┌───────┴────────────┐
     │                    │
┌────▼─────────┐  ┌──────▼─────────┐
│ Graph Builder │  │ Layout Engine  │
│  (grafo)      │  │ (posições)     │
└────┬─────────┘  └──────┬─────────┘
     │                   │
     └───────────┬───────┘
                 │
         ┌───────▼────────┐
         │ Parser (tipos) │
         │  + Analyzer    │
         └───────┬────────┘
                 │
         ┌───────▼────────┐
         │ Cache Manager  │
         │  + Tipos       │
         └────────────────┘
```

## 💡 Conceitos-Chave para Iniciantes

### **Modularidade**
Código dividido em módulos pequenos, cada um faz UMA coisa bem.

### **Single Responsibility**
`parser.py` só faz parsing, `analyzer.py` só analisa, etc.

### **Dependency Inversion**
Altinha nível não depende de baixo nível:
```python
# ❌ Ruim
class Parser:
    def __init__(self):
        self.cache = CacheManager()  # Acoplado!

# ✅ Bom
class Parser:
    def __init__(self, cache: CacheManager = None):
        self.cache = cache or CacheManager()
```

### **Interface Segregation**
Use tipos específicos, não dicts genéricos:
```python
# ❌ Ruim
def analisa(dados: dict[str, Any]) -> dict[str, Any]:
    ...

# ✅ Bom
def analisa(mapa: MetroMap) -> list[str]:
    ...
```

## 📖 Recursos para Aprender Mais

- **AST**: https://docs.python.org/3/library/ast.html
- **NetworkX**: https://networkx.org/documentation/
- **Dataclasses**: https://docs.python.org/3/library/dataclasses.html
- **Type Hints**: https://peps.python.org/pep-0484/
- **Mypy**: http://mypy-lang.org/

## 🎯 Próximos Passos

1. **Rodee o projeto:** `python -m metrocode src/metrocode`
2. **Estude um módulo:** Comece por `types.py`
3. **Execute testes:** `pytest -v`
4. **Modifique algo:** Adicione sua própria métrica!
5. **Contribute:** Envie suas melhorias!

---

**Lembre-se:** Código é para humans ler, não máquinas executar. 🚀
