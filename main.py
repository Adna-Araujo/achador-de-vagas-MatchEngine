import json
import time
from brain import analyze_job
from playwright.sync_api import sync_playwright

def iniciar_aplicacao():
    # 1. Carrega a lista de vagas
    try:
        with open("debug/lista_vagas.json", "r", encoding="utf-8") as f:
            vagas = json.load(f)
    except Exception:
        print("[!] Erro: Arquivo de vagas não encontrado.")
        return

    print(f"[*] MatchEngine pronto! {len(vagas)} vagas no radar.")
    matches_reais = 0 

    # --- CONFIGURAÇÃO DO FILTRO (Ajuste aqui sua stack) ---
    TERMOS_BONS = ["dev", "desenvolvedor", "software", "estágio", "estagiário", "jr", "júnior", "c#", "java", "sistemas"]
    TERMOS_RUINS = ["banco de talentos", "sênior", "sr", "pleno", "pl", "marketing", "vendas", "design", "produto"]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for link in vagas:
            print(f"\n[🔍] Verificando: {link}")
            
            try:
                page.goto(link, wait_until="domcontentloaded", timeout=60000)
                time.sleep(2) # Respiro para o JS

                # --- "CAÇANDO" O TÍTULO DA VAGA ---
                # Tentamos pegar o H1 (nome do cargo), se não der, pegamos o título da aba
                h1_element = page.query_selector("h1")
                nome_da_vaga = h1_element.inner_text().lower() if h1_element else page.title().lower()
                
                print(f"[*] Cargo detectado: {nome_da_vaga.strip().upper()}")

                # --- FILTRO DE ELITE (ECONOMIA DE API) ---
                contem_bom = any(t in nome_da_vaga for t in TERMOS_BONS)
                contem_ruim = any(t in nome_da_vaga for t in TERMOS_RUINS)

                if contem_ruim or not contem_bom:
                    print(f"[🗑️] DESCARTE AUTOMÁTICO: Título fora do perfil. (IA poupada)")
                    continue

                # 2. Chama a IA apenas para os "sobreviventes"
                print("[🧠] Vaga promissora! Consultando a IA...")
                html_da_vaga = page.content()
                analise = analyze_job(html_da_vaga)
                
                # Pausa técnica para não estourar o limite de requisições por minuto
                time.sleep(10)

                if analise and analise.get("match"):
                    matches_reais += 1
                    print(f"[✅] MATCH ENCONTRADO! Score: {analise.get('score')}")
                    print(f"[🚀] Motivo: {analise.get('motivo')}")
                    
                    # Interrupção para você ver o sucesso
                    input("\n>> Pressione Enter para continuar a busca...")
                else:
                    motivo = analise.get("motivo") if analise else "Erro na análise"
                    print(f"[❌] IA descartou: {motivo}")

            except Exception as e:
                print(f"[!] Erro ao processar esta vaga: {e}")

        # --- AVISO DE TÉRMINO ---
        print("\n" + "="*50)
        print(f"[🏁] BUSCA FINALIZADA!")
        print(f"[*] Total de links processados: {len(vagas)}")
        print(f"[*] Vagas que passaram pelo filtro: {matches_reais}")
        print("="*50)
        
        browser.close()

if __name__ == "__main__":
    iniciar_aplicacao()