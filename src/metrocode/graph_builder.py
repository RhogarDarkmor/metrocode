"""
MetrôCode - Construtor de grafo.
Transforma o dicionário do parser em um grafo NetworkX,
com estações (nós) e trilhos (arestas) coloridos igual linha de metrô.
"""

import networkx as nx


CORES_LINHAS = {
    "azul": "#0033A0",
    "verde": "#007F4E",
    "vermelha": "#EE1D23",
    "amarela": "#FFC72C",
    "lilas": "#9B59B6",
    "rubi": "#E87200",
    "diamante": "#7F7F7F",
    "esmeralda": "#00A88F",
    "turquesa": "#00B5E2",
    "coral": "#F07D7D",
    "safira": "#1A2B5F",
    "jade": "#2E8B57",
}

COR_PADRAO = "#AAAAAA"


def construir_grafo(mapa):
    """
    Recebe o dicionário do parser e devolve um grafo NetworkX.
    Cada estação vira um nó, cada trilho vira uma aresta.
    """
    grafo = nx.Graph()
    linhas_usadas = {}

    for nome_estacao, dados in mapa["estacoes"].items():
        grafo.add_node(
            nome_estacao,
            tipo="estacao",
            nome=nome_estacao,
            total_plataformas=dados["total_plataformas"],
            total_trilhos=dados["total_trilhos"],
        )

        for plat in dados["plataformas"]:
            id_plataforma = f"{nome_estacao}::{plat['nome']}"
            grafo.add_node(
                id_plataforma,
                tipo=plat["tipo"],
                nome=plat["nome"],
                linha_codigo=plat["linha"],
                estacao_pai=nome_estacao,
            )
            grafo.add_edge(nome_estacao, id_plataforma, tipo="interno", cor="#555555")

        for trilho in dados["trilhos"]:
            modulo_importado = trilho.get("origem") or trilho.get("destino")
            if not modulo_importado:
                continue

            modulo_raiz = modulo_importado.split(".")[0]

            if modulo_raiz not in linhas_usadas:
                cores_disponiveis = [c for c in CORES_LINHAS.values() if c not in linhas_usadas.values()]
                if cores_disponiveis:
                    linhas_usadas[modulo_raiz] = cores_disponiveis[0]
                else:
                    linhas_usadas[modulo_raiz] = COR_PADRAO

            cor_trilho = linhas_usadas[modulo_raiz]

            for outra_estacao, outros_dados in mapa["estacoes"].items():
                if outra_estacao == nome_estacao:
                    continue
                for outro_trilho in outros_dados["trilhos"]:
                    outro_modulo = outro_trilho.get("origem") or outro_trilho.get("destino")
                    if outro_modulo and outro_modulo.split(".")[0] == modulo_raiz:
                        grafo.add_edge(
                            nome_estacao,
                            outra_estacao,
                            tipo="trilho",
                            cor=cor_trilho,
                            modulo=modulo_raiz,
                        )

    return grafo