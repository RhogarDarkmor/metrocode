from metrocode.app import (
    MetroApp,
    MetroCodeApp,
    build_summary,
    build_visual_preview,
    export_map_image,
    run_interactive_console,
    run_visual_dashboard,
)
from metrocode.parser import parse_project


def test_app_imports():
    assert MetroCodeApp is not None
    assert MetroApp is not None


def test_parse_project_collects_files_and_nodes(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text(
        "from os import path\n\n"
        "class Example:\n"
        "    def run(self):\n"
        "        return path.isdir('.')\n\n"
        "def helper():\n"
        "    return 42\n",
        encoding="utf-8",
    )

    data = parse_project(tmp_path)

    assert "sample.py" in data["estacoes"]
    station = data["estacoes"]["sample.py"]
    assert station["total_plataformas"] >= 2
    assert any(platform["nome"] == "Example" for platform in station["plataformas"])
    assert station["total_trilhos"] >= 1


def test_build_summary_renders_station_names(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text(
        "class Example:\n" "    def run(self):\n" "        return 1\n",
        encoding="utf-8",
    )

    data = parse_project(tmp_path)
    summary = build_summary(data)

    assert "sample.py" in summary
    assert "Example" in summary


def test_run_interactive_console_shows_station_details(monkeypatch, capsys, tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text(
        "class Example:\n" "    def run(self):\n" "        return 1\n",
        encoding="utf-8",
    )

    data = parse_project(tmp_path)
    inputs = iter(["2", "sample.py", "q"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    run_interactive_console(data)

    output = capsys.readouterr().out
    assert "Detalhes da estação" in output
    assert "sample.py" in output
    assert "Example" in output


def test_build_visual_preview_includes_station_names(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text(
        "class Example:\n" "    def run(self):\n" "        return 1\n",
        encoding="utf-8",
    )

    data = parse_project(tmp_path)
    preview = build_visual_preview(data)

    assert "Mapa visual" in preview
    assert "sample.py" in preview


def test_run_visual_dashboard_renders_header(monkeypatch, capsys, tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text(
        "class Example:\n" "    def run(self):\n" "        return 1\n",
        encoding="utf-8",
    )

    data = parse_project(tmp_path)
    monkeypatch.setattr("builtins.input", lambda prompt="": "q")

    run_visual_dashboard(data)

    output = capsys.readouterr().out
    assert "METRÔCODE" in output
    assert "sample.py" in output


def test_export_map_creates_file(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text(
        "class Example:\n" "    def run(self):\n" "        return 1\n",
        encoding="utf-8",
    )

    data = parse_project(tmp_path)
    out = tmp_path / "out.png"

    try:
        import matplotlib  # type: ignore
    except Exception:
        # ambiente sem matplotlib: não falhar o teste
        return

    path = export_map_image(data, output=str(out), fmt="png", layout_mode="metro")

    assert path == str(out)
    assert out.exists()


def test_export_map_creates_svg(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text(
        "class Example:\n" "    def run(self):\n" "        return 1\n",
        encoding="utf-8",
    )

    data = parse_project(tmp_path)
    out = tmp_path / "out.svg"

    try:
        import matplotlib  # type: ignore
    except Exception:
        return

    path = export_map_image(data, output=str(out), fmt="svg", layout_mode="metro")

    assert path == str(out)
    assert out.exists()
