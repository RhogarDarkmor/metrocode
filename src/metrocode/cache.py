"""
MetrôCode - Cache de análise.

Para projetos grandes, reparsar tudo a cada execução é lento.
Este módulo oferece cache persistente usando JSON.

Educativo:
- Mostra como usar cache para otimizar performance
- Demonstrates hashing para detecção de mudanças
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

from .types import MetroMap, Platform, Station, Track

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Gerencia cache de análises do MetrôCode.

    A cache armazena:
    - O mapa já processado (em JSON)
    - Hash dos arquivos analisados (para detectar mudanças)

    Uso:
        cache = CacheManager()
        mapa = cache.carregar("meu_projeto")
        if mapa is None:
            mapa = parse_project("meu_projeto")
            cache.salvar("meu_projeto", mapa)
    """

    def __init__(self, cache_dir: str | Path = ".metrocode_cache"):
        """Inicializa o gerenciador de cache."""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def _get_cache_path(self, root: str | Path) -> Path:
        """Retorna o caminho do arquivo de cache para um projeto."""
        root_str = str(root).replace("\\", "/").replace(":", "-")
        return self.cache_dir / f"{root_str}.json"

    def _get_hash_path(self, root: str | Path) -> Path:
        """Retorna o caminho do arquivo de hashes dos arquivos."""
        root_str = str(root).replace("\\", "/").replace(":", "-")
        return self.cache_dir / f"{root_str}.hashes.json"

    def _calcular_hash_projeto(self, root: Path) -> dict[str, str]:
        """Calcula hash de todos os arquivos .py no projeto."""
        hashes = {}

        for arquivo in sorted(root.rglob("*.py")):
            if "_is_ignored_path" in str(arquivo):  # Será implementado em parser
                continue

            try:
                conteudo = arquivo.read_bytes()
                hash_value = hashlib.md5(conteudo).hexdigest()
                rel_path = str(arquivo.relative_to(root))
                hashes[rel_path] = hash_value
            except (OSError, IOError):
                continue

        return hashes

    def _hashes_mudaram(self, root: Path) -> bool:
        """Verifica se algum arquivo foi modificado."""
        cache_hashes = self._load_hashes(root)
        current_hashes = self._calcular_hash_projeto(root)

        if len(cache_hashes) != len(current_hashes):
            return True

        for arquivo, hash_atual in current_hashes.items():
            if arquivo not in cache_hashes or cache_hashes[arquivo] != hash_atual:
                return True

        return False

    def _load_hashes(self, root: str | Path) -> dict[str, str]:
        """Carrega hashes salvos anteriormente."""
        hash_path = self._get_hash_path(root)
        if hash_path.exists():
            try:
                with open(hash_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}

    def _save_hashes(self, root: Path) -> None:
        """Salva hashes dos arquivos atuais."""
        hashes = self._calcular_hash_projeto(root)
        hash_path = self._get_hash_path(root)

        with open(hash_path, "w", encoding="utf-8") as f:
            json.dump(hashes, f, indent=2)

    def carregar(self, root: str | Path, ignorar_cache: bool = False) -> MetroMap | None:
        """
        Carrega o mapa do cache se disponível e válido.

        Args:
            root: Diretório raiz do projeto
            ignorar_cache: Se True, ignora o cache e retorna None

        Returns:
            MetroMap se cache válido, None se não existir ou estiver inválido
        """
        if ignorar_cache:
            return None

        root_path = Path(root).resolve()
        cache_path = self._get_cache_path(root_path)

        # Verificar se cache existe
        if not cache_path.exists():
            logger.debug(f"Cache não encontrado para {root}")
            return None

        # Verificar se arquivos mudaram
        if self._hashes_mudaram(root_path):
            logger.debug(f"Arquivos mudaram, cache inválido para {root}")
            return None

        # Carregar e desserializar cache
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            return self._deserializar_mapa(data, root_path)
        except (json.JSONDecodeError, IOError, KeyError) as e:
            logger.warning(f"Erro ao carregar cache: {e}")
            return None

    def salvar(self, mapa: MetroMap) -> None:
        """
        Salva o mapa em cache.

        Args:
            mapa: MetroMap a ser salvo
        """
        root_path = Path(mapa.root).resolve()
        cache_path = self._get_cache_path(root_path)

        try:
            data = self._serializar_mapa(mapa)

            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self._save_hashes(root_path)
            logger.debug(f"Cache salvo para {root_path}")
        except (IOError, TypeError) as e:
            logger.warning(f"Erro ao salvar cache: {e}")

    def limpar(self, root: str | Path | None = None) -> None:
        """
        Limpa o cache.

        Args:
            root: Se None, limpa tudo; senão limpa apenas o projeto especificado
        """
        if root is None:
            # Limpar tudo
            for arquivo in self.cache_dir.glob("*.json"):
                arquivo.unlink()
            logger.info("Cache completo limpo")
        else:
            # Limpar específico
            root_path = Path(root).resolve()
            self._get_cache_path(root_path).unlink(missing_ok=True)
            self._get_hash_path(root_path).unlink(missing_ok=True)
            logger.info(f"Cache limpo para {root}")

    @staticmethod
    def _serializar_mapa(mapa: MetroMap) -> dict[str, Any]:
        """Converte MetroMap para dicionário JSON-serializable."""
        return {
            "root": str(mapa.root),
            "estacoes": {
                nome: {
                    "modulo": estacao.modulo,
                    "plataformas": [
                        {
                            "nome": p.nome,
                            "tipo": p.tipo,
                            "linha": p.linha,
                            "metodos": [
                                {
                                    "nome": m.nome,
                                    "tipo": m.tipo,
                                    "linha": m.linha,
                                }
                                for m in p.metodos
                            ],
                            "doc": p.doc,
                        }
                        for p in estacao.plataformas
                    ],
                    "trilhos": [
                        {
                            "tipo": t.tipo,
                            "modulo": t.modulo,
                            "nome": t.nome,
                            "alias": t.alias,
                            "qualificado": t.qualificado,
                            "nivel": t.nivel,
                        }
                        for t in estacao.trilhos
                    ],
                }
                for nome, estacao in mapa.estacoes.items()
            },
            "ciclos": mapa.ciclos,
            "modulo_externo_contador": mapa.modulo_externo_contador,
        }

    @staticmethod
    def _deserializar_mapa(
        data: dict[str, Any], root: Path
    ) -> MetroMap:
        """Reconstrói MetroMap a partir de dicionário JSON."""
        estacoes: dict[str, Station] = {}

        for nome, dados_estacao in data.get("estacoes", {}).items():
            plataformas = [
                Platform(
                    nome=p["nome"],
                    tipo=p["tipo"],  # type: ignore
                    linha=p["linha"],
                    metodos=[
                        Platform(
                            nome=m["nome"],
                            tipo=m["tipo"],  # type: ignore
                            linha=m["linha"],
                        )
                        for m in p.get("metodos", [])
                    ],
                    doc=p.get("doc"),
                )
                for p in dados_estacao.get("plataformas", [])
            ]

            trilhos = [
                Track(
                    tipo=t["tipo"],  # type: ignore
                    modulo=t["modulo"],
                    nome=t.get("nome"),
                    alias=t.get("alias"),
                    qualificado=t.get("qualificado"),
                    nivel=t.get("nivel", 0),
                )
                for t in dados_estacao.get("trilhos", [])
            ]

            estacoes[nome] = Station(
                nome=nome,
                modulo=dados_estacao["modulo"],
                plataformas=plataformas,
                trilhos=trilhos,
            )

        return MetroMap(
            root=root,
            estacoes=estacoes,
            ciclos=data.get("ciclos", []),
            modulo_externo_contador=data.get("modulo_externo_contador", {}),
        )
