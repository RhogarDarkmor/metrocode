# 🚀 Setup e Desenvolvimento

Guia completo para configurar o ambiente de desenvolvimento do MetrôCode.

## Pré-requisitos

- Python 3.11+
- Git
- Poetry (gerenciador de dependências Python)

## 1️⃣ Instalação Inicial

### Clonar o repositório
```bash
git clone https://github.com/RhogarDarkmor/metrocode.git
cd metrocode
```

### Instalar Poetry (se não tiver)
```bash
curl -sSL https://install.python-poetry.org | python3 -
# ou
pip install poetry
```

### Criar environment virtual e instalar dependências
```bash
poetry install
```

Isso cria um `.venv` local com todas as dependências.

### Ativar o environment
```bash
# Windows
.\.venv\Scripts\activate
# ou
poetry shell

# Linux/macOS
source .venv/bin/activate
```

## 2️⃣ Configurar Pre-commit Hooks

Pre-commit hooks rodam **automaticamente** antes de cada commit para:
- Formatar código (Black)
- Organizar imports (isort)
- Lint (Ruff)
- Verificar tipos (Mypy)

```bash
pre-commit install
```

Agora, ao fazer `git commit`, os hooks rodam automaticamente!

Para rodar manualmente:
```bash
pre-commit run --all-files
```

## 3️⃣ Rodando Testes

### Rodar todos os testes
```bash
pytest
```

### Rodar com verbose
```bash
pytest -v
```

### Rodar com cobertura
```bash
pytest --cov=metrocode --cov-report=html
```

Abre um relatório HTML em `htmlcov/index.html`.

### Rodar um arquivo específico
```bash
pytest tests/test_types_and_analysis.py
```

### Rodar um teste específico
```bash
pytest tests/test_types_and_analysis.py::TestParser::test_module_name_from_path
```

## 4️⃣ Verificar Tipos com Mypy

```bash
mypy src/metrocode
```

Ou para ser mais rigoroso:
```bash
mypy src/metrocode --strict
```

## 5️⃣ Formatar e Lint

### Black (formatter)
```bash
black src/metrocode tests/
```

### isort (imports)
```bash
isort src/metrocode tests/
```

### Ruff (linter)
```bash
ruff check src/metrocode tests/
ruff check --fix src/metrocode tests/  # Auto-fix
```

## 6️⃣ Rodando o MetrôCode

### Analisar o próprio código do MetrôCode
```bash
python -m metrocode src/metrocode
```

### Analisar outro projeto
```bash
python -m metrocode /path/to/project
```

### Analisar repositório GitHub
```bash
python -m metrocode psf/requests
```

### Exportar mapa
```bash
python -m metrocode src/metrocode --export metro_map.png --format=png
```

## 7️⃣ Desenvolvimento Passo a Passo

### 1. Criar branch para sua feature
```bash
git checkout -b feature/minha-feature
```

### 2. Fazer alterações
```bash
# Edite os arquivos que quiser
vim src/metrocode/analyzer.py
```

### 3. Testes
```bash
pytest -v
```

### 4. Type check
```bash
mypy src/metrocode
```

### 5. Commit
```bash
git add .
git commit -m "Adiciona minha feature"
# Pre-commit hooks rodam automaticamente!
```

### 6. Push
```bash
git push origin feature/minha-feature
```

### 7. Pull Request
Abra no GitHub!

## 📊 CI/CD

O projeto tem **GitHub Actions** que rodam automaticamente:

1. **Tests** - Executa `pytest`
2. **Lint** - Verifica `ruff`, `black`, `isort`
3. **Type Check** - Verifica com `mypy`
4. **Coverage** - Garante cobertura > 80%

Veja em `.github/workflows/python-ci.yml`.

## 🐛 Debugging

### Logging
O MetrôCode usa logging. Para ver mensagens de debug:

```bash
PYTHONPATH=src python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from metrocode import parse_project
mapa = parse_project('.')
"
```

### IPython para exploração
```bash
pip install ipython
ipython
```

Dentro do IPython:
```python
from metrocode.parser import parse_project
mapa = parse_project(".")
mapa.estacoes.keys()  # Ver todas as estações
```

### VS Code Debug

Crie `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: MetrôCode",
            "type": "python",
            "request": "launch",
            "module": "metrocode.app",
            "console": "integratedTerminal"
        }
    ]
}
```

Pressione `F5` para debugar!

## 📚 Estrutura do Projeto

```
metrocode/
├── src/metrocode/
│   ├── __init__.py        # Entry point
│   ├── types.py           # 📦 Tipos e modelos
│   ├── parser.py          # 🔍 Parse de código
│   ├── analyzer.py        # 📊 Análise avançada
│   ├── cache.py           # 💾 Cache de análises
│   ├── graph_builder.py   # 🕸️ Constrói grafo
│   ├── layout_engine.py   # 📐 Layout/posições
│   └── app.py             # 🎨 Interface (Textual)
├── tests/
│   ├── test_types_and_analysis.py  # 🧪 Testes principais
│   ├── test_app.py                 # 🧪 Testes UI
│   └── test_repo_input.py          # 🧪 Testes de input
├── pyproject.toml         # 📋 Dependências e config
├── .pre-commit-config.yaml  # ⚙️ Git hooks
├── CONTRIBUTING.md        # 📚 Guia educativo
└── DEVELOPMENT.md         # 📚 Este arquivo
```

## 🎓 Conceitos para Aprender

Enquanto desenvolve, você aprende:

1. **Types e Dataclasses** - Como estruturar dados
2. **AST** - Como analisar código Python
3. **Grafos** - NetworkX, algoritmos
4. **Testing** - Pytest, fixtures, cobertura
5. **Type Checking** - Mypy, type hints
6. **Git** - Workflows profissionais
7. **CI/CD** - GitHub Actions automation

## 🚀 Contribuindo

1. Fork o repositório
2. Crie um branch (`git checkout -b feature/xyz`)
3. Commit changes (`git commit -am 'Add feature'`)
4. Push to branch (`git push origin feature/xyz`)
5. Open Pull Request

## 📞 Suporte

- Issues: GitHub Issues
- Discussions: GitHub Discussions
- Email: author@example.com

---

**Happy coding!** 🚇✨
