"""
MetrôCode - Parser de código Python.
Transforma arquivos em estações, funções em plataformas e imports em trilhos.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any


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
}


def parse_project(root_path: str | Path | None = ".") -> dict[str, Any]:
    """Percorre uma pasta de projeto Python e extrai a estrutura do código."""
    root = Path(root_path or ".").resolve()

    mapa: dict[str, Any] = {
        "root": str(root),
        "estacoes": {},
        "total_estacoes": 0,
    }

    if not root.exists():
        return mapa

    for caminho_atual in sorted(root.rglob("*.py")):
        if not caminho_atual.is_file() or any(pasta in caminho_atual.parts for pasta in PASTAS_IGNORADAS):
            continue

        try:
            conteudo = caminho_atual.read_text(encoding="utf-8")
            arvore = ast.parse(conteudo, filename=str(caminho_atual))
        except (SyntaxError, UnicodeDecodeError, OSError):
            continue

        plataformas: list[dict[str, Any]] = []
        trilhos: list[dict[str, Any]] = []

        for nodo in ast.walk(arvore):
            if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
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
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
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
                    trilhos.append({"tipo": "import", "destino": alias.name})
            elif isinstance(nodo, ast.ImportFrom):
                if nodo.module:
                    for alias in nodo.names:
                        trilhos.append(
                            {
                                "tipo": "import_from",
                                "origem": nodo.module,
                                "destino": alias.name,
                            }
                        )

        nome_estacao = str(caminho_atual.relative_to(root)).replace("\\", "/")
        mapa["estacoes"][nome_estacao] = {
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