CORES = ["#004A9F", "#007F4E", "#E31C23", "#F9A727", "#8D6BB8", "#A0A0A0"]

def build_metro_map(projeto_data):
    arquivos = sorted(set(d["file"] for d in projeto_data))
    cores_por_arquivo = {}
    for i, arq in enumerate(arquivos):
        cores_por_arquivo[arq] = CORES[i % len(CORES)]

    estacoes = []
    for d in projeto_data:
        for func in d["functions"]:
            station_id = f"{d['file']}::{func}"
            estacoes.append({
                "id": station_id,
                "nome": func,
                "arquivo": d["file"],
                "resumo": d["docstrings"].get(func, "Sem descrição"),
                "cor_linha": cores_por_arquivo[d["file"]]
            })

    arestas = []
    ids_validos = {e["id"] for e in estacoes}
    for d in projeto_data:
        for func, calls in d["calls"].items():
            origem_id = f"{d['file']}::{func}"
            for called in calls:
                if "::" in called:
                    mod, fn = called.split("::")
                    dest_file = next((dd["file"] for dd in projeto_data if dd["module_name"] == mod), None)
                    if dest_file:
                        dest_id = f"{dest_file}::{fn}"
                    else:
                        continue
                else:
                    dest_id = f"{d['file']}::{called}"
                if dest_id in ids_validos and origem_id != dest_id:
                    tipo = "mesma_linha" if d["file"] == dest_id.split("::")[0] else "baldeacao"
                    arestas.append({"de": origem_id, "para": dest_id, "tipo": tipo})

    estacoes.sort(key=lambda e: (e["arquivo"], e["nome"]))
    y_atual = 80
    espacamento_y = 130
    x_inicial = 120
    espacamento_x = 160
    arquivo_atual = None
    x_atual = x_inicial
    for est in estacoes:
        if est["arquivo"] != arquivo_atual:
            arquivo_atual = est["arquivo"]
            y_atual += espacamento_y
            x_atual = x_inicial
        est["x"] = x_atual
        est["y"] = y_atual
        x_atual += espacamento_x

    return {"estacoes": estacoes, "arestas": arestas}