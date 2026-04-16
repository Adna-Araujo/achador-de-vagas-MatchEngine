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

def carregar_vagas_manuais(analyzer):
    if not os.path.exists(ARQUIVO_VAGAS):
        return []
    with open(ARQUIVO_VAGAS, "r", encoding="utf-8") as f:
        return analyzer.parse_vagas(f.read())

def executar_processamento_estrategico():
    print("[*] MatchEngine: Iniciando Ciclo de Análise Estratégica...")
    
    # CORREÇÃO: Carregando as variáveis antes de usar
    skills_reais = carregar_minhas_skills()
    texto_curriculo = extrair_texto_pdf(MEU_CURRICULO)
    
    analyzer = MatchEngineAnalyzer()
    lista_vagas = carregar_vagas_manuais(analyzer)

    if not skills_reais or not lista_vagas:
        print("[!] Erro: Verifique os arquivos de skills ou vagas.")
        return

    print(f"[*] {len(lista_vagas)} vagas encontradas.")
    resultados_finais = []

    for vaga in lista_vagas:
        resultado = analyzer.calcular_match(skills_reais, vaga['descricao'])
        
        ajustes_criticos = []
        sugestoes_melhoria = []
        
        # Lógica de conferência no PDF com separação por importância
        for match in resultado['matches']:
            variantes = analyzer.sinonimos.get(match, [])
            termos = [match.lower()] + [v.lower() for v in variantes]
            
            if not any(t in texto_curriculo.lower() for t in termos):
                # Se for uma skill obrigatória (definida no analyzer), é crítico
                if match in analyzer.obrigatorios:
                    ajustes_criticos.append(match)
                else:
                    sugestoes_melhoria.append(match)

        status = "RECOMENDADA" if resultado['score'] >= 70 else "NÃO RECOMENDADA"
        
        print(f"\n[🔍] Vaga: {vaga['link'][:50]}...")
        print(f"[{'✅' if status == 'RECOMENDADA' else '❌'}] Score: {resultado['score']}%")
        print(f"[💡] Por que? {resultado['justificativa']}")
        
        if ajustes_criticos:
            print(f"[🚨] CRÍTICO (Falta no seu PDF): {ajustes_criticos}")
        if sugestoes_melhoria:
            print(f"[📝] Sugestão de Melhoria (Palavra-chave): {sugestoes_melhoria}")

        resultados_finais.append({
            "link": vaga['link'],
            "score": resultado['score'],
            "status": status,
            "justificativa": resultado['justificativa'],
            "ajustes_criticos": ajustes_criticos,
            "melhorias": sugestoes_melhoria
        })

    with open(DB_RESULTADOS, "w", encoding="utf-8") as f:
        json.dump(resultados_finais, f, indent=4, ensure_ascii=False)
    print(f"\n[🏁] Análise concluída. Relatório em {DB_RESULTADOS}")

if __name__ == "__main__":
    executar_processamento_estrategico()