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
            # Lança um erro caso o arquivo de prompt não seja encontrado
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
        # Cria o prompt completo com o conteúdo do arquivo e o prompt personalizado
        full_prompt = f"""
        {prompt}
        Caminho: {file_path}
        Código:
        ```
        {file_content}
        ```
        """
        try:
            # Chamada para a API OpenAI
            response = openai.ChatCompletion.create(
                model=openai_model,
                messages=[{"role": "user", "content": full_prompt}],
            )
            # Retorna a mensagem gerada pela IA
            return response['choices'][0]['message']['content']
        except openai.error.OpenAIError as e:
            # Retorna uma mensagem de erro específica para o arquivo
            return f"Erro ao processar o arquivo {file_path} com o modelo {openai_model}: {e}"

    try:
        # Carrega o prompt do arquivo especificado
        prompt = load_prompt()

        # Conecta-se ao GitHub utilizando o token
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(int(pr_number))

        # Lista para armazenar feedbacks e erros de análise
        overall_feedback = []

        # Itera sobre todos os commits do PR
        commits = pr.get_commits()
        for commit in commits:
            commit_id = commit.sha
            print(f"Analisando arquivos no commit: {commit_id}")

            # Itera sobre os arquivos alterados no commit
            for file in commit.files:
                file_path = file.filename

                # Ignora arquivos sem alterações no patch
                if not file.patch:
                    print(f"Ignorando {file_path} (sem alterações no commit).")
                    continue

                # Faz o download do conteúdo do arquivo
                file_content = requests.get(file.raw_url).text

                # Analisa o arquivo com o modelo OpenAI
                feedback = analyze_file(file_path, file_content, prompt)

                # Adiciona feedback ou mensagem de erro ao resumo consolidado
                if "Erro ao processar o arquivo" in feedback:
                    overall_feedback.append(
                        f"**Erro ao analisar o arquivo `{file_path}`:**\n\n{feedback}\n\n---"
                    )
                else:
                    overall_feedback.append(
                        f"### Arquivo: `{file_path}`\n\n{feedback}\n\n---"
                    )

        # Gera o comentário consolidado com todos os feedbacks
        summary = (
            f"**Análise Automática do PR pela RAICO:**\n\n" + "\n\n".join(overall_feedback)
        )
        pr.create_issue_comment(summary)
        print("Comentário do resumo do PR criado com sucesso!")

    except Exception as e:
        # Lida com erros gerais durante o processo de análise
        print(f"Erro ao revisar o PR: {e}")
        post_error_comment(github_token, repo_name, pr_number, str(e))
