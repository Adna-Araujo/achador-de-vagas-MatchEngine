import json
import os
import re
import time
from playwright.sync_api import sync_playwright
from datetime import datetime

TEMP_FILE = "debug/lista_vagas.json"
DB_FILE = "vagas_db.json"
LOG_FILE = "relatorio_limpeza.txt"

# Filtros com Regex Blindado
TERMOS_BONS = [
    r'\bdev\b', r'\bdesenvolvedor\b', r'\bestágio\b', r'\bestagiário\b', 
    r'\bjr\b', r'\bjúnior\b', r'\bjunior\b', r'\bc#\b', r'\bjava\b', 
    r'\bsistemas\b', r'\bprogramador\b', r'\bbackend\b'
]

TERMOS_RUINS = [
    r'\bsênior\b', r'\bsenior\b', r'\bsr\b', r'\bpleno\b', r'\bpl\b', 
    r'\bmanager\b', r'\baccount\b', r'\barquiteto\b', r'\blead\b', 
    r'\bowner\b', r'\bmaster\b', r'\bgerente\b', r'\boperador\b',
    r'\bespecialista\b', r'\bcientista\b', r'\bengenheiro\b', r'\bui\b', r'\bux\b',
    r'\bbanco de talentos\b', r'\bcadastro de reserva\b' # Adicionados conforme sua preferência
]

def validar_titulo(titulo):
    titulo = titulo.lower()
    for padrao in TERMOS_RUINS:
        if re.search(padrao, titulo):
            return False, f"REJEITADA: Contém termo proibido ({padrao.replace(r'\b', '')})"
    
    bons_achados = [padrao.replace(r'\b', '') for padrao in TERMOS_BONS if re.search(padrao, titulo)]
    if bons_achados:
        return True, f"APROVADA: Contém ({', '.join(bons_achados)})"
    
    return False, "REJEITADA: Não contém termos técnicos de desenvolvimento"

def importar_vagas():
    if not os.path.exists(TEMP_FILE):
        print("[!] Erro: Rode o scraper primeiro.")
        return

    with open(TEMP_FILE, "r", encoding="utf-8") as f:
        links_brutos = json.load(f)

    banco_dados = {}
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            banco_dados = json.load(f)

    # Início do Terminal Minimalista
    print(f"[*] MatchEngine carregou {len(links_brutos)} vagas para processar.")
    print("\nAnalisando vagas... (Aguarde, o relatório está sendo gerado)")

    relatorio = [f"=== RELATÓRIO DE LIMPEZA ({datetime.now().strftime('%d/%m/%Y %H:%M')}) ===\n"]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        cont_salvas = 0

        for url in links_brutos:
            # Pula se já estiver no banco para não re-analisar o que já salvou
            if url in banco_dados: continue

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                h1 = page.query_selector("h1")
                titulo = h1.inner_text().strip() if h1 else page.title().strip()
                
                aprovada, motivo = validar_titulo(titulo)

                if aprovada:
                    banco_dados[url] = {
                        "cargo": titulo,
                        "status": "pendente",
                        "data_descoberta": datetime.now().strftime("%Y-%m-%d")
                    }
                    cont_salvas += 1

                # O log detalhado vai APENAS para a lista do relatório
                log_entry = f"Cargo: {titulo.upper()}\nMotivo: {motivo}\nURL: {url}\n{'-'*50}"
                relatorio.append(log_entry + "\n")

            except Exception as e:
                relatorio.append(f"ERRO na URL {url}: {e}\n{'-'*50}")

        # Salva o banco e o relatório silenciosamente
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(banco_dados, f, indent=4, ensure_ascii=False)
        
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.writelines(relatorio)

        # Encerramento do Terminal Minimalista
        print("\n==================================================")
        print(f"[🏁] BUSCA FINALIZADA!")
        print(f"[*] Total de vagas analisadas: {len(links_brutos)}")
        print(f"[*] Matches reais encontrados: {cont_salvas}")
        print("==================================================")
        
        browser.close()

if __name__ == "__main__":
    importar_vagas()