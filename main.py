import sys
import json
from pathlib import Path
from tkinter import Tk, filedialog
import webview
from parser.python_parser import parse_project
from graph.metro_graph import build_metro_map

PAGE_HTML = r'''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>MetroCode</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #0d1117; color: #c9d1d9; height: 100vh; overflow: hidden; }

        .screen { display: none; width: 100%; height: 100%; flex-direction: column; align-items: center; justify-content: center; gap: 30px; }
        .screen.active { display: flex; }

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

        .btn {
            padding: 15px 30px; background: #0055FF; color: white; border: none;
            border-radius: 10px; font-size: 1.1rem; cursor: pointer; transition: background 0.3s;
        }
        .btn:hover { background: #003bb3; }
        .btn:disabled { background: #555; cursor: not-allowed; }
        .btn-secondary { background: #444; }
        .btn-secondary:hover { background: #555; }
        .folder-path { font-size: 1rem; color: #58a6ff; }

        #screen-map { position: relative; }
        #map-container { width: 100%; height: 100vh; }
        svg { width: 100%; height: 100%; background: #1a1e24; cursor: grab; }
        svg:active { cursor: grabbing; }

        .estacao circle { cursor: pointer; transition: r 0.2s; }
        .estacao circle:hover { r: 14; }

        .tooltip {
            position: absolute; background: #2d333b; color: #c9d1d9; padding: 8px 12px;
            border-radius: 8px; font-size: 0.9rem; pointer-events: none; opacity: 0;
            transition: opacity 0.2s; white-space: nowrap; z-index: 1000;
        }

        .map-controls {
            position: absolute; bottom: 20px; right: 20px; 
            z-index: 2000;
            background: rgba(13,17,23,0.9);
            padding: 10px;
            border-radius: 12px;
            border: 1px solid #444;
            display: flex; flex-wrap: wrap; gap: 10px;
            max-width: calc(100% - 40px); max-height: 50vh; overflow-y: auto;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        }
        .map-controls button {
            background: #2d333b; color: #c9d1d9; border: 1px solid #555;
            border-radius: 6px; padding: 8px 14px; cursor: pointer; font-size: 0.9rem;
            white-space: nowrap; transition: background 0.2s;
        }
        .map-controls button:hover { background: #3a414a; }

        .legend {
            position: absolute; bottom: 20px; left: 20px;
            background: rgba(13,17,23,0.9); padding: 15px;
            border-radius: 10px; border: 1px solid #444; z-index: 500;
            display: flex; flex-wrap: wrap; gap: 10px; max-width: 300px;
            max-height: 40vh; overflow-y: auto;
        }
        .legend-item { display: flex; align-items: center; gap: 8px; font-size: 0.8rem; }
        .legend-color { width: 16px; height: 16px; border-radius: 4px; }
    </style>
</head>
<body>
    <div id="screen-select" class="screen active">
        <h1>MetroCode</h1>
        <p>Selecione a pasta do projeto para começar</p>
        <button class="btn" onclick="selecionarPasta()">Selecionar Pasta</button>
        <button class="btn btn-secondary" onclick="carregarMapaSalvo()">Carregar Mapa Salvo</button>
        <p id="folder-path" class="folder-path" style="display:none;"></p>
    </div>

    <div id="screen-start" class="screen">
        <h2>Pasta selecionada:</h2>
        <p id="selected-folder" class="folder-path"></p>
        <button class="btn" onclick="iniciarMapeamento()">Iniciar Mapeamento</button>
    </div>

    <div id="screen-loading" class="screen">
        <div class="loader"></div>
        <div class="status">Analisando código e construindo <span>MetroCode</span>...</div>
    </div>

    <div id="screen-map" class="screen" style="display:none;">
        <div class="map-controls">
            <button onclick="voltarParaInicio()">↩ Voltar</button>
            <button onclick="salvarMapa()">💾 Salvar Mapa</button>
            <button id="btn-zoom-in" title="Zoom +">🔍+</button>
            <button id="btn-zoom-out" title="Zoom -">🔍-</button>
            <button id="btn-zoom-reset" title="Resetar Zoom">↺</button>
        </div>
        <div id="map-container">
            <svg id="metro-svg"></svg>
            <div class="tooltip" id="tooltip"></div>
        </div>
        <div id="legend" class="legend" style="display:none;"></div>
    </div>

    <script>
        let pastaSelecionada = null;
        let dadosMapa = null;

        async function selecionarPasta() {
            try {
                pastaSelecionada = await pywebview.api.selecionar_pasta();
                if (pastaSelecionada) {
                    document.getElementById('folder-path').textContent = pastaSelecionada;
                    document.getElementById('folder-path').style.display = 'block';
                    mostrarTela('screen-start');
                    document.getElementById('selected-folder').textContent = pastaSelecionada;
                }
            } catch (e) { alert('Erro ao selecionar pasta: ' + e); }
        }

        async function carregarMapaSalvo() {
            try {
                const jsonStr = await pywebview.api.carregar_json();
                if (jsonStr) {
                    dadosMapa = JSON.parse(jsonStr);
                    mostrarMapa(dadosMapa);
                }
            } catch (e) { alert('Erro ao carregar mapa: ' + e); }
        }

        async function iniciarMapeamento() {
            mostrarTela('screen-loading');
            try {
                dadosMapa = await pywebview.api.processar_pasta();
                if (!dadosMapa || dadosMapa.estacoes.length === 0) {
                    alert('Nenhuma função encontrada nos arquivos Python.');
                    mostrarTela('screen-select');
                    return;
                }
                mostrarMapa(dadosMapa);
            } catch (erro) {
                alert('Erro na análise: ' + erro);
                mostrarTela('screen-select');
            }
        }

        function voltarParaInicio() {
            const mapScreen = document.getElementById('screen-map');
            mapScreen.classList.remove('active');
            mapScreen.style.display = 'none';
            dadosMapa = null;
            pastaSelecionada = null;
            mostrarTela('screen-select');
            document.getElementById('folder-path').style.display = 'none';
            document.getElementById('metro-svg').innerHTML = '';
            document.getElementById('legend').innerHTML = '';
            document.getElementById('legend').style.display = 'none';
        }

        function salvarMapa() {
            if (!dadosMapa) return;
            const blob = new Blob([JSON.stringify(dadosMapa, null, 2)], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'metromap.json';
            a.click();
            URL.revokeObjectURL(url);
        }

        function mostrarTela(id) {
            document.querySelectorAll('.screen').forEach(s => {
                s.classList.remove('active');
                if (s.id !== 'screen-map') s.style.display = '';
            });
            document.getElementById(id).classList.add('active');
            if (id === 'screen-map') document.getElementById('screen-map').style.display = 'flex';
        }

        // ========== MAPA OTIMIZADO (pan uniforme, zoom 200x) ==========
        function mostrarMapa(data) {
            dadosMapa = data;
            const mapScreen = document.getElementById('screen-map');
            mapScreen.style.display = 'flex';
            mapScreen.classList.add('active');
            document.querySelectorAll('.screen').forEach(s => { if (s.id !== 'screen-map') s.classList.remove('active'); });

            const svg = document.getElementById('metro-svg');
            const tooltip = document.getElementById('tooltip');
            const container = document.getElementById('map-container');

            // Força proporção 1:1 entre coordenadas e pixels (sem distorção)
            svg.setAttribute('preserveAspectRatio', 'none');
            svg.innerHTML = '';

            const estacoesMap = new Map(data.estacoes.map(e => [e.id, e]));
            const arquivosUnicos = [...new Set(data.estacoes.map(e => e.arquivo))];
            const coresArquivo = {};
            data.estacoes.forEach(e => { if (!coresArquivo[e.arquivo]) coresArquivo[e.arquivo] = e.cor_linha; });

            // ---- Desenhar arestas (linhas retas) ----
            data.arestas.forEach(a => {
                const de = estacoesMap.get(a.de);
                const para = estacoesMap.get(a.para);
                if (!de || !para) return;
                const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                line.setAttribute('x1', de.x);
                line.setAttribute('y1', de.y);
                line.setAttribute('x2', para.x);
                line.setAttribute('y2', para.y);
                line.setAttribute('stroke', a.tipo === 'baldeacao' ? '#f0f0f0' : de.cor_linha);
                line.setAttribute('stroke-width', a.tipo === 'baldeacao' ? 2.5 : 4);
                line.setAttribute('stroke-dasharray', a.tipo === 'baldeacao' ? '8,4' : 'none');
                line.setAttribute('opacity', 0.8);
                svg.appendChild(line);
            });

            // ---- Desenhar estações ----
            data.estacoes.forEach(est => {
                const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
                g.setAttribute('transform', `translate(${est.x},${est.y})`);
                g.classList.add('estacao');

                const arquivosConectados = new Set();
                data.arestas.forEach(a => {
                    if (a.de === est.id) arquivosConectados.add(estacoesMap.get(a.para)?.arquivo);
                    if (a.para === est.id) arquivosConectados.add(estacoesMap.get(a.de)?.arquivo);
                });
                const ehBaldeacao = arquivosConectados.size > 1;

                if (ehBaldeacao) {
                    const losango = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
                    const size = 14;
                    const points = `0,${-size} ${size},0 0,${size} ${-size},0`;
                    losango.setAttribute('points', points);
                    losango.setAttribute('fill', '#ffffff');
                    losango.setAttribute('stroke', est.cor_linha);
                    losango.setAttribute('stroke-width', 3);
                    g.appendChild(losango);
                } else {
                    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                    circle.setAttribute('r', 12);
                    circle.setAttribute('fill', '#ffffff');
                    circle.setAttribute('stroke', est.cor_linha);
                    circle.setAttribute('stroke-width', 4);
                    g.appendChild(circle);
                }

                const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                text.setAttribute('dy', -22);
                text.setAttribute('text-anchor', 'middle');
                text.setAttribute('fill', '#c9d1d9');
                text.style.fontSize = '0.7rem';
                text.textContent = est.nome;
                g.appendChild(text);

                g.addEventListener('mouseenter', () => {
                    tooltip.innerHTML = `<strong>${est.nome}</strong><br>${est.resumo}<br><em>${est.arquivo}</em>`;
                    tooltip.style.opacity = 1;
                });
                g.addEventListener('mouseleave', () => { tooltip.style.opacity = 0; });

                svg.appendChild(g);
            });

            // ---- Configurar viewBox inicial com proporção correta ----
            const todosX = data.estacoes.map(e => e.x);
            const todosY = data.estacoes.map(e => e.y);
            const minX = Math.min(...todosX) - 150;
            const maxX = Math.max(...todosX) + 150;
            const minY = Math.min(...todosY) - 150;
            const maxY = Math.max(...todosY) + 150;
            const conteudoW = maxX - minX;
            const conteudoH = maxY - minY;

            // Obtém dimensões reais do container
            const svgRect = container.getBoundingClientRect();
            const containerW = svgRect.width;
            const containerH = svgRect.height;
            const proporcaoContainer = containerW / containerH;
            const proporcaoConteudo = conteudoW / conteudoH;

            let vbW, vbH;
            if (proporcaoConteudo > proporcaoContainer) {
                // Conteúdo mais largo que o container → altura deve ser expandida
                vbW = conteudoW;
                vbH = conteudoW / proporcaoContainer;
            } else {
                // Conteúdo mais alto que o container → largura deve ser expandida
                vbH = conteudoH;
                vbW = conteudoH * proporcaoContainer;
            }

            // Centraliza o conteúdo original dentro do novo viewBox
            const offsetX = (vbW - conteudoW) / 2;
            const offsetY = (vbH - conteudoH) / 2;
            const vbX = minX - offsetX;
            const vbY = minY - offsetY;

            let viewBox = { x: vbX, y: vbY, w: vbW, h: vbH };
            const vbInicial = { ...viewBox };

            function aplicarViewBox() {
                svg.setAttribute('viewBox', `${viewBox.x} ${viewBox.y} ${viewBox.w} ${viewBox.h}`);
            }
            aplicarViewBox();

            // ---- Pan (arrastar uniforme) ----
            let isPanning = false;
            let lastMouseX, lastMouseY;

            svg.addEventListener('mousedown', (e) => {
                if (e.button !== 0) return;
                isPanning = true;
                lastMouseX = e.clientX;
                lastMouseY = e.clientY;
                svg.style.cursor = 'grabbing';
                e.preventDefault();
            });

            window.addEventListener('mousemove', (e) => {
                if (!isPanning) return;
                const dx = e.clientX - lastMouseX;
                const dy = e.clientY - lastMouseY;
                // Escala uniforme: como preserveAspectRatio='none', a escala é igual em x e y
                const scale = viewBox.w / container.clientWidth;   // mesmo que viewBox.h / container.clientHeight
                viewBox.x -= dx * scale;
                viewBox.y -= dy * scale;
                lastMouseX = e.clientX;
                lastMouseY = e.clientY;
                requestAnimationFrame(aplicarViewBox);
            });

            window.addEventListener('mouseup', () => {
                if (isPanning) {
                    isPanning = false;
                    svg.style.cursor = 'grab';
                }
            });

            // ---- Zoom com roda do mouse (centrado no cursor) ----
            svg.addEventListener('wheel', (e) => {
                e.preventDefault();
                const fator = e.deltaY > 0 ? 1.1 : 0.9;
                const rect = svg.getBoundingClientRect();
                const mouseX = e.clientX - rect.left;
                const mouseY = e.clientY - rect.top;
                const proporcaoX = mouseX / rect.width;
                const proporcaoY = mouseY / rect.height;

                const novoW = viewBox.w * fator;
                const novoH = viewBox.h * fator;
                if (novoW < 10 || novoW > 100000) return; // limites

                viewBox.x = viewBox.x + viewBox.w * proporcaoX - novoW * proporcaoX;
                viewBox.y = viewBox.y + viewBox.h * proporcaoY - novoH * proporcaoY;
                viewBox.w = novoW;
                viewBox.h = novoH;
                requestAnimationFrame(aplicarViewBox);
            }, { passive: false });

            // ---- Botões de zoom ----
            document.getElementById('btn-zoom-in').onclick = () => {
                const centroX = viewBox.x + viewBox.w / 2;
                const centroY = viewBox.y + viewBox.h / 2;
                viewBox.w *= 0.8;
                viewBox.h *= 0.8;
                viewBox.x = centroX - viewBox.w / 2;
                viewBox.y = centroY - viewBox.h / 2;
                aplicarViewBox();
            };
            document.getElementById('btn-zoom-out').onclick = () => {
                const centroX = viewBox.x + viewBox.w / 2;
                const centroY = viewBox.y + viewBox.h / 2;
                viewBox.w *= 1.2;
                viewBox.h *= 1.2;
                viewBox.x = centroX - viewBox.w / 2;
                viewBox.y = centroY - viewBox.h / 2;
                aplicarViewBox();
            };
            document.getElementById('btn-zoom-reset').onclick = () => {
                viewBox = { ...vbInicial };
                aplicarViewBox();
            };

            // ---- Legenda ----
            const legendDiv = document.getElementById('legend');
            legendDiv.innerHTML = '';
            for (const [arquivo, cor] of Object.entries(coresArquivo)) {
                const item = document.createElement('div');
                item.className = 'legend-item';
                item.innerHTML = `<div class="legend-color" style="background:${cor}"></div><span>${arquivo}</span>`;
                legendDiv.appendChild(item);
            }
            legendDiv.style.display = 'flex';
        }
    </script>
</body>
</html>
'''

class MetroCodeAPI:
    def __init__(self):
        self.pasta = None

    def selecionar_pasta(self):
        root = Tk()
        root.withdraw()
        pasta = filedialog.askdirectory(title="Selecione a pasta do projeto")
        if pasta:
            self.pasta = pasta
            return pasta
        return None

    def processar_pasta(self):
        if not self.pasta:
            raise Exception("Nenhuma pasta selecionada.")
        try:
            print("Analisando código...")
            dados = parse_project(Path(self.pasta))
            grafo = build_metro_map(dados)
            print(f"Análise concluída. {len(grafo['estacoes'])} estações, {len(grafo['arestas'])} conexões.")
            return grafo
        except Exception as e:
            raise Exception(f"Erro ao analisar o código: {str(e)}")

    def carregar_json(self):
        root = Tk()
        root.withdraw()
        arquivo = filedialog.askopenfilename(
            title="Selecione um mapa salvo (.json)",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if arquivo:
            try:
                with open(arquivo, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                raise Exception(f"Erro ao ler o arquivo: {str(e)}")
        return None

def main():
    api = MetroCodeAPI()
    webview.create_window("MetroCode", html=PAGE_HTML, js_api=api, width=1200, height=800)
    webview.start()

if __name__ == "__main__":
    main()