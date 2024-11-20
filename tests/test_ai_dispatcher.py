import os
import pytest
from dotenv import load_dotenv
from scripts.ai_dispatcher import ai_dispatcher

# Carrega as variáveis do .env (local)
load_dotenv()

@pytest.mark.openai
def test_ai_dispatcher_openai():
    """
    Testa o fluxo completo usando o provedor OpenAI e os valores definidos no .env.
    """
    # Define explicitamente o provider como OpenAI
    os.environ["AI_PROVIDER"] = "openai"

    try:
        # Executa o dispatcher
        ai_dispatcher()
    except Exception as e:
        pytest.fail(f"Teste falhou para o provedor OpenAI: {e}")

@pytest.mark.gemini
def test_ai_dispatcher_gemini():
    """
    Testa o fluxo completo usando o provedor Gemini e os valores definidos no .env.
    """
    # Define explicitamente o provider como Gemini
    os.environ["AI_PROVIDER"] = "gemini"

    try:
        # Executa o dispatcher
        ai_dispatcher()
    except Exception as e:
        pytest.fail(f"Teste falhou para o provedor Gemini: {e}")

@pytest.mark.invalid
def test_ai_dispatcher_invalid_provider():
    """
    Testa o fluxo quando um provedor inválido é definido.
    """
    # Define um provedor inválido
    os.environ["AI_PROVIDER"] = "invalid_provider"

    with pytest.raises(ValueError, match="Provedor de IA 'invalid_provider' não suportado/implementado."):
        ai_dispatcher()
