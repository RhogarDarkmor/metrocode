__version__ = "0.1.1"

__all__ = [
    "MetroApp",
    "MetroCodeApp",
    "build_summary",
    "build_visual_preview",
    "run_visual_dashboard",
    "calcular_layout",
    "construir_grafo",
    "parse_project",
    "__version__",
]


def __getattr__(name: str):
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
    if name == "construir_grafo":
        from .graph_builder import construir_grafo

        return construir_grafo
    if name == "calcular_layout":
        from .layout_engine import calcular_layout

        return calcular_layout
    if name == "parse_project":
        from .parser import parse_project

        return parse_project
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
