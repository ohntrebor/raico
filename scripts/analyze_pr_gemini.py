import requests
from github import Github

def review_pr_gemini(ai_api_key, github_token, repo_name, pr_number, prompt_path, ai_model, ai_version):
    def load_prompt():
        try:
            with open(prompt_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file não encontrado em: {prompt_path}")

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
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(int(pr_number))

        # Ocultar comentários anteriores usando a API REST
        comments = pr.get_issue_comments()
        bot_username = "github-actions[bot]"  # Ajuste se necessário
        headers = {"Authorization": f"Bearer {github_token}"}

        for comment in comments:
            if comment.user.login == bot_username:
                try:
                    # Ocultar comentário via API REST
                    url = f"https://api.github.com/repos/{repo_name}/issues/comments/{comment.id}/reactions"
                    payload = {"content": "hooray"}  # Reação padrão ao esconder
                    response = requests.delete(url, headers=headers)
                    if response.status_code == 204:
                        print(f"Comentário ocultado: {comment.id}")
                    else:
                        print(f"Erro ao ocultar comentário {comment.id}: {response.text}")
                except Exception as e:
                    print(f"Erro ao ocultar comentário {comment.id}: {e}")

        # Análise do PR
        overall_feedback = []
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
        pr.create_issue_comment(f"**Erro na análise automatizada pelo RAICO 🤖:**\n\n{str(e)}")
