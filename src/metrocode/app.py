from __future__ import annotations

import argparse
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any


def _is_github_shorthand(s: str) -> bool:
    """Detecta strings no formato `owner/repo` para GitHub."""
    return bool(re.match(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", s))


def _to_github_url(s: str) -> str:
    """Converte `owner/repo` em URL HTTPS para clonagem."""
    return f"https://github.com/{s}.git"


def _is_zip_path(s: str) -> bool:
    """Detecta se a string aponta para um arquivo zip local ou remoto."""
    return isinstance(s, str) and (
        s.lower().endswith(".zip")
        or s.startswith("http")
        and s.lower().endswith(".zip")
    )


def _download_and_extract_zip(url_or_path: str, dest: str) -> None:
    """Baixa (se URL) e extrai um ZIP para `dest`.

    Aceita tanto caminhos locais quanto URLs HTTP(S).
    """
    dest_path = Path(dest)
    dest_path.mkdir(parents=True, exist_ok=True)

    if url_or_path.startswith("http://") or url_or_path.startswith("https://"):
        with urllib.request.urlopen(url_or_path) as resp:
            data = resp.read()
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        try:
            tmp.write(data)
            tmp.flush()
            with zipfile.ZipFile(tmp.name, "r") as z:
                z.extractall(dest)
        finally:
            tmp.close()
            try:
                os.unlink(tmp.name)
            except Exception:
                pass
    else:
        # caminho local
        with zipfile.ZipFile(url_or_path, "r") as z:
            z.extractall(dest)


def _normalize_station_name(name: str) -> str:
    return name.strip().replace("\\", "/")


from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, ListItem, ListView, Static

from . import __version__
from .graph_builder import construir_grafo
from .layout_engine import calcular_layout
from .parser import parse_project


def build_summary(mapa_data: dict[str, Any]) -> str:
    """Gera um resumo textual legível do mapa do projeto."""
    estacoes = mapa_data.get("estacoes", {})
    if not estacoes:
        return (
            "🚇 Nenhuma estação encontrada. Execute em um diretório com código Python."
        )

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


def build_visual_preview(
    mapa_data: dict[str, Any], selected_station: str | None = None
) -> str:
    """Gera uma pré-visualização visual do mapa em estilo terminal."""
    estacoes = list(mapa_data.get("estacoes", {}).keys())
    if not estacoes:
        return "Mapa visual\nNenhuma estação disponível."

    grupos: dict[str, list[str]] = {}
    for station, dados in mapa_data.get("estacoes", {}).items():
        modulo = dados.get("modulo") or station
        raiz = modulo.split(".")[0]
        grupos.setdefault(raiz, []).append(station)

    linhas = ["Mapa visual", "=" * 28, ""]
    for raiz, stations in sorted(grupos.items()):
        linha = " ─> ".join(stations[:6])
        if len(stations) > 6:
            linha += " ..."
        linhas.append(f"[{raiz}] {linha}")

    if selected_station:
        linhas.append("")
        linhas.append(f"Estação selecionada: {selected_station}")

    return "\n".join(linhas)


def export_map_image(
    mapa_data: dict[str, Any],
    *,
    output: str | Path = "metrocode_map.png",
    fmt: str = "png",
    layout_mode: str = "metro",
) -> str:
    """Exporta o mapa como imagem (PNG ou SVG) usando NetworkX + Matplotlib.

    Retorna o caminho do arquivo gerado.
    """
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import networkx as nx
    except Exception as exc:  # pragma: no cover - environment-specific
        raise RuntimeError(
            "matplotlib e networkx são necessários para exportar imagens"
        ) from exc

    fmt = fmt.lower()
    if fmt not in {"png", "svg"}:
        raise ValueError("Formato de exportação inválido. Use 'png' ou 'svg'.")

    grafo = construir_grafo(mapa_data)
    pos = calcular_layout(grafo, modo=layout_mode)

    station_nodes = [n for n, d in grafo.nodes(data=True) if d.get("tipo") == "estacao"]
    station_graph = grafo.subgraph(station_nodes)

    fig, ax = plt.subplots(figsize=(16, 12))
    fig.patch.set_facecolor("#f8fafc")
    ax.set_facecolor("#f8fafc")

    edge_colors = [
        d.get("cor", "#444444") for _, _, d in station_graph.edges(data=True)
    ]
    edge_widths = [
        4 if d.get("tipo") == "import" else 2
        for _, _, d in station_graph.edges(data=True)
    ]

    nx.draw_networkx_edges(
        station_graph,
        pos,
        ax=ax,
        edge_color=edge_colors,
        width=edge_widths,
        alpha=0.95,
        arrows=False,
    )

    nx.draw_networkx_nodes(
        station_graph,
        pos,
        ax=ax,
        nodelist=station_nodes,
        node_size=760,
        node_color="#ffffff",
        edgecolors="#111827",
        linewidths=2.4,
        alpha=0.98,
    )

    labels = {n: n.rsplit("/", 1)[-1].replace(".py", "") for n in station_nodes}
    for n in station_nodes:
        x, y = pos[n]
        ax.text(
            x,
            y,
            labels[n],
            fontsize=8,
            ha="center",
            va="center",
            color="#111827",
            bbox={
                "facecolor": "#ffffff",
                "edgecolor": "#111827",
                "boxstyle": "round,pad=0.2",
                "alpha": 0.95,
            },
        )

    legend_items = sorted(
        {
            d.get("modulo", "externo").split(".")[0]
            for _, _, d in station_graph.edges(data=True)
            if d.get("modulo")
        }
    )
    if legend_items:
        legend_text = "Linhas: " + ", ".join(legend_items[:10])
        ax.text(
            0.02,
            0.98,
            legend_text,
            transform=ax.transAxes,
            fontsize=8,
            va="top",
            ha="left",
            bbox={
                "facecolor": "#ffffff",
                "edgecolor": "#111827",
                "boxstyle": "round,pad=0.3",
                "alpha": 0.95,
            },
        )

    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()

    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, format=fmt, dpi=200)
    import matplotlib.pyplot as _plt

    _plt.close(fig)

    return str(out_path)


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
            qualificado = trilho.get("qualificado")
            modulo = trilho.get("modulo")
            nome = trilho.get("nome")
            alias = trilho.get("alias")
            descricao = qualificado or modulo or nome or "import desconhecido"
            if alias:
                descricao += f" as {alias}"
            linhas.append(f"   - {descricao}")

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
        console.print(
            Panel.fit(
                "🚇 Nenhuma estação disponível", title="MetrôCode", border_style="red"
            )
        )
        return

    while True:
        console.clear()
        console.print(
            Panel.fit(
                "[bold cyan]🚇 METRÔCODE[/bold cyan]\n[dim]Mapa visual interativo do projeto[/dim]",
                border_style="cyan",
            )
        )

        table = Table(title="Estações", show_header=True, header_style="bold magenta")
        table.add_column("#", justify="right", style="cyan")
        table.add_column("Estação", style="white")
        table.add_column("Plataformas", justify="right", style="green")
        table.add_column("Trilhos", justify="right", style="yellow")

        for index, station_name in enumerate(station_names[:10], start=1):
            dados = estacoes[station_name]
            table.add_row(
                str(index),
                station_name,
                str(dados.get("total_plataformas", 0)),
                str(dados.get("total_trilhos", 0)),
            )

        console.print(table)
        console.print(
            "[bold]Comandos:[/bold] digite o número da estação para ver detalhes ou [q] para sair"
        )

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
                console.print(
                    Panel.fit(
                        build_station_details(mapa_data, station_name),
                        title=f"Detalhes: {station_name}",
                        border_style="green",
                    )
                )
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

    def __init__(
        self, project_path: str | Path = ".", *, mapa_data: dict[str, Any] | None = None
    ):
        super().__init__()
        self.project_path = str(project_path)
        self.mapa_data = (
            mapa_data if mapa_data is not None else parse_project(self.project_path)
        )
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
        preview.update(
            build_visual_preview(self.mapa_data, selected_station=station_name)
        )
        details.update(build_station_details(self.mapa_data, station_name))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        station_name = event.item.id if getattr(event.item, "id", None) else None
        if station_name:
            self._refresh_station(station_name)


class MetroApp(MetroCodeApp):
    """Alias compatível com versões anteriores do projeto."""


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="metrocode", description="Gera um mapa interativo do código fonte"
    )
    parser.add_argument(
        "--version", action="version", version=f"metrocode {__version__}"
    )
    parser.add_argument(
        "path", nargs="?", default=".", help="Caminho local, URL git, owner/repo ou ZIP"
    )
    parser.add_argument(
        "--json",
        "-j",
        dest="output",
        action="store_const",
        const="json",
        help="Saída em JSON",
    )
    parser.add_argument(
        "--text",
        "-t",
        dest="output",
        action="store_const",
        const="text",
        help="Saída em texto",
    )
    parser.add_argument(
        "--no-gui",
        dest="use_ui",
        action="store_false",
        default=True,
        help="Executar em modo texto, mesmo em terminal interativo",
    )
    parser.add_argument(
        "--export",
        "-e",
        dest="export_path",
        help="Exportar mapa para arquivo (png/svg)",
    )
    parser.add_argument(
        "--format",
        dest="export_format",
        default="png",
        help="Formato de exportação (png|svg)",
    )
    parser.add_argument(
        "--layout",
        dest="export_layout",
        default="metro",
        help="Modo de layout (metro|geografico|circular)",
    )
    parser.add_argument(
        "--no-clean",
        dest="no_clean",
        action="store_true",
        help="Manter arquivos temporários (clone/zip)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="count",
        default=0,
        help="Aumentar verbosidade (mais -v aumenta nível)",
    )
    parser.add_argument(
        "--log-file",
        dest="log_file",
        default="metrocode.log",
        help="Arquivo de log de saída",
    )

    parsed = parser.parse_args(argv)

    # configurar logging
    level = logging.WARNING
    if parsed.verbose >= 2:
        level = logging.DEBUG
    elif parsed.verbose == 1:
        level = logging.INFO

    handlers = [logging.StreamHandler()]
    if parsed.log_file:
        handlers.append(
            RotatingFileHandler(
                parsed.log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
            )
        )

    logging.basicConfig(
        level=level, format="%(asctime)s %(levelname)s: %(message)s", handlers=handlers
    )

    path = parsed.path
    output_format = parsed.output or "ui"
    use_ui = parsed.use_ui
    export_path: str | None = parsed.export_path
    export_format = parsed.export_format
    export_layout = parsed.export_layout
    no_clean = parsed.no_clean
    log_file = parsed.log_file

    def _cleanup(temp_clone: str | None, temp_extracted: str | None) -> None:
        if no_clean:
            if temp_clone:
                print(f"Clone temporário mantido em: {temp_clone}")
            if temp_extracted:
                print(f"ZIP extraído em: {temp_extracted}")
            return

        if temp_clone and os.path.exists(temp_clone):
            logging.debug("Removendo clone temporário %s", temp_clone)
            shutil.rmtree(temp_clone)
        if temp_extracted and os.path.exists(temp_extracted):
            logging.debug("Removendo extração temporária %s", temp_extracted)
            shutil.rmtree(temp_extracted)

    _temp_clone: str | None = None
    _temp_extracted: str | None = None
    try:
        # aceitar shorthand "owner/repo"
        if (
            isinstance(path, str)
            and _is_github_shorthand(path)
            and not Path(path).exists()
        ):
            logging.info("Interpretando shorthand GitHub %s", path)
            path = _to_github_url(path)

        # ZIP remoto/local
        if isinstance(path, str) and _is_zip_path(path):
            logging.info("Detectado ZIP %s — extraindo para temporário", path)
            _temp_extracted = tempfile.mkdtemp(prefix="metrocode_zip_")
            try:
                _download_and_extract_zip(path, _temp_extracted)
                path = _temp_extracted
            except Exception as exc:  # pragma: no cover - env-specific
                logging.error("Erro ao extrair ZIP %s: %s", path, exc)
                if os.path.exists(_temp_extracted):
                    shutil.rmtree(_temp_extracted)
                return

        if (
            isinstance(path, str)
            and (
                path.startswith("http://")
                or path.startswith("https://")
                or path.startswith("git@")
            )
            and "github.com" in path
        ):
            logging.info("Clonando repositório %s", path)
            _temp_clone = tempfile.mkdtemp(prefix="metrocode_git_")
            try:
                if shutil.which("git") is None:
                    raise RuntimeError(
                        "git não encontrado no PATH; instale o Git para usar repositórios remotos"
                    )
                subprocess.check_call(
                    ["git", "clone", "--depth", "1", path, _temp_clone],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                path = _temp_clone
            except Exception as exc:  # pragma: no cover - environment-specific
                logging.error("Erro ao clonar o repositório %s: %s", path, exc)
                if os.path.exists(_temp_clone):
                    shutil.rmtree(_temp_clone)
                return

        mapa_data = parse_project(path)

        if output_format == "json":
            print(json.dumps(mapa_data, indent=2, ensure_ascii=False))
            return

        if export_path:
            out = export_map_image(
                mapa_data,
                output=export_path,
                fmt=export_format,
                layout_mode=export_layout,
            )
            print(f"Exportado: {out}")
            return

        if output_format == "text" or not use_ui or not sys.stdout.isatty():
            print(build_summary(mapa_data))
            return

        run_visual_dashboard(mapa_data)
    finally:
        _cleanup(_temp_clone, _temp_extracted)


if __name__ == "__main__":
    main()
