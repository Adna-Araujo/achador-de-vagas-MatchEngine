import sys
import os

# Adiciona o diretório onde o app.py está localizado ao caminho de busca do Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
from analyzer import MatchEngineAnalyzer, extrair_texto_pdf
import io

# Configuração da página
st.set_page_config(page_title="MatchEngine Analysis", layout="wide")

def main():
    st.title("MatchEngine: Análise Estratégica de Vagas")
    st.markdown("""
    Esta ferramenta realiza a extração de competências de currículos em PDF e 
    cruza os dados com requisitos de vagas para identificar lacunas técnicas.
    """)

    analyzer = MatchEngineAnalyzer()

    # Sidebar para configuração de Skills
    st.sidebar.header("Configurações de Perfil")
    skills_input = st.sidebar.text_area(
        "Suas Skills (separadas por vírgula):",
        "Java, Python, C#, SQL, Web API, IoT, Lógica de Programação"
    )
    skills_usuario = [s.strip() for s in skills_input.split(",") if s.strip()]

    # Layout de colunas para Upload e Entrada de Vagas
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Currículo")
        arquivo_pdf = st.file_uploader("Upload do seu currículo (PDF)", type=["pdf"])

    with col2:
        st.subheader("Dados das Vagas")
        texto_vagas = st.text_area(
            "Cole as vagas aqui (use '---' para separar múltiplas vagas):",
            height=200,
            placeholder="Descrição da vaga...\nLink da vaga\n---\nPróxima vaga..."
        )

    if st.button("Executar Análise"):
        if arquivo_pdf and texto_vagas:
            # Extração de texto do PDF carregado em memória
            with st.spinner("Processando currículo..."):
                # Salvando temporariamente para processar
                with open("temp_curriculo.pdf", "wb") as f:
                    f.write(arquivo_pdf.getbuffer())
                
                texto_curriculo = extrair_texto_pdf("temp_curriculo.pdf")
                lista_vagas = analyzer.parse_vagas(texto_vagas)

                st.divider()
                st.header("Resultados da Análise")

                for vaga in lista_vagas:
                    resultado = analyzer.calcular_match(skills_usuario, vaga['descricao'])
                    
                    # Lógica de Auditoria de Keywords (Original do seu main.py)
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

                    # Exibição Visual
                    with st.expander(f"Vaga: {vaga['link'][:60]}...", expanded=True):
                        c1, c2 = st.columns([1, 3])
                        
                        with c1:
                            st.metric("Aderência Técnica", f"{resultado['score']}%")
                        
                        with c2:
                            st.write(f"**Justificativa:** {resultado['justificativa']}")

                        if ajustes_criticos:
                            st.error(f"**CRÍTICO (Falta no PDF):** {', '.join(ajustes_criticos)}")
                        
                        if sugestoes_melhoria:
                            st.warning(f"**Sugestão de Palavra-chave:** {', '.join(sugestoes_melhoria)}")

        else:
            st.info("Por favor, faça o upload do PDF e insira as descrições das vagas.")

if __name__ == "__main__":
    main()