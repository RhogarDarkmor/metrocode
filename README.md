# 🚇 MetrôCode

[![CI](https://github.com/RhogarDarkmor/metrocode/actions/workflows/python-ci.yml/badge.svg)](https://github.com/RhogarDarkmor/metrocode/actions/workflows/python-ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**Transforme seu código Python em um mapa interativo no terminal — igual ao mapa do metrô de São Paulo.**

- Arquivos são estações
- Funções e classes são baldeações
- Imports são as linhas conectando tudo

> Projeto em construção. Primeira estação: app rodando com Textual.

## Como usar

Executar localmente (analisa a pasta atual):

```bash
./.venv/Scripts/python.exe -m metrocode.app
```

Analisar um repositório GitHub pelo link:

```bash
./.venv/Scripts/python.exe -m metrocode.app https://github.com/owner/repo.git
```

Ou usar o atalho `owner/repo` (ex: `psf/requests`):

```bash
./.venv/Scripts/python.exe -m metrocode.app psf/requests
```

Exportar imagem do mapa (requer `matplotlib`):

```bash
./.venv/Scripts/python.exe -m metrocode.app /caminho/para/projeto --export out.png --format=png
```

Observação: é necessário ter o `git` instalado para clonar repositórios remotos.

Exemplos com verbosidade e sem limpeza de temporários:

```bash
./.venv/Scripts/python.exe -m metrocode.app psf/requests -v
./.venv/Scripts/python.exe -m metrocode.app https://github.com/owner/repo.git --no-clean -vv
```

## Integração contínua e build

- O projeto já inclui um workflow GitHub Actions em `.github/workflows/python-ci.yml`.
- Ele roda testes com `pytest`, faz lint com `ruff` e constrói o pacote com `poetry build`.

## Docker

Construir a imagem:

```bash
docker build -t metrocode .
```

Executar o app dentro do container:

```bash
docker run --rm metrocode
```

## Changelog

Veja `CHANGELOG.md` para o histórico e as melhorias planejadas.


## Integração contínua e build

- O projeto já inclui um workflow GitHub Actions em `.github/workflows/python-ci.yml`.
- Ele roda testes com `pytest`, faz lint com `ruff` e constrói o pacote com `poetry build`.

## Docker

Construir a imagem:

```bash
docker build -t metrocode .
```

Executar o app dentro do container:

```bash
docker run --rm metrocode
```

## Changelog

Veja `CHANGELOG.md` para o histórico e as melhorias planejadas.
