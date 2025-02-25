from scripts.github_handler.commented_pr import GithubPRHandler
import anthropic
import requests

def claude_pr_review_file(ai_api_key, github_token, repo_name, pr_number, prompt_path, ai_model="claude-2"):
    """
    Função principal para revisar um Pull Request (PR) utilizando a API Claude AI (Anthropic),
    analisando arquivos completos.

    Args:
        ai_api_key (str): Chave de autenticação da API Claude (Anthropic).
        github_token (str): Token de autenticação do GitHub.
        repo_name (str): Nome do repositório no formato "owner/repo".
        pr_number (int): Número do Pull Request.
        prompt_path (str): Caminho para o arquivo de prompt personalizado.
        ai_model (str): Modelo da IA Claude (ex: claude-2).
    """

    client = anthropic.Anthropic(api_key=ai_api_key)

    def load_prompt():
        """
        Carrega o texto do prompt a partir de um arquivo.

        Returns:
            str: Texto do prompt.
        """
        try:
            with open(prompt_path, 'r', encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file não encontrado em: {prompt_path}")

    def analyze_file_with_claude(file_path, file_content, prompt):
        """
        Analisa o conteúdo de um arquivo com base no modelo Claude AI e no prompt.

        Args:
            file_path (str): Caminho do arquivo.
            file_content (str): Conteúdo do arquivo.
            prompt (str): Texto do prompt.

        Returns:
            str: Resposta do modelo Claude.
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
            response = client.messages.create(
                model=ai_model,
                max_tokens=1000,
                messages=[{"role": "user", "content": full_prompt}]
            )
            return response.content[0].text
        except anthropic.APIError as e:
            return f"Erro ao processar o arquivo {file_path} com o modelo {ai_model}: {e}"

    try:
        prompt = load_prompt()
        github_handler = GithubPRHandler(github_token)

        github_handler.delete_previous_comments(
            github_handler.get_pull_request(repo_name, pr_number)
        )

        overall_feedback = []
        pr = github_handler.get_pull_request(repo_name, pr_number)

        for file in pr.get_files():
            file_path = file.filename
            if not file.patch:
                print(f"Ignorando {file_path} (sem alterações no PR).")
                continue

            file_content = requests.get(file.raw_url).text
            feedback = analyze_file_with_claude(file_path, file_content, prompt)

            if "Erro ao processar o arquivo" in feedback:
                overall_feedback.append(
                    f"**Erro ao analisar o arquivo `{file_path}`:**\n\n{feedback}\n\n---"
                )
            else:
                overall_feedback.append(
                    f"### Arquivo: `{file_path}`\n\n{feedback}\n\n---"
                )

        github_handler.post_feedback_comment(repo_name, pr_number, overall_feedback)

    except Exception as e:
        print(f"Erro ao revisar o PR com Claude: {e}")
        github_handler.post_error_comment(repo_name, pr_number, str(e))
