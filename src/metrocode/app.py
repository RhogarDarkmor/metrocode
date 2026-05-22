"""
MetrôCode - O mapa do seu código no terminal.
Inspirado no mapa do metrô de São Paulo.
"""

from textual.app import App
from textual.widgets import Header, Footer, Static


class MetroCodeApp(App):
    """Aplicativo principal. Por enquanto, só uma carcaça."""

    CSS = """
    Screen {
        align: center middle;
    }

    #splash {
        text-align: center;
        color: #00ff00;
        text-style: bold;
    }
    """

    def compose(self):
        yield Header()
        yield Static("MetrôCode - Embarque nessa linha de código", id="splash")
        yield Footer()

    def on_mount(self):
        self.title = "MetrôCode"


if __name__ == "__main__":
    app = MetroCodeApp()
    app.run()