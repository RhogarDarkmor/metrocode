# 🗺️ Roadmap - Futuras Melhorias

> Este documento descreve melhorias planejadas para tornar MetrôCode ainda melhor.
> Perfeito para **iniciantes** que querem contribuir!

## 🎯 Objetivos Principais

### Curto Prazo (v0.2.0 - Próximas 2-3 semanas)

#### 1. **Refatorar app.py** 🏗️
- **Problema**: app.py tem 100 pontos de complexidade (muito grande)
- **Solução**: Quebrar em componentes menores
  - `widgets/` para componentes Textual
  - `exporters/` para PNG, SVG, JSON
  - `cli/` para argumentos de linha de comando
- **Impacto**: Código mais legível e testável

#### 2. **Eliminar Ciclo __init__.py ↔ app.py** 🔄
- **Problema**: Ciclo detectado
- **Causa**: app.py importa do `__init__.py`
- **Solução**: Lazy imports ou reorganizar módulos
- **Aprendizado**: Como evitar ciclos em Python

#### 3. **Melhorar Testes** 🧪
- Adicionar testes de integração para o app completo
- Testes de export (PNG, SVG)
- Testes de CLI
- Meta: > 90% cobertura

#### 4. **Documentação de API** 📚
- Gerar docs com Sphinx
- Deploy no ReadTheDocs
- Adicionar exemplos mais completos

### Médio Prazo (v0.3.0 - 1-2 meses)

#### 1. **Análise de Qualidade Avançada** 📊
```python
def detectar_god_objects(mapa) -> list[str]:
    """Encontra classes gigantes (anti-padrão)"""
    pass

def sugerir_refatoracao_modulo(estacao: Station) -> str:
    """Sugere como quebrar módulo grande"""
    pass

def encontrar_dead_code(mapa) -> list[str]:
    """Encontra imports não usados"""
    pass
```

#### 2. **Visualização Interativa Melhorada** 🎨
- Busca/filtro em tempo real
- Clique para explorar detalhes
- Drag-and-drop para reorganizar
- Tema customizável (claro/escuro)

#### 3. **Exportação para Múltiplos Formatos** 📤
- JSON estruturado
- DOT (Graphviz) - para `dot -Tsvg`
- YAML
- Markdown (relatório)
- HTML interativo

#### 4. **Suporte a Mais Linguagens** 🌍
- TypeScript/JavaScript
- Go
- Rust
- Java

### Longo Prazo (v1.0.0 - 3-6 meses)

#### 1. **Integração com IDEs** 💻
- VS Code Extension
- PyCharm Plugin
- Integração com pre-commit

#### 2. **Dashboard Web** 🌐
- Servidor Flask/FastAPI
- Visualização no browser
- Histórico de análises
- Comparação entre versões

#### 3. **Análise de Performance** ⚡
- Perfil de imports
- Custo de cada import
- Otimizações sugeridas

#### 4. **Machine Learning** 🤖
- Detectar patterns de código
- Sugerir refatorações automáticas
- Classificar arquivos por complexidade

---

## 📋 Features por Dificuldade

### 🟢 Fácil - Bom para Iniciantes

- [ ] Adicionar nova cor de linha no metro
- [ ] Adicionar novo tipo de métrica
- [ ] Melhorar mensagens de erro
- [ ] Adicionar emojis em mais lugares
- [ ] Criar exemplo de projeto de teste

**Tempo**: 30 min - 1h  
**Aprendizado**: Estrutura, tipos, testing

### 🟡 Médio - Para Quem Sabe Python

- [ ] Refatorar app.py em componentes
- [ ] Implementar novo exportador (JSON, YAML)
- [ ] Adicionar caching de grafo
- [ ] Melhorar detecção de ciclos
- [ ] Implementar novo layout (hierarchical)

**Tempo**: 2-4h  
**Aprendizado**: Arquitetura, design patterns, testing avançado

### 🔴 Difícil - Para Experientes

- [ ] Dashboard web (Flask + React)
- [ ] VS Code Extension
- [ ] Suporte a TypeScript/JS
- [ ] ML para detecção de patterns
- [ ] Otimizações de performance

**Tempo**: 8h+  
**Aprendizado**: Web dev, DevOps, ML, extensões IDE

---

## 🚀 Como Começar a Contribuir

### Passo 1: Escolha uma Feature

```bash
# 1. Veja issues marcadas "good first issue"
# 2. Escolha algo do roadmap acima
# 3. Abra uma discussão se tiver dúvidas
```

### Passo 2: Fork e Setup

```bash
git clone https://github.com/SEU_USER/metrocode.git
cd metrocode
poetry install
pre-commit install
```

### Passo 3: Crie uma Branch

```bash
git checkout -b feature/minha-feature
```

### Passo 4: Implemente

```python
# Edite os arquivos necessários
# Adicione testes
# Mantenha > 85% cobertura
```

### Passo 5: Test & Commit

```bash
pytest --cov=metrocode
mypy src/metrocode
pre-commit run --all-files
git commit -m "Adiciona minha feature"
```

### Passo 6: Push & PR

```bash
git push origin feature/minha-feature
# Abra Pull Request no GitHub
```

---

## 📚 Recursos para Aprender

Para contribuir em diferentes áreas:

**AST e Parsing**
- https://docs.python.org/3/library/ast.html
- https://greentreesnakes.readthedocs.io/

**Grafos e Algoritmos**
- https://networkx.org/documentation/
- https://www.coursera.org/learn/algorithms-graphs-data-structures

**Design Patterns**
- https://refactoring.guru/design-patterns/python
- "Clean Code" - Robert Martin

**Testing**
- https://docs.pytest.org/
- "Python Testing with pytest" - Brian Okken

**Web Development**
- https://flask.palletsprojects.com/
- https://react.dev/ (para dashboard)

---

## 💡 Ideias de Projetos de Aprendizado

Use MetrôCode para aprender:

### 1. **Analisar um projeto aberto**
```bash
python -m metrocode psf/flask
# Veja como Flask é estruturado
```

### 2. **Criar seu próprio analisador**
```python
# Use parser.py como referência
# Implemente analisador para Java, Go, etc
```

### 3. **Dashboard web**
```python
# Use analyzer.py para dados
# Crie API Flask
# Frontend React
```

### 4. **Refatorar seu projeto**
```bash
# Analise seu próprio projeto
python -m metrocode meu_projeto
# Use sugestões para melhorar
```

---

## 🎓 Conceitos-Chave para Cada Feature

| Feature | Conceitos | Dificuldade |
|---------|-----------|------------|
| Nova métrica | Análise estatística, loops | 🟢 |
| Novo layout | Algoritmos de grafos, geometria | 🟡 |
| Exportador | File I/O, serialização | 🟡 |
| Dashboard web | Web frameworks, APIs, frontend | 🔴 |
| IDE Extension | APIs da IDE, comunicação IPC | 🔴 |
| ML detection | Sklearn, feature engineering | 🔴 |

---

## 📊 Progresso Atual

```
Core Features
  ✅ Parser com AST
  ✅ Tipos bem definidos
  ✅ Análise básica
  ✅ Cache inteligente
  ✅ Detecção de ciclos
  ⏳ App TUI (em melhoramento)

Testes
  ✅ > 85% cobertura
  ⏳ Testes de integração

Documentação
  ✅ Guias educativos
  ✅ CONTRIBUTING.md
  ✅ API docstrings
  ⏳ ReadTheDocs

DevOps
  ✅ GitHub Actions CI
  ✅ Pre-commit hooks
  ✅ Docker support
  ⏳ Automated releases
```

---

## 🔗 Links Úteis

- **Issues**: https://github.com/RhogarDarkmor/metrocode/issues
- **Discussions**: https://github.com/RhogarDarkmor/metrocode/discussions
- **Project Board**: https://github.com/users/RhogarDarkmor/projects/1
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Development**: [DEVELOPMENT.md](DEVELOPMENT.md)

---

**Quer contribuir? Comece pequeno, aprenda muito! 🚀**
