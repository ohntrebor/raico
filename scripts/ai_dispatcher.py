import os
from scripts.analyze_pr_openai import review_pr as openai_review
# Importe aqui outros métodos para provedores diferentes, se necessário.

def ai_dispatcher():
    """
    Dispatcher para decidir qual lógica de análise usar com base no ai_provider.
    """
    # Carregar variáveis do ambiente
    ai_provider = os.getenv("AI_PROVIDER")
    api_key = os.getenv("API_KEY")
    github_token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY")
    pr_number = os.getenv("PR_NUMBER")
    prompt_path = os.getenv("PROMPT_PATH", "scripts/prompts/default_prompt.txt")
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4")

    # Definir um "switch" para provedores diferentes
    def openai_method():
        return openai_review(
            api_key=api_key,
            github_token=github_token,
            repo_name=repo_name,
            pr_number=pr_number,
            prompt_path=prompt_path,
            openai_model=openai_model
        )

    # Aqui podemos adicionar mais provedores no futuro
    provider_methods = {
        "openai": openai_method,
        # "gemini": gemini_method,  # Exemplo de outro provedor
        # "other_ai": other_ai_method,  # Adicione aqui outros métodos
    }

    # Executar o método correspondente ao ai_provider
    try:
        if ai_provider in provider_methods:
            provider_methods[ai_provider]()  # Chama o método correto
        else:
            raise ValueError(f"Provedor de IA '{ai_provider}' não suportado.")
    except Exception as e:
        print(f"Erro ao executar o provedor de IA '{ai_provider}': {e}")
        raise

if __name__ == "__main__":
    ai_dispatcher()
