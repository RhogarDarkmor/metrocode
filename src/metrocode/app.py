from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.containers import Container
from pathlib import Path
from .parser import parse_project  # ajuste o import conforme sua estrutura

class MetroMap(Static):
    """Widget que vai desenhar o mapa do metrô"""
    def __init__(self, mapa_data: dict):
        super().__init__()
        self.mapa_data = mapa_data
    
    def render(self) -> str:
        """Desenha o mapa baseado nos dados do parser"""
        if not self.mapa_data.get("estacoes"):
            return "🚇 Nenhuma estação encontrada. Execute em um diretório com código Python."
        
        linhas = ["🚇 METRÔCODE - MAPA DE DEPENDÊNCIAS\n" + "="*40 + "\n"]
        
        for estacao, dados in list(self.mapa_data["estacoes"].items())[:10]:  # limita a 10
            linhas.append(f"📍 ESTAÇÃO: {estacao}")
            linhas.append(f"   🚪 Plataformas: {dados['total_plataformas']}")
            linhas.append(f"   🔗 Trilhos: {dados['total_trilhos']}")
            
            # Mostra algumas plataformas
            if dados['plataformas'][:3]:
                linhas.append("   🏢 Principais plataformas:")
                for p in dados['plataformas'][:3]:
                    nome = p['nome']
                    tipo = "📦" if p['tipo'] == 'classe' else "⚡"
                    linhas.append(f"      {tipo} {nome}")
            
            linhas.append("")
        
        if len(self.mapa_data["estacoes"]) > 10:
            linhas.append(f"... e mais {len(self.mapa_data['estacoes']) - 10} estações")
        
        return "\n".join(linhas)

class MetroApp(App):
    """Aplicação principal"""
    
    def __init__(self, project_path: str = "."):
        super().__init__()
        self.project_path = project_path
        self.mapa_data = parse_project(project_path)
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(MetroMap(self.mapa_data))
        yield Footer()
    
    def on_mount(self):
        self.title = "🚇 MetrôCode"
        self.sub_title = f"Analisando: {self.project_path}"

def main():
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    app = MetroApp(path)
    app.run()

if __name__ == "__main__":
    main()