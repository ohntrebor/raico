from scripts.github_handler.commented_pr import GithubPRHandler
import openai

def openai_pr_review_line_inline(ai_api_key, github_token, repo_name, pr_number, prompt_path, ai_model):
    """
    Função principal para revisar as linhas alteradas de um Pull Request (PR) utilizando a API OpenAI,
    adicionando comentários diretamente na diff.

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
        """Carrega o texto do prompt a partir de um arquivo."""
        try:
            with open(prompt_path, 'r', encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file não encontrado em: {prompt_path}")

    def analyze_patch_with_openai(file_path, patch_line, prompt):
        """
        Analisa uma única linha alterada com base no modelo OpenAI e no prompt.

        Args:
            file_path (str): Caminho do arquivo.
            patch_line (str): Linha alterada no código.
            prompt (str): Texto do prompt.

        Returns:
            str: Resposta do modelo OpenAI.
        """
        full_prompt = f"""
        {prompt}
        Arquivo: {file_path}
        Linha alterada:
        ```diff
        {patch_line}
        ```
        """

        try:
            response = openai.ChatCompletion.create(
                model=ai_model,
                messages=[{"role": "user", "content": full_prompt}],
            )
            return response['choices'][0]['message']['content']
        except openai.error.OpenAIError as e:
            return f"Erro ao processar a linha `{patch_line}` no arquivo `{file_path}`: {e}"

    try:
        # Carrega o prompt do arquivo especificado
        prompt = load_prompt()

        # Inicializa o manipulador de PRs do GitHub
        github_handler = GithubPRHandler(github_token)

        # Obtém o PR e exclui comentários anteriores
        pr = github_handler.get_pull_request(repo_name, pr_number)
        github_handler.delete_previous_comments(pr)

        # Itera sobre os arquivos do PR e analisa as linhas alteradas
        for file in pr.get_files():
            file_path = file.filename
            patch_content = file.patch  # Apenas as alterações no arquivo

            if not patch_content:
                print(f"Ignorando {file_path} (sem alterações no PR).")
                continue

            patch_lines = patch_content.split("\n")
            position = 1  # Posição da linha no diff

            for line in patch_lines:
                if line.startswith("+") and not line.startswith("+++"):  # Apenas linhas adicionadas
                    feedback = analyze_patch_with_openai(file_path, line, prompt)

                    if "Erro ao processar" in feedback:
                        print(f"Erro ao analisar `{file_path}` na linha `{line}`: {feedback}")
                    else:
                        comment_text = f"**Sugestão para `{file_path}`:**\n\n{feedback}"
                        github_handler.post_inline_comment(repo_name, pr_number, file_path, position, comment_text)

                position += 1  # Atualiza a posição da linha

    except Exception as e:
        print(f"Erro ao revisar o PR com OpenAI: {e}")
        github_handler.post_error_comment(repo_name, pr_number, str(e))
