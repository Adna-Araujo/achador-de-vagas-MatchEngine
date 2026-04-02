import json
import os
from datetime import datetime

DB_FILE = "vagas_db.json"
TEMP_FILE = "debug/lista_vagas.json"

def salvar_no_banco():
    # 1. Carrega as vagas novas do Scraper
    if not os.path.exists(TEMP_FILE):
        print("[!] Nenhum arquivo temporário encontrado. Rode o scraper primeiro.")
        return

    with open(TEMP_FILE, "r", encoding="utf-8") as f:
        vagas_novas = json.load(f)

    # 2. Carrega o Banco de Dados existente (ou cria um novo)
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            banco_dados = json.load(f)
    else:
        banco_dados = {}

    # 3. Adiciona apenas o que é novo
    cont_novas = 0
    for url in vagas_novas:
        if url not in banco_dados:
            banco_dados[url] = {
                "status": "pendente",
                "data_descoberta": datetime.now().strftime("%Y-%m-%d"),
                "score": 0,
                "motivo": ""
            }
            cont_novas += 1

    # 4. Salva o Banco de Dados atualizado
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(banco_dados, f, indent=4, ensure_ascii=False)

    print(f"[✅] Banco de dados atualizado!")
    print(f"[*] Vagas novas adicionadas: {cont_novas}")
    print(f"[*] Total de vagas no banco: {len(banco_dados)}")

if __name__ == "__main__":
    salvar_no_banco()