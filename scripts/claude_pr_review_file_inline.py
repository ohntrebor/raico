from scripts.github_handler.commented_pr import GithubPRHandler
import anthropic
import requests

def claude_pr_review_file_inline(ai_api_key, github_token, repo_name, pr_number, prompt_path, ai_model="claude-2"):
    """
    Função para revisar um arquivo inteiro alterado em um Pull Request (PR) utilizando a API Claude AI,
    adicionando comentários diretamente na diff com contexto completo.

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
        """Carrega o texto do prompt a partir de um arquivo."""
        try:
            with open(prompt_path, 'r', encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file não encontrado em: {prompt_path}")

    def fetch_file_content(file_url):
        """
        Obtém o conteúdo completo do arquivo para fornecer mais contexto.

        Args:
            file_url (str): URL do arquivo no GitHub.

        Returns:
            str: Conteúdo do arquivo como texto.
        """
        try:
            response = requests.get(file_url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            return f"Erro ao obter o conteúdo do arquivo: {e}"

    def analyze_file_with_claude(file_path, file_content, prompt):
        """
        Analisa o arquivo inteiro alterado.

        Args:
            file_path (str): Caminho do arquivo.
            file_content (str): Conteúdo completo do arquivo.
            prompt (str): Texto do prompt.

        Returns:
            str: Resposta do modelo Claude.
        """
        full_prompt = f"""
        {prompt}
        Arquivo: {file_path}

        **Conteúdo completo do arquivo atualizado:**
        ```python
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

        # Obtém o PR e exclui comentários anteriores
        pr = github_handler.get_pull_request(repo_name, pr_number)
        github_handler.delete_previous_comments(pr)

        # Itera sobre os arquivos do PR e analisa o arquivo completo
        for file in pr.get_files():
            file_path = file.filename
            file_url = file.raw_url  # URL do arquivo atualizado

            print(f"🔍 Analisando arquivo: {file_path}")

            # Obtém o conteúdo completo do arquivo
            file_content = fetch_file_content(file_url)

            # Analisa o arquivo inteiro no contexto do prompt
            feedback = analyze_file_with_claude(file_path, file_content, prompt)

            if "Erro ao processar" in feedback:
                print(f"❌ Erro ao analisar `{file_path}`: {feedback}")
            else:
                comment_text = f"""
                ### Sugestão para `{file_path}`
                {feedback}
                """

                # Posta o comentário na primeira linha do arquivo modificado
                github_handler.post_inline_comment(repo_name, pr_number, file_path, 1, comment_text)

            print(f"✅ Revisão concluída para `{file_path}`\n")

    except Exception as e:
        print(f"Erro ao revisar o PR com Claude: {e}")
        github_handler.post_error_comment(repo_name, pr_number, str(e))
