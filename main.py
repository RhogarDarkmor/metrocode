import sys
import json
from pathlib import Path
from tkinter import Tk, filedialog
import webview
from parser.python_parser import parse_project
from graph.metro_graph import build_metro_map

# HTML da interface com etapas
PAGE_HTML = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>MetroCode</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #0d1117; color: #c9d1d9; height: 100vh; overflow: hidden; }
        /* Telas */
        .screen { display: none; width: 100%; height: 100%; flex-direction: column; align-items: center; justify-content: center; gap: 30px; }
        .screen.active { display: flex; }
        /* Loader */
        .loader {
            width: 60px; padding: 8px; aspect-ratio: 1; border-radius: 50%;
            background: #0055FF;
            --_m: conic-gradient(#0000 10%, #000), linear-gradient(#000 0 0) content-box;
            -webkit-mask: var(--_m); mask: var(--_m);
            -webkit-mask-composite: source-out; mask-composite: subtract;
            animation: l3 1s infinite linear, colorShift 10s infinite ease-in-out alternate;
        }
        @keyframes l3 { to { transform: rotate(1turn); } }
        @keyframes colorShift {
            0% { background: #0055FF; } 20% { background: #00CC44; } 40% { background: #FF0044; }
            60% { background: #FFCC00; } 80% { background: #C084FC; } 100% { background: #C0C0C0; }
        }
        .status { font-size: 1.2rem; color: #c9d1d9; }
        .status span { color: #58a6ff; font-weight: bold; }
        /* Botões */
        .btn {
            padding: 15px 30px; background: #0055FF; color: white; border: none;
            border-radius: 10px; font-size: 1.1rem; cursor: pointer; transition: background 0.3s;
        }
        .btn:hover { background: #003bb3; }
        .btn:disabled { background: #555; cursor: not-allowed; }
        .folder-path { font-size: 1rem; color: #58a6ff; }
        /* Mapa */
        #map-container { width: 100%; height: 100vh; }
        svg { width: 100%; height: 100%; background: #1a1e24; }
        .estacao circle { cursor: pointer; transition: r 0.2s; }
        .estacao circle:hover { r: 14; }
        .tooltip {
            position: absolute; background: #2d333b; color: #c9d1d9; padding: 8px 12px;
            border-radius: 8px; font-size: 0.9rem; pointer-events: none; opacity: 0;
            transition: opacity 0.2s; white-space: nowrap; z-index: 1000;
        }
    </style>
</head>
<body>
    <!-- Tela 1: Seleção da pasta -->
    <div id="screen-select" class="screen active">
        <h1>MetroCode</h1>
        <p>Selecione a pasta do projeto para começar</p>
        <button class="btn" onclick="selecionarPasta()">Selecionar Pasta</button>
        <p id="folder-path" class="folder-path" style="display:none;"></p>
    </div>

    <!-- Tela 2: Iniciar mapeamento -->
    <div id="screen-start" class="screen">
        <h2>Pasta selecionada:</h2>
        <p id="selected-folder" class="folder-path"></p>
        <button class="btn" onclick="iniciarMapeamento()">Iniciar Mapeamento</button>
    </div>

    <!-- Tela 3: Loader durante análise -->
    <div id="screen-loading" class="screen">
        <div class="loader"></div>
        <div class="status">Analisando código e construindo <span>MetroCode</span>...</div>
    </div>

    <!-- Tela 4: Mapa (inicialmente oculta) -->
    <div id="screen-map" class="screen" style="display:none;">
        <svg id="metro-svg"></svg>
        <div class="tooltip" id="tooltip"></div>
    </div>

    <script>
        let pastaSelecionada = null;

        async function selecionarPasta() {
            try {
                pastaSelecionada = await pywebview.api.selecionar_pasta();
                if (pastaSelecionada) {
                    document.getElementById('folder-path').textContent = pastaSelecionada;
                    document.getElementById('folder-path').style.display = 'block';
                    mostrarTela('screen-start');
                    document.getElementById('selected-folder').textContent = pastaSelecionada;
                }
            } catch (e) {
                console.error(e);
            }
        }

        async function iniciarMapeamento() {
            mostrarTela('screen-loading');
            try {
                const dados = await pywebview.api.processar_pasta();
                mostrarMapa(dados);
            } catch (erro) {
                alert('Erro: ' + erro);
                mostrarTela('screen-select');
            }
        }

        function mostrarTela(id) {
            document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
            document.getElementById(id).classList.add('active');
        }

        // Função que desenha o mapa (mantida da versão anterior, com melhorias visuais)
        function mostrarMapa(data) {
            const mapScreen = document.getElementById('screen-map');
            mapScreen.style.display = 'flex';  // mostrar tela do mapa
            mostrarTela('screen-map');

            const svg = document.getElementById('metro-svg');
            const tooltip = document.getElementById('tooltip');
            const width = mapScreen.clientWidth;
            const height = mapScreen.clientHeight;
            svg.setAttribute('viewBox', `0 0 ${width} ${height}`);

            // Limpar SVG anterior, se houver
            svg.innerHTML = '';

            const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            svg.appendChild(g);

            let isPanning = false, startX, startY, translateX = 0, translateY = 0, scale = 1;

            svg.addEventListener('mousedown', (e) => {
                isPanning = true;
                startX = e.clientX - translateX;
                startY = e.clientY - translateY;
            });
            svg.addEventListener('mousemove', (e) => {
                if (isPanning) {
                    translateX = e.clientX - startX;
                    translateY = e.clientY - startY;
                    atualizarTransformacao();
                }
                tooltip.style.left = (e.pageX + 15) + 'px';
                tooltip.style.top = (e.pageY - 30) + 'px';
            });
            svg.addEventListener('mouseup', () => isPanning = false);
            svg.addEventListener('mouseleave', () => isPanning = false);
            svg.addEventListener('wheel', (e) => {
                e.preventDefault();
                const fator = e.deltaY > 0 ? 0.9 : 1.1;
                scale *= fator;
                scale = Math.min(Math.max(0.3, scale), 2);
                atualizarTransformacao();
            });

            function atualizarTransformacao() {
                g.setAttribute('transform', `translate(${translateX},${translateY}) scale(${scale})`);
            }

            const estacoesMap = new Map(data.estacoes.map(e => [e.id, e]));

            // Desenhar arestas (linhas de conexão)
            data.arestas.forEach(a => {
                const de = estacoesMap.get(a.de);
                const para = estacoesMap.get(a.para);
                if (!de || !para) return;
                const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                const dx = para.x - de.x, dy = para.y - de.y;
                const dr = Math.sqrt(dx*dx + dy*dy) * 1.5;
                const d = `M${de.x},${de.y}A${dr},${dr} 0 0,1 ${para.x},${para.y}`;
                path.setAttribute('d', d);
                path.setAttribute('fill', 'none');
                path.setAttribute('stroke', a.tipo === 'baldeacao' ? '#f0f0f0' : de.cor_linha);
                path.setAttribute('stroke-width', a.tipo === 'baldeacao' ? 2.5 : 4);
                path.setAttribute('stroke-dasharray', a.tipo === 'baldeacao' ? '8,4' : 'none');
                path.setAttribute('opacity', 0.8);
                g.appendChild(path);
            });

            // Desenhar estações
            data.estacoes.forEach(est => {
                const grupo = document.createElementNS('http://www.w3.org/2000/svg', 'g');
                grupo.setAttribute('transform', `translate(${est.x},${est.y})`);
                grupo.classList.add('estacao');

                // Verificar se é estação de baldeação (conectada a mais de um arquivo)
                const arquivosConectados = new Set();
                data.arestas.forEach(a => {
                    if (a.de === est.id) arquivosConectados.add(estacoesMap.get(a.para)?.arquivo);
                    if (a.para === est.id) arquivosConectados.add(estacoesMap.get(a.de)?.arquivo);
                });
                const ehBaldeacao = arquivosConectados.size > 1;

                if (ehBaldeacao) {
                    // Desenhar losango (baldeação)
                    const losango = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
                    const size = 14;
                    const points = `0,${-size} ${size},0 0,${size} ${-size},0`;
                    losango.setAttribute('points', points);
                    losango.setAttribute('fill', '#ffffff');
                    losango.setAttribute('stroke', est.cor_linha);
                    losango.setAttribute('stroke-width', 3);
                    grupo.appendChild(losango);
                } else {
                    // Círculo normal
                    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                    circle.setAttribute('r', 12);
                    circle.setAttribute('fill', '#ffffff');
                    circle.setAttribute('stroke', est.cor_linha);
                    circle.setAttribute('stroke-width', 4);
                    grupo.appendChild(circle);
                }

                // Nome da estação
                const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                text.setAttribute('dy', -22);
                text.setAttribute('text-anchor', 'middle');
                text.setAttribute('fill', '#c9d1d9');
                text.style.fontSize = '0.7rem';
                text.textContent = est.nome;
                grupo.appendChild(text);

                // Tooltip
                grupo.addEventListener('mouseenter', () => {
                    tooltip.innerHTML = `<strong>${est.nome}</strong><br>${est.resumo}<br><em>${est.arquivo}</em>`;
                    tooltip.style.opacity = 1;
                });
                grupo.addEventListener('mouseleave', () => {
                    tooltip.style.opacity = 0;
                });

                g.appendChild(grupo);
            });

            // Ajustar viewBox para mostrar todas as estações
            setTimeout(() => {
                const bbox = g.getBBox();
                const padding = 100;
                svg.setAttribute('viewBox', `${bbox.x - padding} ${bbox.y - padding} ${bbox.width + 2*padding} ${bbox.height + 2*padding}`);
            }, 100);
        }
    </script>
</body>
</html>
'''

class MetroCodeAPI:
    def __init__(self):
        self.pasta = None

    def selecionar_pasta(self):
        """Abre diálogo nativo e retorna o caminho escolhido."""
        root = Tk()
        root.withdraw()
        pasta = filedialog.askdirectory(title="Selecione a pasta do projeto")
        if pasta:
            self.pasta = pasta
            return pasta
        return None

    def processar_pasta(self):
        """Analisa a pasta e retorna o grafo."""
        if not self.pasta:
            raise Exception("Nenhuma pasta selecionada.")
        print("Analisando código...")
        dados = parse_project(Path(self.pasta))
        grafo = build_metro_map(dados)
        print(f"Análise concluída. {len(grafo['estacoes'])} estações, {len(grafo['arestas'])} conexões.")
        return grafo

def main():
    api = MetroCodeAPI()
    # Cria a janela com o HTML embutido e expõe a API
    webview.create_window("MetroCode", html=PAGE_HTML, js_api=api, width=1200, height=800)
    webview.start()

if __name__ == "__main__":
    main()