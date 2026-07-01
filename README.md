# 🚇 MetrôCode

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