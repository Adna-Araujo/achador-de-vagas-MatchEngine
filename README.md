# MatchEngine - Analisador Estratégico de Vagas

O MatchEngine é uma ferramenta de automação voltada para a análise de aderência entre perfis profissionais e descrições de vagas de tecnologia. O sistema processa currículos em formato PDF e realiza uma comparação semântica com os requisitos de múltiplas vagas, gerando relatórios de compatibilidade e identificando lacunas críticas de palavras-chave.

## Funcionalidades Principais

* **Extração de Dados de PDF:** Utiliza a biblioteca `pdfplumber` para converter currículos não estruturados em texto processável de forma automatizada.
* **Análise Semântica:** Implementa um dicionário de sinônimos para validar competências, garantindo que variações de nomenclatura (ex: .NET vs C#) não prejudiquem o score de compatibilidade.
* **Priorização de Lacunas:** O motor diferencia a ausência de tecnologias obrigatórias (Hard Skills) de sugestões de melhoria de SEO para o currículo.
* **Processamento em Lote:** Capacidade de analisar diversas vagas simultaneamente a partir de um arquivo de entrada centralizado, otimizando o tempo de triagem.

## Estrutura do Projeto

* `main.py`: Orquestrador do fluxo de execução e interface de saída via terminal.
* `analyzer.py`: Motor de análise contendo a lógica de match e as definições de sinônimos.
* `skills.txt`: Arquivo de configuração contendo a stack tecnológica do usuário para cruzamento de dados.
* `vagas_analise.txt`: Repositório de entrada para as descrições das vagas coletadas.
* `analise_vagas_match.json`: Saída estruturada dos dados para persistência ou integração com dashboards de métricas.

## Tecnologias Utilizadas

* Python 3.12
* PDFPlumber (Extração de texto e metadados)
* Regular Expressions (Limpeza, normalização e extração de padrões)
* JSON (Estruturação de relatórios e persistência de dados)

## Fluxo de Execução

1. **Leitura de Configurações:** O sistema carrega a lista de competências técnicas definidas pelo usuário no arquivo de texto.
2. **Processamento do Currículo:** O texto do currículo em PDF é extraído, normalizado e armazenado em memória para comparação.
3. **Parsing de Vagas:** O sistema segmenta o arquivo de entrada de vagas, identificando links e descrições técnicas.
4. **Cálculo de Match:** Cada vaga é processada individualmente, onde o motor calcula um score percentual baseado na presença de tecnologias e seus sinônimos.
5. **Auditoria de Keywords:** O sistema verifica se as tecnologias encontradas na vaga estão presentes no texto do currículo, emitindo alertas caso uma skill dominada pelo usuário não tenha sido citada explicitamente no documento PDF.