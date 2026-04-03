import os
import time
import json
import re
from google import genai
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Inicializa o Cliente usando o novo SDK da Google
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def clean_html(html_content):
    """Limpa o HTML para economizar tokens e focar no texto da vaga."""
    if not html_content:
        return ""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove elementos que não ajudam na análise técnica
    for element in soup(["script", "style", "header", "footer", "nav", "aside"]):
        element.decompose()
        
    # Pega o texto, remove espaços extras e limita o tamanho
    texto = soup.get_text(separator=' ', strip=True)
    return texto[:7000] 

def analisar_vaga(html_raw):
    """
    Função principal de análise. 
    Renomeada para 'analisar_vaga' para funcionar com seu main.py
    """
    texto_vaga = clean_html(html_raw)
    
    # Modelo sugerido para velocidade e custo (Flash)
    # Se o 'gemini-3-flash-preview' não estiver disponível, use 'gemini-1.5-flash'
    model_id = "gemini-2.0-flash" 
    
    prompt = f"""
    Você é um Recrutador Técnico rigoroso e realista. Analise a vaga abaixo para o perfil da Adna:
    
    PERFIL DO CANDIDATO:
    - Nível: Desenvolvedora Júnior ou Estagiária.
    - Formação: Estudante de Análise e Desenvolvimento de Sistemas (Estácio).
    - Localização: Natal/RN (Aceita Remoto ou Presencial/Híbrido em Natal).
    - Stack Principal: C# (.NET) e Java (Spring Boot).
    - Diferencial: Manutenção de Hardware (ESP32) e Escape Rooms.
    - Estado Atual: Em formação (Ensino Superior NÃO concluído).

    CRITÉRIOS DE REJEIÇÃO (FALSE):
    1. Exigência explícita de "Ensino Superior COMPLETO".
    2. Vagas de nível Sênior, Especialista ou Gestão.
    3. Títulos como "Banco de Talentos", "Cadastro Reserva" ou "Talent Pool".
    4. Vagas em outras cidades que exijam residência local (Ex: Presencial em Curitiba).

    TEXTO DA VAGA:
    {texto_vaga}

    Responda APENAS com um JSON puro no formato:
    {{
      "match": boolean,
      "score": int,
      "resumo": "string curta",
      "motivo": "justificativa direta"
    }}
    """
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Chamada da API com o novo SDK
            response = client.models.generate_content(
                model=model_id, 
                contents=prompt,
                # Força o modelo a responder apenas JSON (se disponível no SDK)
                config={'response_mime_type': 'application/json'}
            )
            
            # Limpeza do texto para garantir JSON válido
            json_txt = response.text.strip()
            # Remove blocos de código markdown se a IA os colocar
            json_txt = re.sub(r'```json\s?|```', '', json_txt)
            
            return json.loads(json_txt)

        except Exception as e:
            error_msg = str(e)
            
            # Erro 429: Limite de requisições (muito comum no plano gratuito)
            if "429" in error_msg:
                print(f"[!] Limite de API (429). Aguardando 60s (Tentativa {attempt+1})...")
                time.sleep(60)
                continue
            
            # Erro 503: Servidor instável
            if "503" in error_msg and attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))
                continue
                
            print(f"[!] Erro na análise técnica: {e}")
            return {"match": False, "score": 0, "resumo": "Erro", "motivo": "Erro na comunicação com a IA."}
    
    return None