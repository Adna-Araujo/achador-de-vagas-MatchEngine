import json
import time
import os
from playwright.sync_api import sync_playwright

def find_jobs():
    if not os.path.exists("debug"):
        os.makedirs("debug")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) 
        page = browser.new_page()
        
        portal_url = "https://gruposysmap.gupy.io/" 
        print(f"[*] Investigando: {portal_url}")
        
        vagas_totais = []
        
        try:
            page.goto(portal_url, wait_until="load", timeout=60000)
            time.sleep(3)

            # --- PASSO 1: Mudar para 50 itens por página ---
            try:
                print("[*] Ajustando para 50 vagas por página...")
                # Procura o seletor de "Itens por página" (baseado no seu print)
                dropdown = page.locator("div[role='combobox']").filter(has_text="10")
                if dropdown.is_visible():
                    dropdown.click()
                    # Seleciona a opção 50 na lista que abrir
                    page.get_by_role("option", name="50").click()
                    time.sleep(3) # Tempo para o site re-renderizar a lista maior
            except Exception as e:
                print(f"[!] Não consegui mudar para 50 itens: {e}. Seguindo com o padrão.")

            # --- LOOP DE PAGINAÇÃO ---
            pagina_atual = 1
            while True:
                print(f"\n[📄] ESCANEANDO PÁGINA: {pagina_atual}")
                
                # --- PASSO 2: Scroll para garantir que os 50 carregaram ---
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)

                # Coleta links da página atual
                links_da_pagina = page.query_selector_all('a[href*="/jobs/"]')
                for link in links_da_pagina:
                    href = link.get_attribute("href")
                    if href:
                        full_path = href if href.startswith("http") else f"https://gruposysmap.gupy.io{href}"
                        clean_link = full_path.split('?')[0]
                        vagas_totais.append(clean_link)

                vagas_unindo = list(set(vagas_totais))
                print(f"[*] Total capturado até agora: {len(vagas_unindo)} links.")

                # --- PASSO 3: Tenta ir para a próxima página de 50 ---
                btn_proximo = (
                    page.query_selector('button[aria-label*="next"]') or 
                    page.query_selector('button[aria-label*="próxima"]') or 
                    page.query_selector('button:has(svg[data-testid="ChevronRightIcon"])')
                )
                
                if btn_proximo and btn_proximo.is_enabled():
                    print("[>] Indo para a próxima página de 50...")
                    btn_proximo.click()
                    pagina_atual += 1
                    time.sleep(3)
                else:
                    print("[!] Fim das páginas alcançado.")
                    break

            # --- SALVAMENTO ---
            final_list = list(set(vagas_totais))
            print(f"\n[+] Sucesso! {len(final_list)} vagas encontradas.")
            with open("debug/lista_vagas.json", "w", encoding="utf-8") as f:
                json.dump(final_list, f, indent=4, ensure_ascii=False)

        except Exception as e:
            print(f"[!] Erro: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    find_jobs()