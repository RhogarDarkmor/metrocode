"""
MetrôCode - Parser de código Python.

Este módulo analisa arquivos Python e extrai sua estrutura:
- Arquivos → Estações (📍)
- Funções e classes → Plataformas (🚪)
- Imports → Trilhos (🔗)

O resultado é um MetroMap que pode ser visualizado como um mapa de metrô.

Educativo:
- Mostra como usar o módulo `ast` para analisar código Python
- Demonstra como resolver imports relativos
- Ensina sobre AST (Abstract Syntax Tree)
"""

from __future__ import annotations

import ast
import logging
from pathlib import Path
from typing import Any

from .analyzer import detectar_ciclos
from .cache import CacheManager
from .types import MetroMap, Platform, Station, Track

logger = logging.getLogger(__name__)

# Tipos de nó AST que representam funções
AST_FUNCTION_TYPES = (ast.FunctionDef, ast.AsyncFunctionDef)

# Pastas que devem ser ignoradas durante análise
PASTAS_IGNORADAS = {
    "__pycache__",
    "venv",
    ".venv",
    "env",
    ".env",
    "node_modules",
    ".git",
    ".idea",
    ".vscode",
    "dist",
    "build",
    ".mypy_cache",
    ".pytest_cache",
    ".tox",
    "eggs",
    ".eggs",
}


def _is_ignored_path(caminho: Path) -> bool:
    """
    Verifica se um caminho deve ser ignorado durante análise.

    Ignora pastas comuns de venv, cache, git, etc.

    Args:
        caminho: Path do arquivo a verificar

    Returns:
        True se deve ser ignorado, False caso contrário
    """
    return any(pasta in caminho.parts for pasta in PASTAS_IGNORADAS)


def _module_name_from_path(caminho: Path, root: Path) -> str:
    """
    Converte um caminho de arquivo para um nome de módulo Python.

    Exemplos:
        src/metrocode/parser.py → metrocode.parser
        src/metrocode/__init__.py → metrocode
        utils.py → utils

    Args:
        caminho: Path absoluto do arquivo
        root: Diretório raiz do projeto

    Returns:
        Nome do módulo em notação Python (pontos)
    """
    relativo = caminho.relative_to(root).as_posix()

    # __init__.py não tem nome, representa o pacote
    if relativo == "__init__.py":
        return ""

    # Remover __init__.py do caminho
    if relativo.endswith("/__init__.py"):
        relativo = relativo[: -len("/__init__.py")]
    # Remover extensão .py
    elif relativo.endswith(".py"):
        relativo = relativo[: -len(".py")]

    # Converter / em .
    return relativo.replace("/", ".")


def _resolve_relative_import(
    module: str | None, level: int, current_module: str
) -> str:
    """
    Resolve imports relativos.

    Educativo: Ensina como Python resolve coisas como:
    - from . import foo       (nível 1)
    - from .. import bar     (nível 2)
    - from ...module import baz (nível 3)

    Args:
        module: Nome do módulo (None para "from . import")
        level: Nível de relatividade (1 = ., 2 = .., etc)
        current_module: Nome do módulo atual

    Returns:
        Nome do módulo resolvido em forma absoluta

    Exemplo:
        Se estou em "metrocode.parser" e faço "from . import types":
        → resolve para "metrocode.types"
    """
    current_parts = current_module.split(".") if current_module else []

    # Remover o último componente (o próprio módulo)
    if current_parts:
        current_parts = current_parts[:-1]

    # Ir "para cima" conforme o nível de relatividade
    parent_parts = current_parts[: max(len(current_parts) - level + 1, 0)]

    if module:
        if parent_parts:
            return ".".join([*parent_parts, *module.split(".")])
        return module

    return ".".join(parent_parts)


def _extrair_docstring(nodo: ast.AST) -> str | None:
    """
    Extrai docstring de um nó AST.

    Educativo: Mostra como extrair e documentar automaticamente.

    Args:
        nodo: Nó AST (função, classe, etc)

    Returns:
        Docstring se existir, None caso contrário
    """
    return ast.get_docstring(nodo)


def _extrair_plataformas(arvore: ast.AST) -> list[Platform]:
    """
    Extrai todas as funções e classes de um arquivo.

    Args:
        arvore: AST do arquivo

    Returns:
        Lista de Platform (funções e classes)
    """
    plataformas: list[Platform] = []

    for nodo in ast.walk(arvore):
        # Funções e funções assíncronas
        if isinstance(nodo, AST_FUNCTION_TYPES):
            plataformas.append(
                Platform(
                    nome=nodo.name,
                    tipo="funcao",  # type: ignore
                    linha=nodo.lineno,
                    doc=_extrair_docstring(nodo),
                )
            )

        # Classes
        elif isinstance(nodo, ast.ClassDef):
            # Extrair métodos
            metodos: list[Platform] = []
            for item in nodo.body:
                if isinstance(item, AST_FUNCTION_TYPES):
                    metodos.append(
                        Platform(
                            nome=item.name,
                            tipo="metodo",  # type: ignore
                            linha=item.lineno,
                            doc=_extrair_docstring(item),
                        )
                    )

            plataformas.append(
                Platform(
                    nome=nodo.name,
                    tipo="classe",  # type: ignore
                    linha=nodo.lineno,
                    metodos=metodos,
                    doc=_extrair_docstring(nodo),
                )
            )

    return plataformas


def _extrair_trilhos(arvore: ast.AST, modulo_atual: str) -> list[Track]:
    """
    Extrai todos os imports de um arquivo.

    Args:
        arvore: AST do arquivo
        modulo_atual: Nome do módulo atual (para resolver imports relativos)

    Returns:
        Lista de Track (imports)
    """
    trilhos: list[Track] = []

    for nodo in ast.walk(arvore):
        # import foo, import foo as bar
        if isinstance(nodo, ast.Import):
            for alias in nodo.names:
                trilhos.append(
                    Track(
                        tipo="import",  # type: ignore
                        modulo=alias.name,
                        alias=alias.asname,
                        qualificado=alias.name,
                    )
                )

        # from foo import bar, from . import baz
        elif isinstance(nodo, ast.ImportFrom):
            # Resolver módulo (pode ser relativo)
            resolved_module = _resolve_relative_import(
                nodo.module, nodo.level, modulo_atual
            )

            for alias in nodo.names:
                # Determinar o nome qualificado
                if alias.name == "*":
                    qualificado = resolved_module or "*"
                elif resolved_module:
                    qualificado = f"{resolved_module}.{alias.name}"
                else:
                    qualificado = alias.name

                trilhos.append(
                    Track(
                        tipo="import_from",  # type: ignore
                        modulo=resolved_module,
                        nome=alias.name,
                        alias=alias.asname,
                        qualificado=qualificado,
                        nivel=nodo.level,
                    )
                )

    return trilhos



def parse_project(
    root_path: str | Path | None = ".",
    usar_cache: bool = True,
    ignorar_cache: bool = False,
) -> MetroMap:
    """
    Analisa um projeto Python e retorna seu mapa de estrutura.

    Este é o ponto de entrada principal do MetrôCode. Ele:
    1. Percorre recursivamente o diretório em busca de arquivos .py
    2. Parse cada arquivo usando o módulo `ast`
    3. Extrai funções, classes, imports
    4. Constrói um grafo representando a estrutura
    5. Detecta ciclos de dependência

    Args:
        root_path: Diretório do projeto (padrão: diretório atual)
        usar_cache: Se deve tentar usar cache (mais rápido)
        ignorar_cache: Se deve ignorar cache existente

    Returns:
        MetroMap contendo toda a estrutura analisada

    Educativo:
        Este é o primeiro passo para entender o código:
        - Lê todos os arquivos Python
        - Usa AST para análise segura (não usa eval!)
        - Identifica estruturas (classes, funções, imports)
        - Torna visuável a arquitetura

    Exemplo:
        >>> mapa = parse_project("meu_projeto")
        >>> print(f"Total de arquivos: {mapa.total_estacoes}")
        >>> print(f"Total de funções/classes: {mapa.total_plataformas}")
    """
    root = Path(root_path or ".").resolve()

    if not root.exists():
        logger.warning(f"Diretório não encontrado: {root}")
        return MetroMap(root=root)

    # Tentar carregar do cache
    if usar_cache:
        cache_manager = CacheManager()
        mapa_cache = cache_manager.carregar(root, ignorar_cache=ignorar_cache)
        if mapa_cache is not None:
            logger.info(f"✅ Mapa carregado do cache: {root}")
            return mapa_cache

    logger.info(f"🚇 Analisando projeto: {root}")

    mapa = MetroMap(root=root)

    # Encontrar todos os arquivos .py
    arquivo_count = 0
    for caminho_atual in sorted(root.rglob("*.py")):
        if not caminho_atual.is_file():
            continue

        if _is_ignored_path(caminho_atual):
            logger.debug(f"Ignorando: {caminho_atual}")
            continue

        arquivo_count += 1

        try:
            # Parse do arquivo
            conteudo = caminho_atual.read_text(encoding="utf-8")
            arvore = ast.parse(conteudo, filename=str(caminho_atual))
        except (SyntaxError, UnicodeDecodeError, OSError) as e:
            logger.debug(f"Erro ao parsear {caminho_atual}: {e}")
            continue

        # Extrair informações
        modulo_atual = _module_name_from_path(caminho_atual, root)
        plataformas = _extrair_plataformas(arvore)
        trilhos = _extrair_trilhos(arvore, modulo_atual)

        # Nome da estação (path relativo)
        nome_estacao = caminho_atual.relative_to(root).as_posix()

        # Criar estação
        estacao = Station(
            nome=nome_estacao,
            modulo=modulo_atual,
            plataformas=plataformas,
            trilhos=trilhos,
            caminho=caminho_atual,
        )

        mapa.estacoes[nome_estacao] = estacao

        # Registrar módulos externos (para analytics)
        for trilho in trilhos:
            raiz_modulo = trilho.modulo.split(".")[0] if trilho.modulo else "unknown"
            if raiz_modulo not in mapa.estacoes:
                mapa.modulo_externo_contador[raiz_modulo] = (
                    mapa.modulo_externo_contador.get(raiz_modulo, 0) + 1
                )

    logger.info(f"✅ Análise concluída: {arquivo_count} arquivos, {len(mapa.estacoes)} estações")

    # Detectar ciclos
    mapa.ciclos = detectar_ciclos(mapa)
    if mapa.ciclos:
        logger.warning(f"⚠️  {len(mapa.ciclos)} ciclo(s) de dependência encontrado(s)")

    # Salvar em cache
    if usar_cache:
        cache_manager = CacheManager()
        cache_manager.salvar(mapa)

    return mapa



def mapa_para_dict_compativel(mapa: MetroMap) -> dict[str, Any]:
    """
    Converte MetroMap para formato de dicionário antigo.

    Para compatibilidade com código legado que espera dict[str, Any].

    Args:
        mapa: MetroMap a converter

    Returns:
        Dicionário no formato antigo
    """
    return {
        "root": str(mapa.root),
        "estacoes": {
            nome: {
                "modulo": estacao.modulo,
                "plataformas": [
                    {
                        "tipo": p.tipo,
                        "nome": p.nome,
                        "linha": p.linha,
                        "metodos": [
                            {
                                "tipo": m.tipo,
                                "nome": m.nome,
                                "linha": m.linha,
                            }
                            for m in p.metodos
                        ],
                    }
                    for p in estacao.plataformas
                ],
                "trilhos": [
                    {
                        "tipo": t.tipo,
                        "modulo": t.modulo,
                        "nome": t.nome,
                        "alias": t.alias,
                        "qualificado": t.qualificado,
                        "nivel": t.nivel,
                    }
                    for t in estacao.trilhos
                ],
                "total_plataformas": estacao.total_plataformas,
                "total_trilhos": estacao.total_trilhos,
            }
            for nome, estacao in mapa.estacoes.items()
        },
        "total_estacoes": mapa.total_estacoes,
    }


if __name__ == "__main__":
    import json

    resultado = parse_project(".")
    dict_result = mapa_para_dict_compativel(resultado)

    print("🚇 Mapa do MetrôCode gerado:")
    print(json.dumps(dict_result, indent=2, ensure_ascii=False))
    print(f"\nTotal de estações: {len(resultado.estacoes)}")
    print(f"Total de plataformas: {resultado.total_plataformas}")
    print(f"Total de trilhos: {resultado.total_trilhos}")

    if resultado.ciclos:
        print(f"\n⚠️  {len(resultado.ciclos)} ciclo(s) de dependência")

