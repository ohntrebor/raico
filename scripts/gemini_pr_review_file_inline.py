from scripts.github_handler.commented_pr import GithubPRHandler
import requests

# Função principal para revisar um arquivo inteiro alterado no Pull Request (PR).
def gemini_pr_review_file_inline(ai_api_key, github_token, repo_name, pr_number, prompt_path, ai_model, ai_version):
    """
    Função para revisar um arquivo inteiro alterado em um Pull Request (PR) utilizando a API Gemini,
    adicionando comentários diretamente na diff com contexto completo.

    Args:
        ai_api_key (str): Chave de autenticação da API Gemini.
        github_token (str): Token de autenticação do GitHub.
        repo_name (str): Nome do repositório no formato "owner/repo".
        pr_number (int): Número do Pull Request.
        prompt_path (str): Caminho para o arquivo de prompt personalizado.
        ai_model (str): Modelo da API Gemini.
        ai_version (str): Versão da API Gemini.
    """

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

    def analyze_file_with_gemini(file_path, file_content, patch_content, prompt):
        """
        Analisa o arquivo inteiro alterado e faz múltiplas análises para cada mudança.

        Args:
            file_path (str): Caminho do arquivo.
            file_content (str): Conteúdo completo do arquivo.
            patch_content (str): Apenas as alterações feitas no arquivo.
            prompt (str): Texto do prompt.

        Returns:
            list: Lista de sugestões organizadas por linha modificada.
        """
        url = f"https://generativelanguage.googleapis.com/{ai_version}/models/{ai_model}:generateContent?key={ai_api_key}"
        headers = {"Content-Type": "application/json"}

        # Criar o payload com o código completo e o patch do arquivo
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"""
                            {prompt}
                            Arquivo: {file_path}

                            **Conteúdo completo do arquivo atualizado:**
                            ```python
                            {file_content}
                            ```

                            **Alterações aplicadas:**
                            ```diff
                            {patch_content}
                            ```
                            """
                        }
                    ]
                }
            ]
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            data = response.json()
            generated_text = (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "Nenhuma análise fornecida.")
            )

            # Dividir sugestões para cada alteração (separação fictícia por linhas)
            suggestions = generated_text.strip().split("\n\n")  # Divide sugestões baseadas em parágrafos
            return suggestions
        except requests.RequestException as e:
            return [f"Erro ao processar o arquivo {file_path} com o Gemini: {e}"]

    try:
        prompt = load_prompt()
        github_handler = GithubPRHandler(github_token)

        # Obtém o PR e exclui comentários anteriores
        pr = github_handler.get_pull_request(repo_name, pr_number)
        github_handler.delete_previous_comments(pr)

        # Itera sobre os arquivos do PR e analisa todas as mudanças
        for file in pr.get_files():
            file_path = file.filename
            file_url = file.raw_url  # URL do arquivo atualizado
            patch_content = file.patch  # Obtém apenas as alterações (diff)

            print(f"🔍 Analisando arquivo: {file_path}")

            # Obtém o conteúdo completo do arquivo
            file_content = fetch_file_content(file_url)

            # Analisa o arquivo inteiro e gera sugestões para cada modificação
            suggestions = analyze_file_with_gemini(file_path, file_content, patch_content, prompt)

            # Identificar as linhas alteradas no patch
            modified_lines = []
            line_position = 0
            for line in patch_content.split("\n"):
                if line.startswith("@@"):
                    # Extrai a posição real da linha a partir do diff
                    try:
                        line_position = int(line.split(" ")[1].split(",")[0].replace("-", ""))
                    except ValueError:
                        continue
                elif line.startswith("+") and not line.startswith("+++"):
                    modified_lines.append(line_position)
                    line_position += 1

            # Iterar sobre cada linha alterada e adicionar um comentário inline corretamente
            last_position = None
            grouped_suggestions = []
            
            for i, suggestion in enumerate(suggestions):
                if "✅ Alterações Aprovadas" in suggestion:
                    print(f"✔️ Nenhum comentário necessário para `{file_path}` (Alteração aprovada)")
                    continue

                if i < len(modified_lines):
                    line_number = modified_lines[i]
                else:
                    line_number = modified_lines[-1] if modified_lines else 1

                # Agrupar comentários próximos em um único bloco
                if last_position is not None and abs(line_number - last_position) <= 2:
                    grouped_suggestions.append(suggestion)
                else:
                    if grouped_suggestions:
                        comment_text = "\n\n".join(grouped_suggestions)
                        github_handler.post_inline_comment(repo_name, pr_number, file_path, last_position, comment_text)
                    grouped_suggestions = [suggestion]

                last_position = line_number

            # Postar o último grupo de comentários
            if grouped_suggestions:
                comment_text = "\n\n".join(grouped_suggestions)
                github_handler.post_inline_comment(repo_name, pr_number, file_path, last_position, comment_text)

            print(f"✅ Revisão concluída para `{file_path}`\n")

    except Exception as e:
        print(f"Erro ao revisar o PR com Gemini: {e}")
        github_handler.post_error_comment(repo_name, pr_number, str(e))
