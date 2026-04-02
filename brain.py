import os
import time
import json
from google import genai
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Inicializa o Cliente
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def clean_html(html_content):
    """Limpa o HTML para economizar tokens e focar no texto da vaga."""
    soup = BeautifulSoup(html_content, 'html.parser')
    for script_or_style in soup(["script", "style", "header", "footer", "nav"]):
        script_or_style.decompose()
    return soup.get_text(separator=' ', strip=True)[:7000] 

def analyze_job(html_raw):
    texto_vaga = clean_html(html_raw)
    model_id = "gemini-3-flash-preview"
    
    # PROMPT ATUALIZADO: Focado em C#, Java e sua realidade acadêmica
    prompt = f"""
    Você é um Recrutador Técnico rigoroso. Analise a vaga abaixo para o seguinte perfil:
    
    PERFIL DO CANDIDATO:
    - Nível: Desenvolvedor Júnior ou Estagiário.
    - Formação: Estudante de Análise e Desenvolvimento de Sistemas (Estácio).
    - Localização: Natal/RN (Prioridade para Remoto ou Presencial/Híbrido em Natal).
    - Stack Principal: C# (.NET, ASP.NET) e Java (Spring Boot, Hibernate).
    - Diferencial: Experiência com Hardware (ESP32/ESP8266) e manutenção de sistemas (Escape Rooms).
    - Estado Atual: Em formação (Ainda NÃO possui ensino superior completo).

    CRITÉRIOS DE FILTRAGEM (CRÍTICO):
    1. Se a vaga exigir "Ensino Superior COMPLETO", defina match como false e cite isso no motivo.
    2. Vagas de Java ou C# Júnior/Estágio = Match Alto.
    3. Vagas exclusivas de outras linguagens (Python, PHP, Ruby) = Match Baixo/Falso.
    4. REJEIÇÃO OBRIGATÓRIA (BANCO DE TALENTOS): Se o título ou a descrição indicar "Banco de Talentos", "Cadastro de Reserva" ou "Talent Pool", defina match como FALSE.

    TEXTO DA VAGA:
    {texto_vaga}

    Responda APENAS com um JSON puro:
    {{
      "match": boolean,
      "score": int,
      "resumo": "string",
      "motivo": "string"
    }}
    """
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(model=model_id, contents=prompt)
            json_txt = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(json_txt)
        except Exception as e:
            # Se for erro de limite de requisições (429)
            if "429" in str(e):
                print(f"[!] Limite de API atingido. Aguardando 60s para o Google respirar...")
                time.sleep(60)
                continue # Tenta a mesma vaga de novo após o descanso
            
            # Se for servidor instável (503)
            if "503" in str(e) and attempt < max_retries - 1:
                wait_time = 5 * (attempt + 1)
                print(f"[!] Servidor ocupado. Tentativa {attempt + 1}. Esperando {wait_time}s...")
                time.sleep(wait_time)
                continue
                
            print(f"[!] Erro na análise: {e}")
            return None