import openai
import requests
from github import Github

def review_pr_openai(ai_api_key, github_token, repo_name, pr_number, prompt_path, ai_model):
    """
    Função principal para analisar Pull Requests usando OpenAI.

    Args:
        ai_api_key (str): Chave de autenticação da API OpenAI.
        github_token (str): Token de autenticação do GitHub.
        repo_name (str): Nome do repositório no formato "owner/repo".
        pr_number (int): Número do Pull Request.
        prompt_path (str): Caminho para o arquivo de prompt personalizado.
        ai_model (str): Modelo OpenAI a ser usado (ex: gpt-4).
    """
    # Configuração da chave da API OpenAI
    openai.api_key = ai_api_key

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
                model=ai_model,
                messages=[{"role": "user", "content": full_prompt}],
            )
            # Retorna a mensagem gerada pela IA
            return response['choices'][0]['message']['content']
        except openai.error.OpenAIError as e:
            # Retorna uma mensagem de erro específica para o arquivo
            return f"Erro ao processar o arquivo {file_path} com o modelo {ai_model}: {e}"

    def delete_previous_comments(pr, github_token, repo_name, bot_username="github-actions[bot]"):
        """
        Deleta os comentários anteriores feitos pelo bot no Pull Request.

        Args:
            pr (PullRequest): Objeto do Pull Request do GitHub.
            github_token (str): Token de autenticação do GitHub.
            repo_name (str): Nome do repositório no formato "owner/repo".
            bot_username (str): Nome do bot autor dos comentários (default: github-actions[bot]).
        """
        # Cabeçalhos para autenticação na API REST do GitHub
        headers = {"Authorization": f"Bearer {github_token}"}

        # Obtém todos os comentários no PR
        comments = pr.get_issue_comments()
        for comment in comments:
            # Filtra comentários feitos pelo bot
            if comment.user.login == bot_username:
                try:
                    # Deleta o comentário via API REST
                    url = f"https://api.github.com/repos/{repo_name}/issues/comments/{comment.id}"
                    response = requests.delete(url, headers=headers)
                    if response.status_code == 204:
                        print(f"Comentário deletado: {comment.id}")
                    else:
                        print(f"Erro ao deletar comentário {comment.id}: {response.text}")
                except Exception as e:
                    print(f"Erro ao deletar comentário {comment.id}: {e}")

    try:
        # Carrega o prompt do arquivo especificado
        prompt = load_prompt()

        # Conecta-se ao GitHub utilizando o token
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(int(pr_number))

        # Deleta os comentários anteriores feitos pelo bot
        delete_previous_comments(pr, github_token, repo_name)

        # Lista para armazenar feedbacks e erros de análise
        overall_feedback = []
        analyzed_files = set()  # Mantém controle dos arquivos já analisados

        # Itera sobre todos os arquivos do PR (independentemente dos commits)
        for file in pr.get_files():
            file_path = file.filename

            # Ignora arquivos sem alterações no patch
            if not file.patch:
                print(f"Ignorando {file_path} (sem alterações no PR).")
                continue

            # Verifica se o arquivo já foi analisado
            if file_path in analyzed_files:
                print(f"Ignorando {file_path} (já analisado).")
                continue

            # Marca o arquivo como analisado
            analyzed_files.add(file_path)

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
            f"**Análise Automática do PR pelo RAICO 🤖:**\n\n" + "\n\n".join(overall_feedback)
        )
        pr.create_issue_comment(summary)
        print("Comentário do resumo do PR criado com sucesso!")

    except Exception as e:
        # Lida com erros gerais durante o processo de análise
        print(f"Erro ao revisar o PR: {e}")
        pr.create_issue_comment(f"**Erro na análise automatizada pelo RAICO 🤖:**\n\n{str(e)}")
