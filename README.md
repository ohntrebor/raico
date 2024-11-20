# 🐈‍⬛ RAICO (Review with Artificial Intelligence for Code Orchestration)

## **Repositório Exclusivo de Integração com IA para assitência em fluxos de trabalho, em especial o GitubAction**

O **RAICO** é um repositório focado em AI, que fornece integração simples entre repositórios terceiros para revisar Pull Requests (PRs). Ele utiliza o poder da AI para:

- Analisar alterações de código.
- Verificar a aderência às melhores práticas.
- Identificar possíveis bugs.
- Sugerir melhorias.

Este repositório foi projetado para ser **reutilizável** por qualquer outro repositório. Basta configurar alguns parâmetros, como a **chave da AI** e o **prompt personalizado**, para obter análises automatizadas e inteligentes dos seus PRs.

---

## **🎯 Objetivo**

1. **Centralização**:
   - Fornecer uma solução única de IA para revisar PRs em múltiplos repositórios.
2. **Reutilização**:
   - A lógica de revisão está configurada como uma **GitHub Action Reutilizável**.
3. **Análise Inteligente**:
   - Utilizar modelos como o **`gpt-4`** ou **`gpt-3.5-turbo`** para analisar Pull Requests, detectar possíveis problemas e sugerir melhorias.

---

## **🚀 Como Funciona**

1. Repositórios externos referenciam este repositório como uma **GitHub Action**.
2. Durante a execução do pipeline:
   - Captura as alterações do Pull Request.
   - Processa as alterações usando a AI de preferência.
   - Adiciona comentários automáticos no Pull Request com feedback detalhado.

---


## Para revisar seu PR com IA, basta APENAS colar código yml abaixo -> .github\workflows\meu-pipeline.yml

```yaml
name: RAICO Review

on:
  pull_request:
    types: [opened, synchronize]

permissions:
  pull-requests: write
  contents: write

env:
  AI_PROVIDER: "gemini"
  AI_MODEL: "gemini-1.5-flash-latest"
  PROMPT_TEXT: "Com base nas alterações realizadas no meu PR, gostaria de obter recomendações específicas sobre boas práticas de segurança e estilo de código, considerando que este projeto é um [descrição do projeto]. Por favor, analise as do meu PR e forneça sugestões práticas e contextualizadas para melhorar a qualidade do código, garantindo alinhamento com padrões de segurança e consistência com as melhores práticas do mercado."

jobs:
  analyze:
    runs-on: ubuntu-latest

    steps:

      - name: 🤖 Run Pull Request Review
        uses: ohntrebor/raico/.github/actions/analyze-pr@main
        with:
          ai_provider: ${{ env.AI_PROVIDER }} # No exemplo foi definida no pipe, mas pode cadastrar no seu repositório se preferir
          api_key: ${{ secrets.GEMINI_API_KEY }} # Cadastrar a API_KEY no secrests do seu repositório
          ai_model: ${{ env.AI_MODEL }} # No exemplo foi definida no pipe, mas pode cadastrar no seu repositório se preferir
          github_token: ${{ secrets.GITHUB_TOKEN }} # O Github gere automático em pipelines, não precisa gerar
          prompt_text: ${{ env.PROMPT_TEXT }} # No exemplo foi definida no pipe, mas pode cadastrar no seu repositório se preferir

```

## 🐈‍⬛ Após a configuração, dando sucesso ou erro, as sugestões da IA aparecerão como comentários do seu PR, facilitando assim a leitura

![alt text](print_ex_pr.png)








## Caso queira clonar o repositório em sua máquina e rodar localmente, siga o passa a passo logo abaixo:




## **📄 Estrutura Necessária do `.env`**

Certifique-se de configurar o arquivo `.env` com as seguintes variáveis no ambiente onde o script será executado, caso deseje clonar o repo e testar local:

```plaintext
ai_provider: openai // Qual AI você está utilizando
api_key: xxxxxxxxxxxxxxxxxxxxxx // Sua API-KEY de Integração com a AI
ai_model: gpt-3.5-turbo # Modelo da sua AI
github_token: ${{ secrets.GITHUB_TOKEN }} # Seu token do Github (é gerado automáticamente)
prompt_text: "........." # Comando para definir que tipo de análise você quer que a AI faça em relação as alterações do seu PR
```

## 📖 Passo a Passo para Instalar e Rodar o Projeto

### **1. Clone o Repositório**

```bash
git clone https://github.com/ohntrebor/raico.git
cd raico
```

### **2. Configure o Ambiente Virtual**

```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

### **3. Instale as Dependências**

```bash
pip install -r scripts/requirements.txt
```

### **4. Execute o script para simular a validação**

```bash
Execute o Script de Teste
```

