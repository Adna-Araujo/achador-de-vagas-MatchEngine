import json
import os
from analyzer import extrair_texto_pdf, MatchEngineAnalyzer

ARQUIVO_SKILLS = "skills.txt"
ARQUIVO_VAGAS = "vagas_analise.txt"
MEU_CURRICULO = "meu_curriculo.pdf"
DB_RESULTADOS = "analise_vagas_match.json"

def carregar_minhas_skills():
    if not os.path.exists(ARQUIVO_SKILLS): return []
    with open(ARQUIVO_SKILLS, "r", encoding="utf-8") as f:
        return [s.strip() for s in f.read().split(",") if s.strip()]

def executar_processamento_estrategico():
    print("[*] MatchEngine: Iniciando Ciclo de Análise Estratégica...")
    
    skills_reais = carregar_minhas_skills()
    texto_curriculo = extrair_texto_pdf(MEU_CURRICULO)
    analyzer = MatchEngineAnalyzer()
    
    if not os.path.exists(ARQUIVO_VAGAS):
        print("[!] Arquivo de vagas não encontrado.")
        return

    with open(ARQUIVO_VAGAS, "r", encoding="utf-8") as f:
        lista_vagas = analyzer.parse_vagas(f.read())

    print(f"[*] {len(lista_vagas)} vagas encontradas.")

    for vaga in lista_vagas:
        # Chamada simplificada sem a calculadora
        resultado = analyzer.calcular_match(skills_reais, vaga['descricao'])
        
        ajustes_criticos = []
        sugestoes_melhoria = []
        
        for match in resultado['matches']:
            variantes = analyzer.sinonimos.get(match, [])
            termos = [match.lower()] + [v.lower() for v in variantes]
            
            if not any(t in texto_curriculo.lower() for t in termos):
                if match in analyzer.obrigatorios:
                    ajustes_criticos.append(match)
                else:
                    sugestoes_melhoria.append(match)

        status = "RECOMENDADA" if resultado['score'] >= 70 else "NÃO RECOMENDADA"
        
        print(f"\n[🔍] Vaga: {vaga['link'][:50]}...")
        print(f"[{'✅' if status == 'RECOMENDADA' else '❌'}] Score: {resultado['score']}%")
        print(f"[💡] Justificativa: {resultado['justificativa']}")
        
        if ajustes_criticos:
            print(f"[🚨] CRÍTICO (Falta no PDF): {ajustes_criticos}")
        if sugestoes_melhoria:
            print(f"[📝] Sugestão (Keyword): {sugestoes_melhoria}")

if __name__ == "__main__":
    executar_processamento_estrategico()