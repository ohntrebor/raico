from github import Github
import requests

def review_pr_gemini(ai_api_key, github_token, repo_name, pr_number, prompt_path, ai_model, ai_version):
    """
    Função para analisar Pull Requests usando o Gemini e ocultar comentários anteriores do bot.

    Args:
        ai_api_key (str): Chave de autenticação da API Gemini.
        github_token (str): Token de autenticação do GitHub.
        repo_name (str): Nome do repositório no formato "owner/repo".
        pr_number (int): Número do Pull Request.
        prompt_path (str): Caminho para o arquivo de prompt personalizado.
        ai_model (str): Modelo da AI.
        ai_version (str): Versão da API.
    """
    # Carregar o prompt do arquivo
    def load_prompt():
        try:
            with open(prompt_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file não encontrado em: {prompt_path}")

    # Fazer a análise de um arquivo com o Gemini
    def analyze_file_with_gemini(file_path, file_content, prompt):
        url = f"https://generativelanguage.googleapis.com/{ai_version}/models/{ai_model}:generateContent?key={ai_api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{prompt}\n\nArquivo: {file_path}\n\n{file_content}"}
                    ]
                }
            ]
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            # Extrair o texto gerado pela IA
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
        # Carrega o prompt
        prompt = load_prompt()

        # Conecta-se ao GitHub
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(int(pr_number))

        # Ocultar comentários anteriores do bot
        comments = pr.get_issue_comments()
        bot_username = "github-actions[bot]"

        for comment in comments:
            if comment.user.login == bot_username:
                try:
                    comment.hide()  # Oculta o comentário
                    print(f"Comentário ocultado: {comment.id}")
                except Exception as e:
                    print(f"Erro ao ocultar comentário {comment.id}: {e}")

        # Lista para armazenar feedback consolidado
        overall_feedback = []

        # Itera sobre os arquivos no PR
        for file in pr.get_files():
            file_path = file.filename

            if not file.patch:
                print(f"Ignorando {file_path} (sem alterações no PR).")
                continue

            file_content = requests.get(file.raw_url).text
            feedback = analyze_file_with_gemini(file_path, file_content, prompt)

            if "Erro ao processar o arquivo" in feedback:
                overall_feedback.append(
                    f"**Erro ao analisar o arquivo `{file_path}`:**\n\n{feedback}\n\n---"
                )
            else:
                overall_feedback.append(
                    f"### Arquivo: `{file_path}`\n\n{feedback}\n\n---"
                )

        # Gera e posta o feedback consolidado
        summary = (
            f"**Análise Automática do PR pelo RAICO 🤖:**\n\n" + "\n\n".join(overall_feedback)
        )
        pr.create_issue_comment(summary)
        print("Comentário do resumo do PR criado com sucesso!")
    except Exception as e:
        print(f"Erro ao revisar o PR com Gemini: {e}")
        # Postar comentário de erro no PR
        pr.create_issue_comment(f"**Erro na análise automatizada pelo RAICO 🤖:**\n\n{str(e)}")
