import json
import os
import re
import time
from playwright.sync_api import sync_playwright
from brain import analisar_vaga

DB_FILE = "vagas_db.json"

def validar_descricao(texto):
    texto_min = texto.lower()
    
    # 1. Filtro de Localização (Mais tolerante)
    LOCALIDADES_OK = ["natal", "rn", "rio grande do norte", "remoto", "anywhere", "home office", "remote"]
    passou_localizacao = any(loc in texto_min for loc in LOCALIDADES_OK)
    
    if not passou_localizacao:
        return False, "Localização incompatível (Não é Natal nem Remoto)"

    # 2. Filtro de Experiência (Ignora o '25 anos da empresa')
    # Só pega o número se tiver 'experiência', 'mínimo' ou 'atuação' por perto
    exp_pattern = r'(?:experiência|mínimo|atuação|vivência|at least).{0,50}(\d+)\s*(?:ano|anos|year|years)'
    exp_matches = re.findall(exp_pattern, texto_min)
    
    for anos in exp_matches:
        if int(anos) >= 3:
            return False, f"Senioridade alta detectada ({anos} anos de exp)"

    return True, "Aprovada no pré-filtro"

def processar_vagas():
    if not os.path.exists(DB_FILE):
        print("[!] Erro: Banco de dados não encontrado.")
        return

    # AQUI AS VARIÁVEIS SÃO CRIADAS (Onde o seu deu erro antes)
    with open(DB_FILE, "r", encoding="utf-8") as f:
        banco_dados = json.load(f)

    vagas_pendentes = {k: v for k, v in banco_dados.items() if v.get("status") == "pendente"}

    if not vagas_pendentes:
        print("[✅] Nenhuma vaga nova para analisar.")
        return

    print(f"[*] MatchEngine analisando {len(vagas_pendentes)} potenciais...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for url, info in vagas_pendentes.items():
            try:
                print(f"\n[🔍] Lendo descrição: {info['cargo']}...")
                page.goto(url, wait_until="networkidle", timeout=60000)
                time.sleep(2) # Respiro para a Gupy carregar

                descricao_completa = page.inner_text("body")

                # Camada de Pré-filtro
                passou, motivo_filtro = validar_descricao(descricao_completa)
                
                if not passou:
                    print(f"[🗑️] Descartada: {motivo_filtro}")
                    banco_dados[url]["status"] = "rejeitada_filtro"
                    banco_dados[url]["motivo"] = motivo_filtro
                    continue

                # Camada de IA
                print("[🧠] Passou no filtro! Consultando IA...")
                resultado = analisar_vaga(descricao_completa)

                if resultado:
                    banco_dados[url]["score"] = resultado.get("score", 0)
                    banco_dados[url]["motivo"] = resultado.get("motivo", "Sem justificativa.")
                    banco_dados[url]["status"] = "analisado"
                    print(f"[⭐] SCORE FINAL: {banco_dados[url]['score']}/100")

            except Exception as e:
                print(f"[!] Erro ao processar {url}: {e}")

        # SALVANDO O BANCO (A variável banco_dados precisa estar aqui)
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(banco_dados, f, indent=4, ensure_ascii=False)

        browser.close()
        print("\n[🏁] Ciclo de análise finalizado.")

if __name__ == "__main__":
    processar_vagas()