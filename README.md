#  🤖🫱🏽‍🫲🏽🐈‍⬛ RAICO (Review with Artificial Intelligence for Code Orchestration)

## **Repositório Exclusivo de Integração com IA para assitência em fluxos de trabalho, em especial o GitubAction**

O **RAICO** é um repositório focado em AI, que fornece integração simples entre repositórios terceiros para revisar Pull Requests (PRs). Ele utiliza o poder da OpenAI para:

- Analisar alterações de código.
- Verificar a aderência às melhores práticas.
- Identificar possíveis bugs.
- Sugerir melhorias.

Este repositório foi projetado para ser **reutilizável** por qualquer outro repositório. Basta configurar alguns parâmetros, como a **chave da OpenAI** e o **prompt personalizado**, para obter análises automatizadas e inteligentes dos seus PRs.

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
   - Processa as alterações usando a API da OpenAI.
   - Adiciona comentários automáticos no Pull Request com feedback detalhado.

---

## **📄 Estrutura Necessária do `.env`**

Certifique-se de configurar o arquivo `.env` com as seguintes variáveis no ambiente onde o script será executado, caso deseje clonar o repo e testar local:

```plaintext
OPENAI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxx // Preencha seu Token
GITHUB_TOKEN=yyyyyyyyyyy // Preencha seu Token
PR_NUMBER=x // Preencha o número do PR que quer testar
PROMPT_PATH=scripts/prompts/default_prompt.txt
GITHUB_REPOSITORY=ToFood/tofood-ai // Preencha seu repositório
OPENAI_MODEL=gpt-3.5-turbo
```

## 📖 Passo a Passo para Instalar e Rodar o Projeto

### **1. Clone o Repositório**

```bash
git clone https://github.com/ToFood/tofood-ai.git
cd tofood-ai
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

## Para revisar o PR com IA, você deve criar um arquivo.yml em seu repostório: .github\workflows\xxxxx.yml (lembre-se de cadastrar seu OPENAI_API_KEY no secrets do seu repositório)

```yaml
name: Analyze Pull Request with ToFood AI

on:
  pull_request:
    types: [opened, synchronize]

permissions:
  pull-requests: write
  contents: write

jobs:
  analyze:
    runs-on: ubuntu-latest

    steps:
      - name: 🐈‍⬛ Run Pull Request Analysis
        uses: ToFood/tofood-ai/.github/actions/analyze-pr@main
        with:
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}
          openai_model: gpt-3.5-turbo
          github_token: ${{ secrets.GITHUB_TOKEN }}
          prompt_text: |
            Analise este Pull Request. Verifique:
            - Melhorias de código e aderência às boas práticas.
            - Possíveis bugs ou inconsistências.
            - Sugestões de melhorias.
```

## 🐈‍⬛ Após a configuração, dando sucesso ou erro, as sugestões da IA aparecerão como comentários do seu PR, facilitando assim a leitura

![image](https://github.com/user-attachments/assets/9d2cbba7-60a8-4e58-87b4-72f097796802)

