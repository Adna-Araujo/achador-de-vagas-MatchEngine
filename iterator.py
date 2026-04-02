import json
import time
from playwright.sync_api import sync_playwright

def test_navigation():
    # 1. Carrega os links que o scraper encontrou
    try:
        with open("debug/lista_vagas.json", "r", encoding="utf-8") as f:
            vagas = json.load(f)
    except FileNotFoundError:
        print("[!] Erro: lista_vagas.json não encontrado. Rode o scraper primeiro.")
        return

    if not vagas:
        print("[!] A lista de vagas está vazia.")
        return

    print(f"[*] MatchEngine carregou {len(vagas)} alvos. Testando os 3 primeiros...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for link in vagas[:3]: # Testa apenas as 3 primeiras para ganhar tempo
            print(f"\n[>] Navegando para: {link}")
            
            try:
                # Entra na vaga
                page.goto(link, wait_until="domcontentloaded", timeout=60000)
                
                # Extrai o título da vaga só para confirmar que carregou
                # Na Gupy, o título geralmente fica em um <h1>
                time.sleep(3) # Espera o JS renderizar o título
                titulo = page.title()
                
                print(f"[+] Página carregada: {titulo}")
                
            except Exception as e:
                print(f"[!] Erro ao acessar vaga: {e}")
            
            print("[*] Aguardando 5 segundos para a próxima...")
            time.sleep(5)

        print("\n[***] Teste de navegação concluído com sucesso! [***]")
        browser.close()

if __name__ == "__main__":
    test_navigation()