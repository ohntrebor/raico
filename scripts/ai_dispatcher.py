import os
from enum import Enum
from scripts.gemini_pr_review_file import gemini_pr_review_file
from scripts.gemini_pr_review_line import gemini_pr_review_line
from scripts.openai_pr_review_file import openai_pr_review_file
from scripts.openai_pr_review_line import openai_pr_review_line

class ReviewType(Enum):
    FILE_DIFF_REVIEW = "1"
    LINE_DIFF_REVIEW = "2"

def ai_dispatcher():
    """
    Dispatcher para decidir qual lógica de análise usar com base no ai_provider e review_type.
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
    review_type = os.getenv("REVIEW_TYPE", ReviewType.LINE_DIFF_REVIEW.value)

    # Provider OpenAI - File Diff Review
    def method_openai_pr_review_file():
        return openai_pr_review_file(
            ai_api_key=ai_api_key,
            github_token=github_token,
            repo_name=repo_name,
            pr_number=pr_number,
            prompt_path=prompt_path,
            ai_model=ai_model
        )

    # Provider OpenAI - Line Diff Review
    def method_openai_pr_review_line():
        return openai_pr_review_line(
            ai_api_key=ai_api_key,
            github_token=github_token,
            repo_name=repo_name,
            pr_number=pr_number,
            ai_model=ai_model,
            prompt_path=prompt_path,
        )

    # Provider Gemini - File Diff Review
    def method_gemini_pr_review_file():
        return gemini_pr_review_file(
            ai_api_key=ai_api_key,
            github_token=github_token,
            repo_name=repo_name,
            pr_number=pr_number,
            prompt_path=prompt_path,
            ai_model=ai_model,
            ai_version=ai_version
        )

    # Provider Gemini - Line Diff Review
    def method_gemini_pr_review_line():
        return gemini_pr_review_line(
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
        "openai": {
            ReviewType.FILE_DIFF_REVIEW.value: method_openai_pr_review_file,
            ReviewType.LINE_DIFF_REVIEW.value: method_openai_pr_review_line,
        },
        "gemini": {
            ReviewType.FILE_DIFF_REVIEW.value: method_gemini_pr_review_file,
            ReviewType.LINE_DIFF_REVIEW.value: method_gemini_pr_review_line,

        },
    }

    # Executar o método correspondente ao ai_provider e review_type
    try:
        if ai_provider in provider_methods:
            if review_type in provider_methods[ai_provider]:
                provider_methods[ai_provider][review_type]()  # Chama o método correto
            else:
                raise ValueError(f"Tipo de revisão '{review_type}' não suportado para o provedor '{ai_provider}'.")
        else:
            raise ValueError(f"Provedor de IA '{ai_provider}' não suportado.")
    except Exception as e:
        print(f"Erro ao executar o provedor de IA '{ai_provider}' com tipo de revisão '{review_type}': {e}")
        raise

if __name__ == "__main__":
    ai_dispatcher()
