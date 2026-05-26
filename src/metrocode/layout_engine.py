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
    - "metro": simula o mapa esquemático do metrô (spring_layout adaptado)
    - "geografico": distribuição baseada em força (kamada_kawai)
    - "circular": tudo em círculo (bom pra poucos nós)
    """
    
    estacoes = [n for n, d in grafo.nodes(data=True) if d.get("tipo") == "estacao"]
    plataformas = [n for n, d in grafo.nodes(data=True) if d.get("tipo") in ("funcao", "classe", "metodo")]
    
    if modo == "metro":
        posicoes = _layout_metro(grafo, estacoes, plataformas)
    elif modo == "geografico":
        posicoes = nx.kamada_kawai_layout(grafo)
    elif modo == "circular":
        posicoes = nx.circular_layout(grafo)
    else:
        posicoes = nx.spring_layout(grafo, seed=42)
    
    return posicoes


def _layout_metro(grafo, estacoes, plataformas):
    """
    Layout personalizado que imita um mapa de metrô.
    """
    posicoes = {}
    
    num_estacoes = len(estacoes)
    colunas = math.ceil(math.sqrt(num_estacoes))
    
    for i, estacao in enumerate(estacoes):
        linha_grid = i // colunas
        coluna_grid = i % colunas
        
        x = coluna_grid * 3.0
        y = linha_grid * 3.0
        
        posicoes[estacao] = (x, y)
        
        plataformas_da_estacao = [
            p for p in plataformas 
            if grafo.nodes[p].get("estacao_pai") == estacao
        ]
        
        num_plats = len(plataformas_da_estacao)
        for j, plat in enumerate(plataformas_da_estacao):
            angulo = (j / max(num_plats, 1)) * 2 * math.pi
            raio = 0.8
            
            px = x + raio * math.cos(angulo)
            py = y + raio * math.sin(angulo)
            
            posicoes[plat] = (px, py)
    
    return posicoes


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