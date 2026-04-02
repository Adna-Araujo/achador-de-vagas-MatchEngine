import os
import json
from brain import analyze_job # Importa a função que criamos antes

def test_engine():
    print("[*] Iniciando Teste de Estresse do MatchEngine Brain...")
    
    # 1. Tenta carregar o HTML que capturamos no Dia 1
    html_path = "debug/vaga_teste.html"
    
    if not os.path.exists(html_path):
        print(f"[!] Erro: Arquivo {html_path} não encontrado. Capture uma vaga primeiro!")
        return

    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    print(f"[*] HTML carregado ({len(html_content)} bytes). Enviando para análise da IA...")

    # 2. Chama o Cérebro para analisar
    resultado = analyze_job(html_content)

    # 3. Exibe o veredito de forma organizada
    if resultado:
        print("\n" + "="*40)
        print("VEREDITO DO MATCHENGINE:")
        print("="*40)
        print(f"MATCH:  {'✅ SIM' if resultado.get('match') else '❌ NÃO'}")
        print(f"SCORE:  {resultado.get('score')}/100")
        print(f"RESUMO: {resultado.get('resumo')}")
        print(f"MOTIVO: {resultado.get('motivo')}")
        print("="*40)
    else:
        print("[!] A IA falhou em retornar um resultado válido.")

if __name__ == "__main__":
    test_engine()