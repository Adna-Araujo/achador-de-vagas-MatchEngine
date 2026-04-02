import time
from playwright.sync_api import sync_playwright

def run():
    # Iniciamos o navegador visível (headless=False) para você ver o que está acontecendo
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # --- PASSO CRÍTICO ---
        # Substitua pela URL de uma vaga real da Gupy que você queira testar
        url = "https://gruposysmap.gupy.io/jobs/11004566?jobBoardSource=share_link" 
        
        print(f"Acessando: {url}")
        page.goto(url)
        
        # Vou te dar 30 segundos para a página carregar ou você fazer login se o site pedir
        print("Aguardando 30 segundos... Verifique se a página carregou o formulário.")
        time.sleep(30)
        
        # Captura o HTML
        html_content = page.content()
        
        # Salva para análise no Dia 3
        with open("debug/vaga_teste.html", "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print("Finalizado! O arquivo debug/vaga_teste.html foi criado.")
        browser.close()

if __name__ == "__main__":
    run()