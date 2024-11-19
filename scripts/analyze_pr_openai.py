import openai
import requests
from github import Github

def review_pr(openai_api_key, github_token, repo_name, pr_number, prompt_path, openai_model):
    """
    Função principal para analisar Pull Requests usando OpenAI.

    Args:
        openai_api_key (str): Chave de autenticação da API OpenAI.
        github_token (str): Token de autenticação do GitHub.
        repo_name (str): Nome do repositório no formato "owner/repo".
        pr_number (int): Número do Pull Request.
        prompt_path (str): Caminho para o arquivo de prompt personalizado.
        openai_model (str): Modelo OpenAI a ser usado (ex: gpt-4).
    """
    # Configuração da chave da API OpenAI
    openai.api_key = openai_api_key

    def load_prompt():
        """
        Carrega o texto do prompt a partir de um arquivo.
        
        Returns:
            str: Texto do prompt.
        """
        try:
            with open(prompt_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file não encontrado em: {prompt_path}")

    def analyze_file(file_path, file_content, prompt):
        """
        Analisa o conteúdo de um arquivo com base no modelo OpenAI e no prompt.

        Args:
            file_path (str): Caminho do arquivo.
            file_content (str): Conteúdo do arquivo.
            prompt (str): Texto do prompt.

        Returns:
            str: Resposta do modelo OpenAI.
        """
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

    try:

        # Carrega o prompt do arquivo especificado
        prompt = load_prompt()

        # Conecta-se ao GitHub
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(int(pr_number))

        # Itera sobre todos os commits do PR
        commits = pr.get_commits()
        for commit in commits:
            commit_id = commit.sha  # Obtém o SHA do commit atual
            print(f"Analisando arquivos no commit: {commit_id}")

            # Itera sobre os arquivos alterados no commit
            for file in commit.files:
                file_path = file.filename  # Nome do arquivo

                # Verifica se o arquivo contém alterações (patch)
                if not file.patch:
                    print(f"Ignorando {file_path} (sem alterações no commit).")
                    continue

                # Faz o download do conteúdo do arquivo
                file_content = requests.get(file.raw_url).text

                # Analisa o arquivo com o modelo OpenAI
                feedback = analyze_file(file_path, file_content, prompt)

                # Tenta adicionar um comentário no PR
                try:
                    pr.create_review_comment(
                        body=feedback,
                        path=file_path,
                        position=1,  # Comenta na primeira linha do diff
                        commit_id=commit_id  # Relaciona o comentário ao commit atual
                    )
                    print(f"Comentário adicionado no arquivo: {file_path}")
                except Exception as e:
                    print(f"Erro ao comentar no arquivo {file_path}: {e}")

        print("Análise do PR concluída com sucesso!")

    except Exception as e:
        # Lida com erros gerais durante a análise
        print(f"Erro ao revisar o PR: {e}")
        try:
            # Cria um comentário no PR relatando o erro
            repo.get_pull(int(pr_number)).create_issue_comment(
                f"**Erro na análise automatizada pela RAICO:**\n\n{str(e)}"
            )
        except Exception as comment_error:
            print(f"Falha ao postar o erro no PR: {comment_error}")
