"""
MetrôCode - Análise avançada de estrutura de código.

Este módulo fornece ferramentas para analisar o código além do parsing básico:
- Detectar ciclos de dependência (estrutura problemática)
- Encontrar módulos mais complexos
- Calcular métricas de qualidade
- Sugerir refatorações

Educativo: Mostra conceitos importantes para iniciantes como:
  * Ciclos de dependência (por que são ruins)
  * Complexidade ciclomática
  * Cohesão e acoplamento
"""

from __future__ import annotations

import logging
from collections import defaultdict, deque
from typing import Any

import networkx as nx

from .types import MetroMap, Station

logger = logging.getLogger(__name__)


def detectar_ciclos(mapa: MetroMap) -> list[list[str]]:
    """
    Detecta ciclos de dependência no projeto.

    Um ciclo acontece quando há uma cadeia circular de imports:
    - arquivo A importa de B
    - arquivo B importa de C
    - arquivo C importa de A novamente

    Por que isso é ruim?
    - Torna o código mais difícil de entender
    - Cria dependências mútuas que complicam testes
    - Quebra o princípio de arquitetura em camadas

    Args:
        mapa: O MetroMap analisado

    Returns:
        Lista de ciclos encontrados. Cada ciclo é uma lista de nomes de estações.
        Exemplo: [['parser.py', 'graph_builder.py', 'parser.py']]

    Nota: Usa o algoritmo de detecção de ciclos do NetworkX.
    """
    # Construir grafo dirigido de dependências
    grafo_dirigido = nx.DiGraph()

    # Adicionar nós
    for nome_estacao in mapa.estacoes:
        grafo_dirigido.add_node(nome_estacao)

    # Adicionar arestas baseadas em imports
    for nome_estacao, estacao in mapa.estacoes.items():
        for trilho in estacao.trilhos:
            # Tentar encontrar a estação destino
            modulo_alvo = trilho.modulo
            for outra_estacao in mapa.estacoes:
                if mapa.estacoes[outra_estacao].modulo == modulo_alvo or (
                    modulo_alvo in mapa.estacoes[outra_estacao].modulo.split(".")
                ):
                    if nome_estacao != outra_estacao:
                        grafo_dirigido.add_edge(nome_estacao, outra_estacao)
                    break

    # Encontrar todos os ciclos
    try:
        ciclos = list(nx.simple_cycles(grafo_dirigido))
        return ciclos
    except nx.NetworkXError:
        return []


def encontrar_complexos(mapa: MetroMap, top: int = 5) -> list[tuple[str, int]]:
    """
    Encontra as 'estações' mais complexas do projeto.

    Complexidade é medida por:
    - Número de funções/classes definidas
    - Número de dependencies (imports)

    Útil para:
    - Identificar módulos que precisam refatoração
    - Ensinar sobre coesão (módulos com muitas responsabilidades)

    Args:
        mapa: O MetroMap analisado
        top: Quantos módulos retornar (padrão 5)

    Returns:
        Lista de (nome_estacao, score_complexidade) ordenada
    """
    complexidade: dict[str, int] = {}

    for nome, estacao in mapa.estacoes.items():
        # Cada função/classe conta como 1 ponto
        # Cada import externo conta como 2 pontos (mais acoplamento = mais complexo)
        score = estacao.total_plataformas + (estacao.total_trilhos * 2)
        complexidade[nome] = score

    # Ordenar por complexidade (maior primeiro)
    ordenado = sorted(complexidade.items(), key=lambda x: x[1], reverse=True)
    return ordenado[:top]


def encontrar_hubs(mapa: MetroMap, top: int = 5) -> list[tuple[str, int]]:
    """
    Encontra as 'estações' mais usadas/importadas.

    Um 'hub' é um módulo que muitos outros módulos dependem.
    Pode ser bom (módulo utilitário reutilizável) ou ruim (muita responsabilidade).

    Args:
        mapa: O MetroMap analisado
        top: Quantos módulos retornar (padrão 5)

    Returns:
        Lista de (nome_estacao, vezes_importado) ordenada
    """
    contador_imports: dict[str, int] = defaultdict(int)

    for estacao in mapa.estacoes.values():
        for trilho in estacao.trilhos:
            # Tenta mapear o módulo importado para uma estação local
            for nome_alvo, estacao_alvo in mapa.estacoes.items():
                if trilho.modulo == estacao_alvo.modulo or (
                    trilho.modulo in estacao_alvo.modulo.split(".")
                ):
                    contador_imports[nome_alvo] += 1
                    break

    ordenado = sorted(contador_imports.items(), key=lambda x: x[1], reverse=True)
    return ordenado[:top]


def sugerir_refatoracoes(mapa: MetroMap) -> list[str]:
    """
    Analisa o projeto e sugere refatorações.

    Útil para:
    - Ensinar boas práticas de arquitetura
    - Identificar problemas estruturais
    - Guiar iniciantes

    Returns:
        Lista de sugestões de melhoria
    """
    sugestoes: list[str] = []

    # Detectar ciclos
    if mapa.tem_ciclos:
        sugestoes.append(
            f"⚠️  CICLOS DETECTADOS: {len(mapa.ciclos)} ciclo(s) de dependência encontrado(s). "
            "Isso torna o código mais difícil de entender e testar. "
            "Considere reorganizar os imports para formar uma hierarquia limpa."
        )

    # Identificar módulos muito complexos
    complexos = encontrar_complexos(mapa, top=3)
    if complexos and complexos[0][1] > 20:
        sugestoes.append(
            f"📦 MODULO SOBRECARRE GADO: '{complexos[0][0]}' tem {complexos[0][1]} pontos de complexidade. "
            "Considere quebra-lo em módulos menores com responsabilidades específicas (Single Responsibility Principle)."
        )

    # Muitas dependências externas
    total_externos = len(mapa.modulo_externo_contador)
    if total_externos > 15:
        sugestoes.append(
            f"🔗 MUITAS DEPENDENCIAS EXTERNAS: {total_externos} módulos externos. "
            "Considere consolidar ou compartilhar dependências. "
            "Use um 'requirements.txt' ou 'pyproject.toml' bem estruturado."
        )

    # Nenhuma sugestão = bom sinal
    if not sugestoes:
        sugestoes.append(
            "✅ ESTRUTURA SAUDAVEL: O projeto parece bem arquitetado! "
            "Mantenha assim enquanto cresce."
        )

    return sugestoes


def calcular_metricas_educativas(mapa: MetroMap) -> dict[str, Any]:
    """
    Calcula métricas educativas sobre a estrutura do código.

    Métricas úteis para ensinar sobre arquitetura de software:
    - Densidade de imports (acoplamento)
    - Distribuição de complexidade
    - Taxa de reutilização

    Returns:
        Dicionário com várias métricas
    """
    if mapa.total_estacoes == 0:
        return {}

    # Densidade de imports (quanto o projeto é "acoplado")
    densidade_imports = (
        mapa.total_trilhos / mapa.total_estacoes if mapa.total_estacoes > 0 else 0
    )

    # Média de plataformas por estação
    media_plataformas = (
        mapa.total_plataformas / mapa.total_estacoes if mapa.total_estacoes > 0 else 0
    )

    # Calcular distribuição de complexidade (Gini coefficient)
    complexidades = [e.total_plataformas for e in mapa.estacoes.values()]
    if complexidades:
        sorted_complex = sorted(complexidades)
        gini = calcular_gini(sorted_complex)
    else:
        gini = 0.0

    return {
        "total_estacoes": mapa.total_estacoes,
        "total_plataformas": mapa.total_plataformas,
        "total_trilhos": mapa.total_trilhos,
        "densidade_imports": round(densidade_imports, 2),
        "media_plataformas_por_estacao": round(media_plataformas, 2),
        "indices_gini_complexidade": round(gini, 3),
        "módulos_externos": len(mapa.modulo_externo_contador),
        "ciclos_detectados": len(mapa.ciclos),
        "interpretacao": interpretar_metricas(densidade_imports, gini),
    }


def calcular_gini(valores: list[int]) -> float:
    """
    Calcula o coeficiente de Gini.

    Mede a desigualdade na distribuição de valores.
    - Gini = 0: Distribuição perfeitamente igual
    - Gini = 1: Distribuição perfeitamente desigual

    Útil para ver se a complexidade está bem distribuída entre módulos.
    """
    if not valores or len(valores) < 2:
        return 0.0

    n = len(valores)
    soma_diferenca = sum(
        abs(valores[i] - valores[j]) for i in range(n) for j in range(n)
    )
    media = sum(valores) / n
    gini = soma_diferenca / (2 * n * n * media) if media > 0 else 0
    return min(gini, 1.0)


def interpretar_metricas(densidade: float, gini: float) -> str:
    """
    Interpreta as métricas em linguagem acessível.

    Ensina o que os números significam.
    """
    if densidade < 1.0 and gini < 0.3:
        return "🟢 EXCELENTE: Projeto bem estruturado, módulos independentes, complexidade equilibrada"
    elif densidade < 2.0 and gini < 0.6:
        return "🟡 BOM: Estrutura razoável, considere reduzir acoplamento"
    elif densidade < 3.0:
        return "🟠 ATENÇÃO: Alto acoplamento, algumas refatorações necessárias"
    else:
        return "🔴 CRITICO: Muito acoplado, refatoração urgente recomendada"


def relatorio_completo(mapa: MetroMap) -> str:
    """
    Gera um relatório completo de análise.

    Útil para exibir no console de forma didática.
    """
    linhas = [
        "🚇 ANALISE COMPLETA DO PROJETO",
        "=" * 50,
        "",
        "📊 METRICAS",
        "-" * 50,
    ]

    metricas = calcular_metricas_educativas(mapa)
    for chave, valor in metricas.items():
        if chave != "interpretacao":
            linhas.append(f"{chave.replace('_', ' ').title()}: {valor}")

    if "interpretacao" in metricas:
        linhas.append("")
        linhas.append(metricas["interpretacao"])

    # Módulos mais complexos
    complexos = encontrar_complexos(mapa, top=5)
    if complexos:
        linhas.append("")
        linhas.append("📦 MODULOS MAIS COMPLEXOS")
        linhas.append("-" * 50)
        for nome, score in complexos:
            linhas.append(f"  {nome}: {score} pontos de complexidade")

    # Módulos mais usados (hubs)
    hubs = encontrar_hubs(mapa, top=5)
    if hubs:
        linhas.append("")
        linhas.append("🔗 MODULOS MAIS IMPORTADOS (HUBS)")
        linhas.append("-" * 50)
        for nome, vezes in hubs:
            linhas.append(f"  {nome}: importado {vezes} vezes")

    # Ciclos
    if mapa.tem_ciclos:
        linhas.append("")
        linhas.append("⚠️  CICLOS DE DEPENDENCIA")
        linhas.append("-" * 50)
        for i, ciclo in enumerate(mapa.ciclos[:5], 1):
            linhas.append(f"  Ciclo {i}: {' → '.join(ciclo)} → {ciclo[0]}")

    # Sugestões
    linhas.append("")
    linhas.append("💡 SUGESTOES DE MELHORIA")
    linhas.append("-" * 50)
    for sugestao in sugerir_refatoracoes(mapa):
        linhas.append(f"  {sugestao}")

    linhas.append("")
    return "\n".join(linhas)
