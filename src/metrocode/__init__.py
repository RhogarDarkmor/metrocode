"""
MetrôCode - Visualize Python code structure like a subway map.

Este é um framework educativo para entender código Python através
de uma metáfora visual: arquivos são estações, funções são plataformas,
e imports são trilhos conectando tudo.

Módulos principais:
- parser: Analisa código Python
- types: Definições de tipos (Station, Platform, Track, etc)
- analyzer: Análise avançada (ciclos, métricas, sugestões)
- graph_builder: Constrói grafo NetworkX
- layout_engine: Calcula posições para visualização
- cache: Cacheia análises para performance
- app: Aplicação Textual (TUI)

Uso básico:
    >>> from metrocode import parse_project
    >>> mapa = parse_project("meu_projeto")
    >>> print(f"Total de arquivos: {mapa.total_estacoes}")
"""

__version__ = "0.1.1"

__all__ = [
    # Tipos principais
    "MetroMap",
    "Station",
    "Platform",
    "Track",
    # Funções principais
    "parse_project",
    "construir_grafo",
    "calcular_layout",
    # App/UI
    "MetroApp",
    "MetroCodeApp",
    "build_summary",
    "build_visual_preview",
    "run_visual_dashboard",
    # Análise
    "detectar_ciclos",
    "encontrar_complexos",
    "sugerir_refatoracoes",
    "relatorio_completo",
    "__version__",
]


def __getattr__(name: str):
    # Tipos
    if name in {"MetroMap", "Station", "Platform", "Track"}:
        from .types import MetroMap, Platform, Station, Track

        return {
            "MetroMap": MetroMap,
            "Station": Station,
            "Platform": Platform,
            "Track": Track,
        }[name]

    # App
    if name in {
        "MetroApp",
        "MetroCodeApp",
        "build_summary",
        "build_visual_preview",
        "run_visual_dashboard",
    }:
        from .app import (
            MetroApp,
            MetroCodeApp,
            build_summary,
            build_visual_preview,
            run_visual_dashboard,
        )

        return {
            "MetroApp": MetroApp,
            "MetroCodeApp": MetroCodeApp,
            "build_summary": build_summary,
            "build_visual_preview": build_visual_preview,
            "run_visual_dashboard": run_visual_dashboard,
        }[name]

    # Grafo
    if name == "construir_grafo":
        from .graph_builder import construir_grafo

        return construir_grafo

    # Layout
    if name == "calcular_layout":
        from .layout_engine import calcular_layout

        return calcular_layout

    # Parser
    if name == "parse_project":
        from .parser import parse_project

        return parse_project

    # Análise
    if name in {"detectar_ciclos", "encontrar_complexos", "sugerir_refatoracoes", "relatorio_completo"}:
        from .analyzer import (
            detectar_ciclos,
            encontrar_complexos,
            relatorio_completo,
            sugerir_refatoracoes,
        )

        return {
            "detectar_ciclos": detectar_ciclos,
            "encontrar_complexos": encontrar_complexos,
            "sugerir_refatoracoes": sugerir_refatoracoes,
            "relatorio_completo": relatorio_completo,
        }[name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

