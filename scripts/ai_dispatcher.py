import os
from scripts.analyze_pr_openai import review_pr_openai
from scripts.analyze_pr_gemini import review_pr_gemini  # Importa o método para o Gemini

def ai_dispatcher():
    """
    Dispatcher para decidir qual lógica de análise usar com base no ai_provider.
    """
    # Carregar variáveis do ambiente
    ai_provider = os.getenv("AI_PROVIDER")
    ai_api_key = os.getenv("AI_API_KEY")
    ai_model = os.getenv("AI_MODEL")
    ai_version = os.getenv("AI_VERSION")
    github_token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY")
    pr_number = os.getenv("PR_NUMBER")
    prompt_path = os.getenv("PROMPT_PATH", "scripts/prompts/review_pr_default.txt")




    # Provider OpenAI
    def openai_method():
        return review_pr_openai(
            ai_api_key=ai_api_key,
            github_token=github_token,
            repo_name=repo_name,
            pr_number=pr_number,
            prompt_path=prompt_path,
            openai_model=ai_model
        )

    # Provider Gemini
    def gemini_method():
        return review_pr_gemini(
            ai_api_key=ai_api_key,
            github_token=github_token,
            repo_name=repo_name,
            pr_number=pr_number,
            prompt_path=prompt_path,
            ai_model=ai_model,
            ai_version=ai_version
        )

    # Provedores Integrados
    provider_methods = {
        "openai": openai_method,
        "gemini": gemini_method,
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
