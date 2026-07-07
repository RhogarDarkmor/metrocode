"""
MetrôCode - Definições de tipos e dataclasses.

Este módulo centraliza todos os tipos de dados usados no MetrôCode,
facilitando a compreensão da estrutura de dados e permitindo type checking
com mypy. Ideal para iniciantes entenderem como os dados fluem pelo projeto.

Analogia do Metrô:
- Estação (Station): Um arquivo Python no projeto
- Plataforma (Platform): Uma função ou classe dentro da estação
- Trilho (Track): Uma importação/dependência conectando estações
- Mapa (MetroMap): O grafo completo do projeto
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, TypeAlias

# Tipos para melhor compreensão
NodeType: TypeAlias = Literal["estacao", "funcao", "classe", "metodo"]
ImportType: TypeAlias = Literal["import", "import_from"]
LayoutMode: TypeAlias = Literal["metro", "geografico", "circular", "spring"]


@dataclass
class Platform:
    """
    Representa uma função, classe ou método dentro de uma estação (arquivo).

    Atributos:
        nome: Nome da função/classe/método
        tipo: Tipo de plataforma (função, classe ou método)
        linha: Número da linha no arquivo onde foi definida
        metodos: Lista de métodos (apenas se tipo == 'classe')
        doc: Docstring (para futuro uso em análise)

    Exemplo:
        Uma função `def somar(a, b)` na linha 42 seria:
        Platform(nome="somar", tipo="funcao", linha=42)
    """

    nome: str
    tipo: Literal["funcao", "classe", "metodo"]
    linha: int
    metodos: list[Platform] = field(default_factory=list)
    doc: str | None = None

    @property
    def definicao(self) -> str:
        """Retorna uma descrição legível da plataforma."""
        emoji = {"funcao": "⚡", "classe": "📦", "metodo": "🔧"}.get(self.tipo, "•")
        return f"{emoji} {self.nome} (linha {self.linha})"


@dataclass
class Track:
    """
    Representa uma importação/dependência entre estações.

    Atributos:
        tipo: Tipo de import (import ou from...import)
        modulo: Nome do módulo importado (resolvido)
        nome: Nome específico importado (para from...import)
        alias: Alias fornecido (import ... as alias)
        qualificado: Nome completamente qualificado
        nivel: Nível de import relativo (para from . import)

    Exemplo:
        `from os.path import isdir` seria:
        Track(tipo="import_from", modulo="os.path", nome="isdir",
              qualificado="os.path.isdir", nivel=0)
    """

    tipo: ImportType
    modulo: str
    nome: str | None = None
    alias: str | None = None
    qualificado: str | None = None
    nivel: int = 0

    @property
    def referencia(self) -> str:
        """Retorna como esse módulo é referenciado no código."""
        if self.alias:
            return self.alias
        if self.nome and self.tipo == "import_from":
            return self.nome
        return self.modulo


@dataclass
class Station:
    """
    Representa um arquivo Python no projeto (uma 'estação' do metrô).

    Atributos:
        nome: Nome do arquivo (ex: "utils/helpers.py")
        modulo: Nome do módulo Python (ex: "utils.helpers")
        caminho: Caminho completo do arquivo
        plataformas: Lista de funções e classes definidas aqui
        trilhos: Lista de imports/dependências
        total_plataformas: Contagem rápida de funções/classes
        total_trilhos: Contagem rápida de imports

    Exemplo:
        Um arquivo "utils/math.py" com funções "somar" e "subtrair":
        Station(nome="utils/math.py", modulo="utils.math",
                plataformas=[Platform(...), Platform(...)])
    """

    nome: str
    modulo: str
    plataformas: list[Platform] = field(default_factory=list)
    trilhos: list[Track] = field(default_factory=list)
    caminho: Path | str | None = None
    doc: str | None = None

    @property
    def total_plataformas(self) -> int:
        """Número total de funções, classes e métodos."""
        return len(self.plataformas) + sum(
            len(p.metodos) for p in self.plataformas if p.tipo == "classe"
        )

    @property
    def total_trilhos(self) -> int:
        """Número total de imports."""
        return len(self.trilhos)

    @property
    def descricao(self) -> str:
        """Descrição visual da estação."""
        return (
            f"📍 {self.nome}\n"
            f"   🚪 Plataformas: {self.total_plataformas}\n"
            f"   🔗 Trilhos: {self.total_trilhos}"
        )


@dataclass
class MetroMap:
    """
    Representa o mapa completo de um projeto Python.

    Este é o objeto principal que contém toda a informação sobre
    a estrutura do código analisado. Funciona como um "banco de dados"
    da análise.

    Atributos:
        root: Diretório raiz do projeto analisado
        estacoes: Dicionário de todas as estações (arquivos)
        ciclos: Lista de ciclos detectados (dependências circulares)
        modulo_externo_contador: Módulos externos usados (frequência)

    Propriedades:
        total_estacoes: Número de arquivos Python
        total_plataformas: Número total de funções/classes
        total_trilhos: Número total de imports
        tem_ciclos: Se há ciclos de dependência

    Exemplo:
        mapa = parse_project("meu_projeto")
        print(f"Projeto tem {mapa.total_estacoes} arquivos")
        if mapa.tem_ciclos:
            print(f"⚠️ Ciclos detectados: {mapa.ciclos}")
    """

    root: str | Path
    estacoes: dict[str, Station] = field(default_factory=dict)
    ciclos: list[list[str]] = field(default_factory=list)
    modulo_externo_contador: dict[str, int] = field(default_factory=dict)

    @property
    def total_estacoes(self) -> int:
        """Número total de estações (arquivos Python)."""
        return len(self.estacoes)

    @property
    def total_plataformas(self) -> int:
        """Número total de plataformas (funções/classes)."""
        return sum(estacao.total_plataformas for estacao in self.estacoes.values())

    @property
    def total_trilhos(self) -> int:
        """Número total de trilhos (imports)."""
        return sum(estacao.total_trilhos for estacao in self.estacoes.values())

    @property
    def tem_ciclos(self) -> bool:
        """Se o projeto tem ciclos de dependência."""
        return len(self.ciclos) > 0

    @property
    def resumo(self) -> dict[str, Any]:
        """Dicionário com estatísticas do projeto."""
        return {
            "root": str(self.root),
            "total_estacoes": self.total_estacoes,
            "total_plataformas": self.total_plataformas,
            "total_trilhos": self.total_trilhos,
            "tem_ciclos": self.tem_ciclos,
            "ciclos_detectados": len(self.ciclos),
            "modulos_externos_unicos": len(self.modulo_externo_contador),
        }


@dataclass
class NodeData:
    """Dados de um nó no grafo (para export)."""

    id: str
    tipo: NodeType
    nome: str
    linha: int | None = None
    estacao_pai: str | None = None
    modulo: str = ""
    total_plataformas: int = 0
    total_trilhos: int = 0


@dataclass
class EdgeData:
    """Dados de uma aresta no grafo (para export)."""

    source: str
    target: str
    tipo: str
    cor: str = "#AAAAAA"
    modulo: str = ""
    peso: int = 1
