# MatchEngine - Analisador Estratégico de Vagas

O MatchEngine é uma ferramenta de automação voltada para a análise de aderência entre perfis profissionais e descrições de vagas de tecnologia. O sistema processa currículos em formato PDF e realiza uma comparação semântica com os requisitos de múltiplas vagas, gerando relatórios de compatibilidade e identificando lacunas críticas de palavras-chave.

## Funcionalidades Principais

* **Extração de Dados de PDF:** Utiliza a biblioteca `pdfplumber` para converter currículos não estruturados em texto processável de forma automatizada.
* **Análise Semântica:** Implementa um dicionário de sinônimos para validar competências, garantindo que variações de nomenclatura (ex: .NET vs C#) não prejudiquem o score de compatibilidade.
* **Auditoria de Keywords:** O motor diferencia a ausência de tecnologias obrigatórias (Hard Skills) de sugestões de otimização de termos para sistemas de triagem (ATS).
* **Interface Dinâmica:** Migração de processamento via CLI para uma interface web funcional, permitindo a entrada de dados em tempo real sem dependência de arquivos estáticos.

## Estrutura do Projeto

* `app.py`: Interface web e orquestrador da camada de apresentação utilizando Streamlit.
* `analyzer.py`: Core da aplicação contendo a engine de análise, lógica de match e dicionário de normalização técnica.
* `analise_vagas_match.json`: Exportação estruturada dos resultados para persistência ou consumo por serviços externos.

## Stack Tecnológica

* **Python 3.12:** Linguagem core utilizada pela robustez no processamento de strings e integração de bibliotecas.
* **Streamlit:** Framework utilizado para transformar o motor de processamento backend em uma aplicação web reativa, abstraindo a complexidade do frontend.
* **Pandas:** Utilizado para a estruturação e manipulação eficiente de dados em memória (DataFrames), facilitando a exibição de métricas e relatórios.
* **PDFPlumber:** Biblioteca especializada para extração de texto e metadados de arquivos PDF, garantindo integridade na leitura de currículos.
* **Regular Expressions (Regex):** Implementação de padrões complexos para limpeza de dados, normalização de texto e identificação de lacunas técnicas.

## Fluxo de Execução

1. **Entrada de Parâmetros:** O usuário define sua stack tecnológica e carrega o arquivo PDF via interface web.
2. **Processamento em Memória:** O motor de análise extrai o conteúdo do PDF e o normaliza, eliminando ruídos e caracteres especiais.
3. **Parsing e Tokenização:** As descrições das vagas são segmentadas e processadas para identificação de requisitos técnicos.
4. **Cálculo de Aderência Técnica:** O sistema executa um cruzamento entre as competências declaradas e os requisitos da vaga, aplicando o dicionário de sinônimos para evitar falsos negativos.
5. **Relatório de Auditoria:** O backend gera uma análise detalhada, destacando o percentual de match e disparando alertas críticos caso competências dominadas pelo usuário não estejam explicitamente citadas no currículo analisado.
6. **IMPORTANTE**: Este projeto NÃO garante vagas, apenas ajuda o usuário a filtrar melhor suas vagas antes de de candidatar sem que ele passe muito tempo lendo descrições de vagas. Ainda sim é importante que a descrição seja lida caso não concorde com o "Match".

## Considerações Técnicas e Escalabilidade

O MatchEngine foi concebido sob a premissa de **modularidade**, permitindo que a lógica de comparação seja independente do nicho de mercado analisado.

### Limitações Atuais
* **Especialização de Domínio:** Atualmente, o dicionário de normalização técnica (`sinonimos`) está configurado para o setor de Tecnologia da Informação. Isso significa que o sistema possui alta precisão para identificar variações de stacks tecnológicas, mas requer atualização manual para compreender jargões de outras áreas (ex: Moda, Saúde ou Direito).
* **Dependência de Palavras-Chave:** A análise é baseada em extração textual e comparação semântica mapeada. Termos que não constam no dicionário de sinônimos precisam ser idênticos entre o currículo e a vaga para serem contabilizados.

### Possibilidades de Melhoria (Roadmap)

* **Dicionários Dinâmicos:** Implementação de uma camada de persistência (Banco de Dados ou arquivos JSON externos) para que o usuário possa alternar entre diferentes dicionários de competências baseados na área de atuação.
* **Integração com LLMs:** Substituição do dicionário estático por chamadas de API (como Gemini ou OpenAI) para realizar uma análise de contexto mais profunda, permitindo que o sistema entenda sinônimos de qualquer área de conhecimento de forma autônoma.
* **Interface de CRUD de Skills:** Desenvolvimento de uma funcionalidade na interface para que o usuário gerencie seus próprios sinônimos e competências em tempo real, sem necessidade de alteração no código-fonte.