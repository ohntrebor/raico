import os
import openai
import requests
from github import Github

#from dotenv import load_dotenv

# Carrega as variáveis do .env automaticamente
#load_dotenv()

# Configurações globais
openai_api_key = os.getenv("OPENAI_API_KEY")
github_token = os.getenv("GITHUB_TOKEN")
repo_name = os.getenv("GITHUB_REPOSITORY")
pr_number = os.getenv("PR_NUMBER")
prompt_path = os.getenv("PROMPT_PATH", "scripts/prompts/default_prompt.txt")
openai_model = os.getenv("OPENAI_MODEL", "gpt-4")  # Modelo padrão: gpt-4

# Configurações da API OpenAI
openai.api_key = openai_api_key

# Função para carregar o prompt
def load_prompt():
    try:
        with open(prompt_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Prompt file não encontrado em: {prompt_path}")

# Função para testar a conexão com a API OpenAI
def test_openai_connection():
    print(f"Testando conexão com a API OpenAI usando o modelo {openai_model}...")
    try:
        response = openai.ChatCompletion.create(
            model=openai_model,
            messages=[{"role": "user", "content": "Teste de conexão. Está funcionando?"}],
        )
        print("Conexão com a API OpenAI bem-sucedida!")
    except openai.error.OpenAIError as e:
        raise Exception(f"Erro ao conectar com a API OpenAI: {e}")

# Função principal de análise
def analyze_file(file_path, file_content, prompt):
    full_prompt = f"""
    {prompt}
    Caminho: {file_path}
    Código:
    ```
    {file_content}
    ```
    """
    try:
        response = openai.ChatCompletion.create(
            model=openai_model,
            messages=[{"role": "user", "content": full_prompt}],
        )
        return response['choices'][0]['message']['content']
    except openai.error.OpenAIError as e:
        return f"Erro ao processar o arquivo {file_path} com o modelo {openai_model}: {e}"

# Conexão com o GitHub e revisão
def review_pr():
    try:
        # Testa conexão com a API OpenAI antes de prosseguir
        test_openai_connection()

        g = Github(github_token)
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(int(pr_number))

        # Pega o commit_id do último commit no PR
        last_commit = pr.get_commits().reversed[0]
        commit_id = last_commit.sha

        prompt = load_prompt()
        print(f"Analisando PR #{pr_number} no repositório {repo_name} usando o modelo {openai_model}...")

        for file in pr.get_files():
            file_path = file.filename

            # Verifica se o arquivo faz parte do diff do PR
            if not file.patch:
                print(f"Ignorando {file_path} (sem alterações no PR).")
                continue

            # Define a posição inicial no diff (primeira linha modificada)
            position = 1

            # Baixa o conteúdo do arquivo
            file_content = requests.get(file.raw_url).text
            feedback = analyze_file(file_path, file_content, prompt)

            print(f"Tentando comentar no arquivo: {file_path} no commit {commit_id} na posição {position}")
            try:
                pr.create_review_comment(
                    body=feedback,
                    path=file_path,
                    position=position,
                    commit_id=commit_id
                )
                print(f"Comentário adicionado no arquivo: {file_path}")
            except Exception as e:
                print(f"Erro ao comentar no arquivo {file_path}: {e}")

        print("Análise do PR concluída com sucesso!")

    except Exception as e:
        print(f"Erro ao revisar o PR: {e}")
        try:
            # Posta o erro como comentário no PR
            g = Github(github_token)
            repo = g.get_repo(repo_name)
            pr = repo.get_pull(int(pr_number))
            pr.create_issue_comment(
                f"**Erro na análise automatizada pela RAICO:**\n\n{str(e)}"
            )
        except Exception as comment_error:
            print(f"Falha ao postar o erro no PR: {comment_error}")

if __name__ == "__main__":
    review_pr()
