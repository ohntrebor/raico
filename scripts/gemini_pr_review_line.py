from scripts.github_handler.commented_pr import GithubPRHandler
import requests

# Função principal para revisar as linhas alteradas de um Pull Request (PR).
def gemini_pr_review_line(ai_api_key, github_token, repo_name, pr_number, prompt_path, ai_model, ai_version):
    """
    Função principal para revisar as linhas alteradas de um Pull Request (PR) utilizando a API Gemini e GitHub.

    Args:
        ai_api_key (str): Chave de autenticação da API Gemini.
        github_token (str): Token de autenticação do GitHub.
        repo_name (str): Nome do repositório no formato "owner/repo".
        pr_number (int): Número do Pull Request.
        prompt_path (str): Caminho para o arquivo de prompt personalizado.
        ai_model (str): Modelo da API Gemini.
        ai_version (str): Versão da API Gemini.
    """
    # Função auxiliar para carregar o prompt
    def load_prompt():
        try:
            with open(prompt_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file não encontrado em: {prompt_path}")

    # Função para enviar o patch de um arquivo para análise pela API Gemini.
    def analyze_patch_with_gemini(file_path, patch_content, prompt):
        url = f"https://generativelanguage.googleapis.com/{ai_version}/models/{ai_model}:generateContent?key={ai_api_key}"
        headers = {"Content-Type": "application/json"}
        
        # Cria o payload com o prompt e o patch do arquivo
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{prompt}\n\nArquivo: {file_path}\n\nAlterações:\n```diff\n{patch_content}\n```"}
                    ]
                }
            ]
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()  # Levanta exceção se houver erro na resposta

            data = response.json()
            generated_text = (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "Nenhuma análise fornecida.")
            )
            return generated_text.strip()
        except requests.RequestException as e:
            return f"Erro ao processar o arquivo {file_path} com o Gemini: {e}"

    try:
        prompt = load_prompt()
        github_handler = GithubPRHandler(github_token)

        # Deleta comentários anteriores
        pr = github_handler.get_pull_request(repo_name, pr_number)
        github_handler.delete_previous_comments(pr)

        overall_feedback = []

        # Itera sobre os arquivos do PR e analisa apenas os patches
        for file in pr.get_files():
            file_path = file.filename
            patch_content = file.patch  # Obtemos as alterações (diff)

            if not patch_content:
                print(f"Ignorando {file_path} (sem alterações no PR).")
                continue

            # Analisa o patch com a API Gemini
            feedback = analyze_patch_with_gemini(file_path, patch_content, prompt)

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
        print(f"Erro ao revisar o PR com Gemini: {e}")
        github_handler.post_error_comment(repo_name, pr_number, str(e))
