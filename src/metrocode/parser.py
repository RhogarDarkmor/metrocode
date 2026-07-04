"""
MetrôCode - Parser de código Python.
Transforma arquivos em estações, funções em plataformas e imports em trilhos.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

MapaData = dict[str, Any]

AST_FUNCTION_TYPES = (ast.FunctionDef, ast.AsyncFunctionDef)
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
}


def _is_ignored_path(caminho: Path) -> bool:
    return any(pasta in caminho.parts for pasta in PASTAS_IGNORADAS)


def _module_name_from_path(caminho: Path, root: Path) -> str:
    relativo = caminho.relative_to(root).as_posix()
    if relativo == "__init__.py":
        return ""
    if relativo.endswith("/__init__.py"):
        relativo = relativo[: -len("/__init__.py")]
    elif relativo.endswith(".py"):
        relativo = relativo[: -len(".py")]
    return relativo.replace("/", ".")


def _resolve_relative_import(
    module: str | None, level: int, current_module: str
) -> str:
    current_parts = current_module.split(".") if current_module else []
    if current_parts:
        current_parts = current_parts[:-1]

    parent_parts = current_parts[: max(len(current_parts) - level + 1, 0)]
    if module:
        if parent_parts:
            return ".".join([*parent_parts, *module.split(".")])
        return module
    return ".".join(parent_parts)


def parse_project(root_path: str | Path | None = ".") -> MapaData:
    """Percorre uma pasta de projeto Python e extrai a estrutura do código."""
    root = Path(root_path or ".").resolve()

    mapa: MapaData = {
        "root": str(root),
        "estacoes": {},
        "total_estacoes": 0,
    }

    if not root.exists():
        return mapa

    for caminho_atual in sorted(root.rglob("*.py")):
        if not caminho_atual.is_file() or _is_ignored_path(caminho_atual):
            continue

        try:
            conteudo = caminho_atual.read_text(encoding="utf-8")
            arvore = ast.parse(conteudo, filename=str(caminho_atual))
        except (SyntaxError, UnicodeDecodeError, OSError):
            continue

        modulo_atual = _module_name_from_path(caminho_atual, root)
        plataformas: list[dict[str, Any]] = []
        trilhos: list[dict[str, Any]] = []

        for nodo in ast.walk(arvore):
            if isinstance(nodo, AST_FUNCTION_TYPES):
                plataformas.append(
                    {
                        "tipo": "funcao",
                        "nome": nodo.name,
                        "linha": nodo.lineno,
                    }
                )
            elif isinstance(nodo, ast.ClassDef):
                metodos = []
                for item in nodo.body:
                    if isinstance(item, AST_FUNCTION_TYPES):
                        metodos.append(
                            {
                                "tipo": "metodo",
                                "nome": item.name,
                                "linha": item.lineno,
                            }
                        )

                plataformas.append(
                    {
                        "tipo": "classe",
                        "nome": nodo.name,
                        "linha": nodo.lineno,
                        "metodos": metodos,
                    }
                )
            elif isinstance(nodo, ast.Import):
                for alias in nodo.names:
                    trilhos.append(
                        {
                            "tipo": "import",
                            "modulo": alias.name,
                            "alias": alias.asname,
                            "qualificado": alias.name,
                        }
                    )
            elif isinstance(nodo, ast.ImportFrom):
                resolved_module = _resolve_relative_import(
                    nodo.module, nodo.level, modulo_atual
                )
                for alias in nodo.names:
                    if alias.name == "*":
                        qualificado = resolved_module or "*"
                    elif resolved_module:
                        qualificado = f"{resolved_module}.{alias.name}"
                    else:
                        qualificado = alias.name

                    trilhos.append(
                        {
                            "tipo": "import_from",
                            "modulo": resolved_module,
                            "nome": alias.name,
                            "alias": alias.asname,
                            "qualificado": qualificado,
                            "nivel": nodo.level,
                        }
                    )

        nome_estacao = caminho_atual.relative_to(root).as_posix()
        mapa["estacoes"][nome_estacao] = {
            "modulo": modulo_atual,
            "plataformas": plataformas,
            "trilhos": trilhos,
            "total_plataformas": len(plataformas),
            "total_trilhos": len(trilhos),
        }

    mapa["total_estacoes"] = len(mapa["estacoes"])
    return mapa


if __name__ == "__main__":
    import json

    resultado = parse_project(".")

    print("🚇 Mapa do MetrôCode gerado:")
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    print(f"\nTotal de estações: {len(resultado['estacoes'])}")
