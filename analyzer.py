import pdfplumber
import re

def extrair_texto_pdf(caminho_pdf):
    texto_completo = ""
    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            for pagina in pdf.pages:
                extraido = pagina.extract_text()
                if extraido:
                    texto_completo += extraido + " "
        return re.sub(r'\s+', ' ', texto_completo).strip()
    except Exception as e:
        print(f"Erro ao ler PDF: {e}")
        return ""

class MatchEngineAnalyzer:
    def __init__(self, separator="---"):
        self.separator = separator
        self.sinonimos = {
            "Lógica de Programação": ["lógica de sistemas", "raciocínio lógico", "algoritmos", "lógica"],
            "C#": [".net", "csharp", "c-sharp"],
            "SQL": ["mysql", "postgresql", "sqlite", "sql server", "banco de dados"],
            "Web API": ["apis", "microserviços", "arquitetura de microserviços", "flask", "spring boot"],
            "IoT": ["automação", "esp32", "esp8266", "microcontroladores", "eletrônica", "mqtt"]
        }
        self.obrigatorios = ["Python", "Java", "C#", "SQL", "C++", ".NET", "PostgreSQL"]

    def gerar_justificativa(self, matches, score):
        if score >= 70:
            principais = ", ".join(matches[:2])
            return f"Candidatura forte! Foco em {principais}. Sua experiência prática em sistemas reais compensa as lacunas de ferramentas específicas."
        return f"Match técnico insuficiente ({score}%). A stack da vaga foca em tecnologias que não são seu forte no momento."

    def calcular_match(self, skills_usuario, descricao_vaga):
        vaga_lower = descricao_vaga.lower()
        skills_na_vaga = []
        for s in skills_usuario:
            variantes = self.sinonimos.get(s, [])
            if s.lower() in vaga_lower or any(v.lower() in vaga_lower for v in variantes):
                skills_na_vaga.append(s)

        score = round((len(skills_na_vaga) / 8) * 100, 2)
        score = max(0, min(100, score))

        return {
            "score": score,
            "matches": skills_na_vaga,
            "justificativa": self.gerar_justificativa(skills_na_vaga, score)
        }

    def parse_vagas(self, texto_vagas):
        vagas = []
        # Divide pelos separadores e remove espaços extras
        blocos = [b.strip() for b in texto_vagas.split(self.separator) if b.strip()]
    
        for bloco in blocos:
            linhas = bloco.strip().split('\n')
            if len(linhas) > 0:
                # Se houver apenas uma linha, assume que é a descrição e o link fica vazio
                link = linhas[-1].strip() if len(linhas) > 1 else "Link não informado"
            
                # Se houver mais de uma linha, a descrição é tudo menos a última
                if len(linhas) > 1:
                    descricao = " ".join(linhas[:-1]).strip()
                else:
                    descricao = linhas[0].strip()
                
                vagas.append({"link": link, "descricao": descricao})
        return vagas