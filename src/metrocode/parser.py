"""
MetrôCode - Parser de código Python.
Transforma arquivos em estações, funções em plataformas e imports em trilhos.
"""

import ast
import os
from pathlib import Path


def parse_project(root_path):
    """
    Percorre uma pasta de projeto Python e extrai a estrutura.
    Retorna um dicionário com estações (arquivos), plataformas (funções/classes) e trilhos (imports).
    """
    # Garante que o caminho é um Path bonitinho
    root = Path(root_path).resolve()
    
    # Dicionário que vai guardar tudo
    mapa = {
        "estacoes": {},  # chave = caminho relativo, valor = dict com plataformas e trilhos
    }
    
    # Pastas que a gente ignora (não quero lixo nos trilhos)
    pastas_ignoradas = {
        "__pycache__", "venv", ".venv", "env", ".env",
        "node_modules", ".git", ".idea", ".vscode", "dist", "build"
    }
    
    # Percorre a pasta recursivamente
    for caminho_atual in root.rglob("*.py"):
        # Pula arquivos que estão em pastas ignoradas
        if any(pasta in caminho_atual.parts for pasta in pastas_ignoradas):
            continue
        
        # Pega o caminho relativo (pra ficar mais limpo)
        caminho_relativo = caminho_atual.relative_to(root)
        nome_estacao = str(caminho_relativo).replace("\\", "/")
        
        # Lê o arquivo e analisa com AST
        try:
            with open(caminho_atual, "r", encoding="utf-8") as arquivo:
                conteudo = arquivo.read()
            arvore = ast.parse(conteudo)
        except (SyntaxError, UnicodeDecodeError):
            # Se o arquivo tiver erro de sintaxe, pula (não vamos travar o metrô por causa disso)
            continue
        
        # Extrai as plataformas (funções e classes) e os trilhos (imports)
        plataformas = []
        trilhos = []
        
        for nodo in ast.walk(arvore):
            # Funções soltas (plataformas simples)
            if isinstance(nodo, ast.FunctionDef):
                plataformas.append({
                    "tipo": "funcao",
                    "nome": nodo.name,
                    "linha": nodo.lineno,
                })
            
            # Classes (estações maiores com sub-plataformas)
            elif isinstance(nodo, ast.ClassDef):
                metodos = []
                for item in nodo.body:
                    if isinstance(item, ast.FunctionDef):
                        metodos.append({
                            "tipo": "metodo",
                            "nome": item.name,
                            "linha": item.lineno,
                        })
                
                plataformas.append({
                    "tipo": "classe",
                    "nome": nodo.name,
                    "linha": nodo.lineno,
                    "metodos": metodos,
                })
            
            # Imports (os trilhos que conectam tudo)
            elif isinstance(nodo, ast.Import):
                for alias in nodo.names:
                    trilhos.append({
                        "tipo": "import",
                        "destino": alias.name,
                    })
            
            elif isinstance(nodo, ast.ImportFrom):
                if nodo.module:
                    for alias in nodo.names:
                        trilhos.append({
                            "tipo": "import_from",
                            "origem": nodo.module,
                            "destino": alias.name,
                        })
        
        # Registra a estação no mapa
        mapa["estacoes"][nome_estacao] = {
            "plataformas": plataformas,
            "trilhos": trilhos,
            "total_plataformas": len(plataformas),
            "total_trilhos": len(trilhos),
        }
    
    return mapa


# Se rodar direto, testa com um exemplo
if __name__ == "__main__":
    import json
    
    # Testa o parser na pasta atual
    resultado = parse_project(".")
    
    print("🚇 Mapa do MetrôCode gerado:")
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    print(f"\nTotal de estações: {len(resultado['estacoes'])}")