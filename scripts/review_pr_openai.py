from scripts.github_handler.commented_pr import GithubPRHandler
import openai
import requests

def review_pr_openai(ai_api_key, github_token, repo_name, pr_number, prompt_path, ai_model):
    """
    Função principal para revisar um Pull Request (PR) utilizando a API OpenAI.

    Args:
        ai_api_key (str): Chave de autenticação da API OpenAI.
        github_token (str): Token de autenticação do GitHub.
        repo_name (str): Nome do repositório no formato "owner/repo".
        pr_number (int): Número do Pull Request.
        prompt_path (str): Caminho para o arquivo de prompt personalizado.
        ai_model (str): Modelo da IA OpenAI (ex: gpt-4).
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

    def analyze_file_with_openai(file_path, file_content, prompt):
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

    try:
        # Carrega o prompt do arquivo especificado
        prompt = load_prompt()

        # Inicializa o manipulador de PRs do GitHub
        github_handler = GithubPRHandler(github_token)

        # Deleta os comentários anteriores
        github_handler.delete_previous_comments(
            github_handler.get_pull_request(repo_name, pr_number)
        )

        # Lista para consolidar o feedback gerado
        overall_feedback = []

        # Itera sobre os arquivos do PR e analisa
        pr = github_handler.get_pull_request(repo_name, pr_number)
        for file in pr.get_files():
            file_path = file.filename
            if not file.patch:
                print(f"Ignorando {file_path} (sem alterações no PR).")
                continue

            file_content = requests.get(file.raw_url).text
            feedback = analyze_file_with_openai(file_path, file_content, prompt)

            if "Erro ao processar o arquivo" in feedback:
                overall_feedback.append(
                    f"**Erro ao analisar o arquivo `{file_path}`:**\n\n{feedback}\n\n---"
                )
            else:
                overall_feedback.append(
                    f"### Arquivo: `{file_path}`\n\n{feedback}\n\n---"
                )

        # Publica o comentário no PR com o feedback consolidado
        github_handler.post_feedback_comment(repo_name, pr_number, overall_feedback)

    except Exception as e:
        print(f"Erro ao revisar o PR com OpenAI: {e}")
        github_handler.post_error_comment(repo_name, pr_number, str(e))
