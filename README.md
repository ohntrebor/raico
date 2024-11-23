## 🦾 RAICO (Review with Artificial Intelligence for Code Orchestration)

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
   - Utilizar modelos como por exemplo o **`gpt-3.5-turbo`** da OPENAI para analisar Pull Requests, detectar possíveis problemas e sugerir melhorias.

---

## **ℹ️ Como Funciona**

1. Repositórios externos referenciam este repositório como uma **GitHub Action**.
2. Durante a execução do pipeline:
   - Captura as alterações do Pull Request.
   - Processa as alterações usando a AI de preferência.
   - Adiciona comentários automáticos no Pull Request com feedback detalhado Ccom base no prompt passado.

---

## **🤖 Como Usar**
➡️ Para revisar seu PR com IA, copie e cole o código YAML abaixo no arquivo .github/workflows/meu-pipeline.yml do seu repositório 😁:

```yaml
name: 🤖 AI Review PR

on:
  pull_request:
    types: [opened, synchronize]

permissions:
  pull-requests: write
  contents: write

env:
  AI_PROVIDER: "openai"
  AI_MODEL: "gpt-3.5-turbo"
  AI_VERSION: ""
  PROMPT: |
    Você é um especialista em revisão de código para Pull Requests. Revise as alterações de forma crítica e prática, focando em segurança, performance, legibilidade e manutenção. Sua análise deve:
      - Apresente apenas pontos que impactam segurança, performance, legibilidade ou manutenção. Evite ao máximo recomendações desnecessárias, se estiver tudo acerto, apenas diga que o PR está apto para o merge, e parabenize o autor.
      - Caso haja problemas criticos ou melhorias significativas, apenas cite, demonstrando como corrigir com exemplos de código claros e curtos.
      - ❌ Rejeite o PR se houver problemas críticos (bugs, segurança, erros graves). Explique claramente o problema, mostre o trecho problemático e sugira uma correção com exemplo.
      - ⚠️ Aprove o PR com ressalvas se funcional, mas com melhorias possíveis. Dê sugestões objetivas para refinar o código.
      - ✅ Aprove o PR se estiver excelente, parabenize e destaque brevemente o que foi bem executado.



jobs:
  raico-review-pr:
    runs-on: ubuntu-latest

    steps:

      - name: 🤖 Run Pull Request Review
        uses: ohntrebor/raico/.github/actions/review-pr@main
        with:
          ai_provider: ${{ env.AI_PROVIDER }} # No exemplo foi definida no pipe, mas pode cadastrar no seu repositório se preferir
          ai_api_key: ${{ secrets.OPENAI_API_KEY }} # Cadastrar a API_KEY no secrests do seu repositório
          ai_model: ${{ env.AI_MODEL }} # No exemplo foi definida no pipe, mas pode cadastrar no seu repositório se preferir
          #ai_version: ${{ env.AI_VERSION }} # (opcional) dependendo da AI será solicitado uma versão
          github_token: ${{ secrets.GITHUB_TOKEN }} # O Github gere automático em pipelines, não precisa gerar
          review_type: 2
          prompt: ${{ env.PROMPT }} # (opcional) Caso não defina um prompt aqui, será considerado o prompt default do repositório RAICO

# review_type: 1 Review Files, é um review por arquivos modificados, consome mais tokens por ser um review mais completo
# review_type: 2 Review Lines, é um review por lonhas modificadas, consome menos tokens por ser um review menos completo 
```

## 🐈‍⬛ Após incluir o pipeline em seu repositório, as sugestões/correções/elogios serão comentadas pela IA em seu PR, ex:
obs: Os comentários gerados pela IA serão atualizados a cada novo push na branch do PR, garantindo que apenas o feedback mais recente seja mantido, enquanto os comentários anteriores são deletados automaticamente.

![image](https://github.com/user-attachments/assets/85e81e1d-884e-45cd-95b5-564642915cac)



<br><br>

<hr>





## 🖥️ Caso queira clonar o repositório em sua máquina e rodar localmente, siga o passa a passo logo abaixo:




## **📄 Estrutura Necessária do `.env`**

Certifique-se de configurar o arquivo `.env` com as seguintes variáveis no ambiente onde o script será executado, caso deseje clonar o repo e testar local:

```plaintext
  AI_PROVIDER: "gemini"
  AI_API_KEY: "xxxxxxxxxxxxxxxxxxxxxx"
  AI_MODEL: "gemini-1.5-flash-latest"
  AI_VERSION: "v1beta"
  GITHUB_REPOSITORY: "github.com/seu-github/seu-repo"
  GITHUB_TOKEN: "seu github token"
  PR_NUMBER: "7" // Número do PR que você quer revisar (do seu repo)
  PROMPT_PATH: "scripts/prompts/review_pr_default.txt" // mantenha esse path, e altere o prompt a partir desse arquivo
```

## 📖 Configuração Dinâmica do Projeto

### **1. Clone o Repositório**

```bash
git clone https://github.com/ohntrebor/raico.git
cd raico
```

### **2. Configurando Ambiente - Windows**

```bash
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
.\setup_raico.ps1

```


### **2. Configurando Ambiente - Linux**

```bash
chmod +x setup_raico.sh
./setup_raico.sh
```

### **2. Configurando Ambiente - Manual**

```bash
Você pode analisar o passo a passo nos arquivos de configuração e instalar manualmente em seu terminal
```

### **Caso queira testar após configurar o projeto e atualizar o .env:**

```bash
pytest -m gemini # exemplo, rodando Gemini
pytest -m openai # exemplo, rodando Chat-GPT
```
