"""
MetrôCode - Motor de layout.
Calcula onde cada estação e plataforma vai aparecer no mapa.
Usa algoritmos de grafo pra deixar tudo bem distribuído.
"""

import networkx as nx
import math


def calcular_layout(grafo, modo="metro"):
    """
    Calcula as posições (x, y) de cada nó do grafo.

    Modos disponíveis:
    - "metro": simula o mapa esquemático do metrô (layout em colunas)
    - "geografico": distribuição baseada em força (kamada_kawai)
    - "circular": tudo em círculo (bom pra poucos nós)
    """

    estacoes = [n for n, d in grafo.nodes(data=True) if d.get("tipo") == "estacao"]
    plataformas = [n for n, d in grafo.nodes(data=True) if d.get("tipo") in ("funcao", "classe", "metodo")]

    if modo == "metro":
        return _layout_metro(grafo, estacoes, plataformas)
    if modo == "geografico":
        return nx.kamada_kawai_layout(grafo)
    if modo == "circular":
        return nx.circular_layout(grafo)
    return nx.spring_layout(grafo, seed=42)


def _layout_metro(grafo, estacoes, plataformas):
    """
    Layout personalizado que imita um mapa de metrô com linhas retas.
    """
    if not estacoes:
        return {}

    positions: dict[str, tuple[float, float]] = {}
    lines: dict[str, list[str]] = {}

    for estacao in estacoes:
        modulo = grafo.nodes[estacao].get("modulo") or estacao
        line_key = modulo.split(".")[0]
        lines.setdefault(line_key, []).append(estacao)

    ordered_lines = sorted(lines.keys(), key=lambda key: (-len(lines[key]), key))
    x_gap = 6.0
    y_gap = 3.5

    for col, line_key in enumerate(ordered_lines):
        line_nodes = sorted(lines[line_key], key=lambda s: (-grafo.degree(s), s))
        for row, estacao in enumerate(line_nodes):
            positions[estacao] = (col * x_gap, row * y_gap)

    for estacao in estacoes:
        x, y = positions[estacao]
        platforms = [
            p for p in plataformas
            if grafo.nodes[p].get("estacao_pai") == estacao
        ]
        if not platforms:
            continue

        radius = 0.8 + min(len(platforms), 6) * 0.15
        for index, platform in enumerate(platforms):
            angle = (index / len(platforms)) * 2 * math.pi
            positions[platform] = (x + radius * math.cos(angle), y + radius * math.sin(angle))

    return positions


if __name__ == "__main__":
    try:
        # Tenta importar como módulo (quando rodado com -m)
        from .parser import parse_project
        from .graph_builder import construir_grafo
    except ImportError:
        # Fallback para quando rodado diretamente
        from parser import parse_project
        from graph_builder import construir_grafo

    mapa = parse_project(".")
    grafo = construir_grafo(mapa)

    for modo in ["metro", "geografico", "circular"]:
        posicoes = calcular_layout(grafo, modo)
        print(f"🚇 Layout '{modo}' calculado: {len(posicoes)} nós posicionados")
        for i, (no, pos) in enumerate(posicoes.items()):
            if i >= 3:
                break
            print(f"   {no}: ({pos[0]:.2f}, {pos[1]:.2f})")
        print()