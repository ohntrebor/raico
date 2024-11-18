import os
import openai
from dotenv import load_dotenv

# Carrega as variáveis do .env
load_dotenv()

# Obtém o token da API OpenAI do arquivo .env
openai_api_key = os.getenv("OPENAI_API_KEY")

# Verifica se o token foi carregado corretamente
if not openai_api_key:
    raise EnvironmentError("OPENAI_API_KEY não encontrado. Verifique seu arquivo .env.")

# Configura o token para a biblioteca OpenAI
openai.api_key = openai_api_key

# Teste básico para verificar a conexão com o ChatGPT
def test_openai_connection():
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um assistente útil."},
                {"role": "user", "content": "Teste de conexão. Está funcionando?"}
            ],
        )
        print("Conexão bem-sucedida!")
        print("Resposta do ChatGPT:", response['choices'][0]['message']['content'])
    except Exception as e:
        print("Erro ao conectar com a API OpenAI:", e)

# Executa o teste
if __name__ == "__main__":
    test_openai_connection()
