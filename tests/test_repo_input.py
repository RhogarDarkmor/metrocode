import zipfile
from pathlib import Path

from metrocode.app import (
    _download_and_extract_zip,
    _is_github_shorthand,
    _is_zip_path,
    _to_github_url,
)
from metrocode.parser import parse_project


def test_github_shorthand_and_url():
    assert _is_github_shorthand("psf/requests")
    assert not _is_github_shorthand("https://github.com/psf/requests")
    assert _to_github_url("psf/requests") == "https://github.com/psf/requests.git"


def test_is_zip_path_and_extract(tmp_path):
    # criar um zip simples com um arquivo Python dentro
    src_dir = tmp_path / "srcproj"
    src_dir.mkdir()
    sample = src_dir / "sample.py"
    sample.write_text("def hello():\n    return 1\n", encoding="utf-8")

    zip_path = tmp_path / "proj.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        z.write(sample, arcname="sample.py")

    assert _is_zip_path(str(zip_path))

    dest = tmp_path / "out"
    dest.mkdir()

    _download_and_extract_zip(str(zip_path), str(dest))

    extracted = dest / "sample.py"
    assert extracted.exists()

    # parse_project should find the extracted file
    data = parse_project(dest)
    assert "sample.py" in data["estacoes"]
