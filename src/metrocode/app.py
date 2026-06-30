from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def _normalize_station_name(name: str) -> str:
    return name.strip().replace("\\", "/")

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Footer, Header, ListItem, ListView, Static

from .parser import parse_project
from .graph_builder import construir_grafo
from .layout_engine import calcular_layout


def build_summary(mapa_data: dict[str, Any]) -> str:
    """Gera um resumo textual legível do mapa do projeto."""
    estacoes = mapa_data.get("estacoes", {})
    if not estacoes:
        return "🚇 Nenhuma estação encontrada. Execute em um diretório com código Python."

    linhas = ["🚇 METRÔCODE - MAPA DE DEPENDÊNCIAS", "=" * 40, ""]

    for estacao, dados in list(estacoes.items())[:10]:
        linhas.append(f"📍 ESTAÇÃO: {estacao}")
        linhas.append(f"   🚪 Plataformas: {dados.get('total_plataformas', 0)}")
        linhas.append(f"   🔗 Trilhos: {dados.get('total_trilhos', 0)}")

        plataformas = dados.get("plataformas", [])
        if plataformas[:3]:
            linhas.append("   🏢 Principais plataformas:")
            for plataforma in plataformas[:3]:
                nome = plataforma.get("nome", "sem-nome")
                tipo = "📦" if plataforma.get("tipo") == "classe" else "⚡"
                linhas.append(f"      {tipo} {nome}")

        linhas.append("")

    if len(estacoes) > 10:
        linhas.append(f"... e mais {len(estacoes) - 10} estações")

    return "\n".join(linhas)


class MetroMap(Static):
    """Widget responsável por renderizar o mapa do metrô no terminal."""

    def __init__(self, mapa_data: dict[str, Any]):
        super().__init__()
        self.mapa_data = mapa_data

    def render(self) -> str:
        return build_summary(self.mapa_data)


def build_visual_preview(mapa_data: dict[str, Any], selected_station: str | None = None) -> str:
    """Gera uma pré-visualização visual do mapa em estilo terminal."""
    estacoes = list(mapa_data.get("estacoes", {}).keys())
    if not estacoes:
        return "Mapa visual\nNenhuma estação disponível."

    linhas = ["Mapa visual", "=" * 28, ""]
    for index, station in enumerate(estacoes[:8]):
        marcador = "▶" if selected_station and station == selected_station else "●"
        linhas.append(f"{marcador} {station}")
        if index < min(len(estacoes), 8) - 1:
            linhas.append("   │")

    if len(estacoes) > 8:
        linhas.append("   ...")

    return "\n".join(linhas)


def export_map_image(mapa_data: dict[str, Any], *, output: str = "metrocode_map.png", fmt: str = "png", layout_mode: str = "metro") -> str:
    """Exporta o mapa como imagem (PNG ou SVG) usando NetworkX + Matplotlib.

    Retorna o caminho do arquivo gerado.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import networkx as nx
    except Exception as exc:  # pragma: no cover - environment-specific
        raise RuntimeError("matplotlib e networkx são necessários para exportar imagens") from exc

    grafo = construir_grafo(mapa_data)
    pos = calcular_layout(grafo, modo=layout_mode)

    plt.figure(figsize=(10, 8))
    nx.draw_networkx_nodes(grafo, pos, node_size=200, node_color="#1f77b4")
    nx.draw_networkx_edges(grafo, pos, alpha=0.6)
    labels = {n: n.split("::")[1] if "::" in n else n for n in grafo.nodes()}
    nx.draw_networkx_labels(grafo, pos, labels=labels, font_size=8)

    plt.axis("off")
    plt.tight_layout()
    out = str(output)
    plt.savefig(out, format=fmt, dpi=150)
    plt.close()
    return out


def build_station_details(mapa_data: dict[str, Any], station_name: str) -> str:
    """Gera um bloco com detalhes de uma estação específica."""
    estacoes = mapa_data.get("estacoes", {})
    name = _normalize_station_name(station_name)

    if name not in estacoes:
        matches = [station for station in estacoes if name.lower() in station.lower()]
        if matches:
            name = matches[0]
        else:
            return f"❌ Estação não encontrada: {station_name}"

    dados = estacoes[name]
    linhas = [f"Detalhes da estação", f"=" * 32, f"📍 {name}"]
    linhas.append(f"   🚪 Plataformas: {dados.get('total_plataformas', 0)}")
    linhas.append(f"   🔗 Trilhos: {dados.get('total_trilhos', 0)}")

    plataformas = dados.get("plataformas", [])
    if plataformas:
        linhas.append("\n🏢 Plataformas:")
        for plataforma in plataformas:
            nome = plataforma.get("nome", "sem-nome")
            tipo = "classe" if plataforma.get("tipo") == "classe" else "função"
            linhas.append(f"   - {nome} ({tipo})")

    trilhos = dados.get("trilhos", [])
    if trilhos:
        linhas.append("\n🔗 Trilhos:")
        for trilho in trilhos[:6]:
            origem = trilho.get("origem")
            destino = trilho.get("destino")
            if origem and destino:
                linhas.append(f"   - {origem} -> {destino}")
            elif destino:
                linhas.append(f"   - {destino}")

    return "\n".join(linhas)


def run_interactive_console(mapa_data: dict[str, Any]) -> None:
    """Oferece um menu interativo em terminal para explorar o mapa."""
    print("\n🚇 MetrôCode - modo interativo")
    print("Escolha uma opção:")
    print("1. Ver resumo geral")
    print("2. Ver detalhes de uma estação")
    print("3. Buscar estação por nome")
    print("4. Sair")

    while True:
        try:
            choice = input("\nSua opção: ").strip().lower()
        except EOFError:
            print("\nEncerrando o MetrôCode.")
            return

        if choice in {"1", "resumo", "menu"}:
            print("\n" + build_summary(mapa_data))
        elif choice in {"2", "detalhes"}:
            station_name = input("Nome da estação: ").strip()
            print("\n" + build_station_details(mapa_data, station_name))
        elif choice in {"3", "buscar"}:
            term = input("Termo de busca: ").strip().lower()
            estacoes = mapa_data.get("estacoes", {})
            matches = [station for station in estacoes if term in station.lower()]
            if matches:
                print("\nEstações encontradas:")
                for station in matches:
                    print(f"- {station}")
            else:
                print("\nNenhuma estação encontrada.")
        elif choice in {"4", "sair", "q", "quit"}:
            print("\nEncerrando o MetrôCode.")
            break
        else:
            print("Opção inválida. Tente novamente.")


def run_visual_dashboard(mapa_data: dict[str, Any]) -> None:
    """Renderiza uma interface visual interativa usando Rich no terminal."""
    console = Console()
    estacoes = mapa_data.get("estacoes", {})
    station_names = list(estacoes.keys())

    if not station_names:
        console.print(Panel.fit("🚇 Nenhuma estação disponível", title="MetrôCode", border_style="red"))
        return

    while True:
        console.clear()
        console.print(Panel.fit("[bold cyan]🚇 METRÔCODE[/bold cyan]\n[dim]Mapa visual interativo do projeto[/dim]", border_style="cyan"))

        table = Table(title="Estações", show_header=True, header_style="bold magenta")
        table.add_column("#", justify="right", style="cyan")
        table.add_column("Estação", style="white")
        table.add_column("Plataformas", justify="right", style="green")
        table.add_column("Trilhos", justify="right", style="yellow")

        for index, station_name in enumerate(station_names[:10], start=1):
            dados = estacoes[station_name]
            table.add_row(str(index), station_name, str(dados.get("total_plataformas", 0)), str(dados.get("total_trilhos", 0)))

        console.print(table)
        console.print("[bold]Comandos:[/bold] digite o número da estação para ver detalhes ou [q] para sair")

        try:
            choice = console.input("[bold]Escolha[/bold] > ").strip().lower()
        except EOFError:
            break

        if choice in {"q", "quit", "sair"}:
            break

        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(station_names[:10]):
                station_name = station_names[index]
                console.print(Panel.fit(build_station_details(mapa_data, station_name), title=f"Detalhes: {station_name}", border_style="green"))
                console.input("[dim]Pressione Enter para continuar[/dim]")
            else:
                console.print("[red]Seleção inválida.[/red]")
                console.input("[dim]Pressione Enter para continuar[/dim]")
        else:
            console.print("[red]Digite um número ou 'q'.[/red]")
            console.input("[dim]Pressione Enter para continuar[/dim]")


class MetroCodeApp(App):
    """Aplicação principal do projeto com interface visual interativa."""

    CSS = """
    Screen {
        background: #020617;
        color: #f8fafc;
    }
    Header {
        background: #0f172a;
        color: #38bdf8;
        text-style: bold;
    }
    #sidebar {
        width: 42%;
        padding: 1 1;
        border: round #38bdf8;
        background: #0f172a;
        margin: 0 1 0 0;
    }
    #content {
        width: 58%;
        padding: 1 1;
        border: round #22c55e;
        background: #0f172a;
        margin: 0 0 0 1;
    }
    .panel-title {
        color: #38bdf8;
        text-style: bold;
        margin-bottom: 1;
    }
    .panel {
        padding: 0 1;
        color: #f8fafc;
    }
    ListView {
        height: 1fr;
        margin-top: 1;
        border: round #334155;
        background: #111827;
    }
    ListItem {
        padding: 0 1;
        background: #111827;
    }
    ListItem.-highlight {
        background: #1d4ed8;
        color: white;
    }
    Static {
        color: #e2e8f0;
    }
    #preview, #details {
        height: 1fr;
        border: round #334155;
        padding: 1 1;
        background: #111827;
    }
    """

    def __init__(self, project_path: str | Path = ".", *, mapa_data: dict[str, Any] | None = None):
        super().__init__()
        self.project_path = str(project_path)
        self.mapa_data = mapa_data if mapa_data is not None else parse_project(self.project_path)
        self.station_names = list(self.mapa_data.get("estacoes", {}).keys())

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Static("🧭 Estações", classes="panel-title")
                yield ListView(id="stations")
            with Vertical(id="content"):
                yield Static("🗺️ Mapa visual", id="preview", classes="panel")
                yield Static("🧩 Detalhes da estação", id="details", classes="panel")
        yield Footer()

    def on_mount(self) -> None:
        self.title = "🚇 MetrôCode"
        self.sub_title = f"Analisando: {self.project_path}"
        station_list = self.query_one("#stations", ListView)
        for station in self.station_names:
            station_list.append(ListItem(Static(f"📍 {station}"), id=station))

        if self.station_names:
            station_list.index = 0
            self._refresh_station(self.station_names[0])

    def _refresh_station(self, station_name: str) -> None:
        preview = self.query_one("#preview", Static)
        details = self.query_one("#details", Static)
        preview.update(build_visual_preview(self.mapa_data, selected_station=station_name))
        details.update(build_station_details(self.mapa_data, station_name))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        station_name = event.item.id if getattr(event.item, "id", None) else None
        if station_name:
            self._refresh_station(station_name)


class MetroApp(MetroCodeApp):
    """Alias compatível com versões anteriores do projeto."""


def main(argv: list[str] | None = None) -> None:
    args = list(sys.argv[1:] if argv is None else argv)
    path = "."
    output_format = "ui"
    export_path: str | None = None
    export_format = "png"
    export_layout = "metro"

    for arg in args:
        if arg in {"--help", "-h"}:
            print("Uso: metrocode [caminho] [--json] [--text]")
            return
        if arg in {"--json", "-j"}:
            output_format = "json"
        elif arg in {"--text", "-t"}:
            output_format = "text"
        elif arg in {"--export", "-e"}:
            # next non-flag argument will be treated as export path
            # handled below when encountering a non-flag
            export_path = None
        elif arg.startswith("--format="):
            export_format = arg.split("=", 1)[1]
        elif arg.startswith("--layout="):
            export_layout = arg.split("=", 1)[1]
        elif not arg.startswith("-"):
            if path == ".":
                path = arg
            else:
                # use second positional as export target
                export_path = arg

    mapa_data = parse_project(path)

    if output_format == "json":
        print(json.dumps(mapa_data, indent=2, ensure_ascii=False))
        return

    # export image if requested: --export <path> [--format=png|svg] [--layout=metro|geografico|circular]
    if export_path:
        out = export_map_image(mapa_data, output=export_path, fmt=export_format, layout_mode=export_layout)
        print(f"Exportado: {out}")
        return

    if output_format == "text" or not sys.stdout.isatty():
        print(build_summary(mapa_data))
        return

    run_visual_dashboard(mapa_data)


if __name__ == "__main__":
    main()