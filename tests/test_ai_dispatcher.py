import os
import sys
import pytest
from dotenv import load_dotenv

# Adiciona o diretório raiz do projeto ao PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importa os métodos específicos
from scripts.review_pr_openai import review_pr_openai
from scripts.review_pr_gemini import review_pr_gemini

# Carrega as variáveis do .env (local)
load_dotenv()


@pytest.mark.openai
def test_review_pr_openai():
    """
    Testa o método review_pr_openai com os valores do .env.
    """
    # Carrega as variáveis do ambiente
    ai_api_key = os.getenv("AI_API_KEY")
    github_token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY")
    pr_number = os.getenv("PR_NUMBER")
    prompt_path = os.getenv("PROMPT_PATH")
    ai_model = os.getenv("AI_MODEL")

    try:
        # Executa o método específico para OpenAI
        review_pr_openai(
            ai_api_key=ai_api_key,
            github_token=github_token,
            repo_name=repo_name,
            pr_number=pr_number,
            prompt_path=prompt_path,
            ai_model=ai_model
        )
    except Exception as e:
        pytest.fail(f"Teste falhou para o provedor OpenAI: {e}")

@pytest.mark.gemini
def test_review_pr_gemini():
    """
    Testa o método review_pr_gemini com os valores do .env.
    """
    # Carrega as variáveis do ambiente
    ai_api_key = os.getenv("AI_API_KEY")
    github_token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY")
    pr_number = os.getenv("PR_NUMBER")
    prompt_path = os.getenv("PROMPT_PATH")
    ai_model = os.getenv("AI_MODEL")
    ai_version = os.getenv("AI_VERSION")

    try:
        # Executa o método específico para Gemini
        review_pr_gemini(
            ai_api_key=ai_api_key,
            github_token=github_token,
            repo_name=repo_name,
            pr_number=pr_number,
            prompt_path=prompt_path,
            ai_model=ai_model,
            ai_version=ai_version
        )
    except Exception as e:
        pytest.fail(f"Teste falhou para o provedor Gemini: {e}")
