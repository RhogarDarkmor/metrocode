"""
MetrôCode - Construtor de grafo.
Transforma o dicionário do parser em um grafo NetworkX,
com estações (nós) e trilhos (arestas) coloridos igual linha de metrô.
"""

from __future__ import annotations

from typing import Any
import networkx as nx


LINE_COLORS: dict[str, str] = {
    "azul": "#005FA7",
    "verde": "#009246",
    "vermelha": "#EE2737",
    "amarela": "#FEDD00",
    "lilas": "#8C4799",
    "prata": "#A7A9AC",
    "ouro": "#FFCD00",
    "rosa": "#E3007D",
    "bronze": "#8A5B2C",
    "turquesa": "#00A9B7",
    "coral": "#F07D7D",
    "magneta": "#C4007E",
}

DEFAULT_EDGE_COLOR = "#AAAAAA"


def _choose_edge_color(modulo: str, line_color_map: dict[str, str]) -> str:
    root_module = modulo.split(".")[0]
    if root_module not in line_color_map:
        available_colors = [color for color in LINE_COLORS.values() if color not in line_color_map.values()]
        line_color_map[root_module] = available_colors[0] if available_colors else DEFAULT_EDGE_COLOR
    return line_color_map[root_module]


def _find_target_station(modulo: str, module_to_station: dict[str, str]) -> str | None:
    if not modulo:
        return None

    if modulo in module_to_station:
        return module_to_station[modulo]

    candidates = [
        (station, mod)
        for mod, station in module_to_station.items()
        if modulo.startswith(mod + ".") or mod.startswith(modulo + ".")
    ]
    if not candidates:
        return None

    candidates.sort(key=lambda item: len(item[1]), reverse=True)
    return candidates[0][0]


def construir_grafo(mapa: dict[str, Any]) -> nx.Graph:
    """Recebe o dicionário do parser e devolve um grafo NetworkX."""
    grafo = nx.Graph()
    line_color_map: dict[str, str] = {}
    module_to_station: dict[str, str] = {
        dados["modulo"]: nome_estacao
        for nome_estacao, dados in mapa.get("estacoes", {}).items()
        if dados.get("modulo")
    }

    for nome_estacao, dados in mapa.get("estacoes", {}).items():
        grafo.add_node(
            nome_estacao,
            tipo="estacao",
            nome=nome_estacao,
            modulo=dados.get("modulo", ""),
            total_plataformas=dados.get("total_plataformas", 0),
            total_trilhos=dados.get("total_trilhos", 0),
        )

        for plat in dados.get("plataformas", []):
            id_plataforma = f"{nome_estacao}::{plat['nome']}"
            grafo.add_node(
                id_plataforma,
                tipo=plat.get("tipo", "funcao"),
                nome=plat.get("nome", "sem-nome"),
                linha_codigo=plat.get("linha"),
                estacao_pai=nome_estacao,
            )
            if not grafo.has_edge(nome_estacao, id_plataforma):
                grafo.add_edge(nome_estacao, id_plataforma, tipo="interno", cor="#555555")

        for trilho in dados.get("trilhos", []):
            modulo_importado = trilho.get("qualificado") or trilho.get("modulo") or trilho.get("destino")
            if not modulo_importado:
                continue

            cor_trilho = _choose_edge_color(modulo_importado, line_color_map)
            target_station = _find_target_station(modulo_importado, module_to_station)

            if target_station and target_station != nome_estacao:
                if not grafo.has_edge(nome_estacao, target_station):
                    grafo.add_edge(
                        nome_estacao,
                        target_station,
                        tipo="import",
                        cor=cor_trilho,
                        modulo=modulo_importado,
                    )
                continue

            modulo_raiz = modulo_importado.split(".")[0]
            target_station = _find_target_station(modulo_raiz, module_to_station)
            if target_station and target_station != nome_estacao:
                if not grafo.has_edge(nome_estacao, target_station):
                    grafo.add_edge(
                        nome_estacao,
                        target_station,
                        tipo="import",
                        cor=cor_trilho,
                        modulo=modulo_raiz,
                    )

    return grafo