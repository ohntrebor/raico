## 🦾 RAICO (Review with Artificial Intelligence for Code Optimization)

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
# Workflow para revisão de Pull Requests utilizando IA
name: 🤖 AI Review PR

on:
  pull_request:
    types: [opened, synchronize] # Ação disparada em PRs abertos e sincronizados

# Permissões necessárias para o workflow
permissions:
  pull-requests: write # Permite alterar PRs, como adicionar comentários
  contents: write      # Necessário para acessar e ler o conteúdo do repositório

# Variáveis de ambiente centralizadas para facilitar manutenção
env:
  AI_PROVIDER: "gemini"                    # Provedor de IA utilizado no pipeline
  AI_MODEL: "gemini-1.5-flash-latest"      # Modelo de IA a ser usado
  AI_VERSION: "v1beta"                     # Versão da API da IA
  PROMPT: |                                # Prompt de instruções enviado para a IA
    Você é um especialista em revisão de código para Pull Requests. Seu objetivo é identificar problemas e analisar alterações no código de forma crítica, seguindo boas práticas globais e critérios técnicos relevantes. Sua análise deve ser sempre breve, objetiva e focada.

    ### Regras para Revisão:

    #### Determinação da Aprovação do PR:
    1. **❌ Alterações reprovadas:** Identifique problemas críticos que possam causar um exception no sistema, como:
      - Potenciais exceções não tratadas
      - Vulnerabilidades de segurança.
      - Bugs ou erros de execução.
      - Erros de sintaxe.
      - Incompatibilidades de tipo.
      - Falta de declarações.
      Forneça uma explicação clara e concisa do problema, indicando o trecho exato do código e apresentando uma solução alternativa funcional.

    2. **⚠️ Alterações aprovadas com ressalvas:** Caso o código esteja funcional, mas apresente:
      - Problemas de performance.
      - Redundâncias ou necessidade de refatoração.
      - Melhorias possíveis na legibilidade ou manutenção.
      Apresente os pontos de melhoria diretamente no trecho do código relevante, com um exemplo concreto de correção.

    3. **✅ Alterações aprovadas:** O código atende às melhores práticas, é funcional e não apresenta problemas críticos. Parabenize brevemente o autor pela solução e reforce os pontos positivos.

    #### Foco e Critérios de Avaliação:
    - **Evitar irrelevâncias:** Não faça sugestões de impacto mínimo.
    - **Foco em problemas reais:** Concentre-se exclusivamente em:
      - Erros ou bugs no código.
      - Segurança do sistema.
      - Otimização de desempenho.
      - Legibilidade e clareza.
    - **Regras de boas práticas:** Siga os padrões do .NET 6.0 e diretrizes globais.

    #### Como fornecer feedback:
    - Aponte o trecho exato do código onde há um problema ou oportunidade de melhoria.
    - Explique a questão de forma prática e direta.
    - Ofereça uma solução ou exemplo claro e funcional para corrigir ou melhorar o código.

# Definição do job principal para revisão de PRs
jobs:
  ai-review-pr:
    name: 🤖 AI Review PR # Nome do job exibido no GitHub Actions
    runs-on: ubuntu-latest # Runner utilizado para executar o workflow

    steps:
      - name: Run PR Review
        uses: ohntrebor/raico/.github/actions/review-pr@main # Ação que executa a revisão de PR
        with:
          ai_provider: ${{ env.AI_PROVIDER }} # Provedor de IA (usando a variável centralizada)
          ai_api_key: ${{ secrets.GEMINI_API_KEY }} # API Key configurada nos secrets do repositório
          ai_model: ${{ env.AI_MODEL }} # Modelo de IA (referenciado na variável env)
          ai_version: ${{ env.AI_VERSION }} # Versão da API (referenciado na variável env)
          github_token: ${{ secrets.GITHUB_TOKEN }} # Token de autenticação padrão do GitHub Actions
          review_type: 2 # Tipo de revisão (e.g., 1 = por arquivo, 2 = Por alterações)
          prompt: ${{ env.PROMPT }} # Prompt definido na seção env, para maior clareza


# review_type: 1 Review Files, é um review por arquivos modificados, consome mais tokens por ser um review mais completo
# review_type: 2 Review Lines, é um review por lonhas modificadas, consome menos tokens por ser um review menos completo 
```

## 🐈‍⬛ Após incluir o pipeline em seu repositório, as sugestões/correções/elogios serão comentadas pela IA em seu PR, ex:
obs: Os comentários gerados pela IA serão atualizados a cada novo push na branch do PR, garantindo que apenas o feedback mais recente seja mantido, enquanto os comentários anteriores são deletados automaticamente.

![image](https://github.com/user-attachments/assets/537291b4-182d-419a-b55f-6d592491f5cc)




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
