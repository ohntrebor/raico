import openai
from github import Github
import requests

def openai_pr_review_line(ai_api_key, github_token, repo_name, pr_number, ai_model="gpt-4"):
    """
    Revisar Pull Requests no GitHub analisando apenas os diffs das alterações (Line Diff Review).

    Args:
        ai_api_key (str): Chave da API OpenAI.
        github_token (str): Token da API do GitHub.
        repo_name (str): Nome do repositório no formato "owner/repo".
        pr_number (int): Número do Pull Request.
        ai_model (str): Modelo OpenAI a ser utilizado (default: gpt-4).
    """
    openai.api_key = ai_api_key
    github_client = Github(github_token)
    repo = github_client.get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    def get_diff_from_pr(pr):
        """
        Obtém o diff de todos os arquivos alterados no PR.
        """
        diff_url = pr.diff_url
        response = requests.get(diff_url, headers={"Authorization": f"Bearer {github_token}"})
        if response.status_code != 200:
            raise Exception(f"Falha ao obter o diff: {response.status_code} - {response.text}")
        return response.text

    def analyze_diff_with_openai(file_name, diff_content):
        """
        Envia o conteúdo do diff para o modelo OpenAI e obtém comentários.

        Args:
            file_name (str): Nome do arquivo.
            diff_content (str): Conteúdo do diff.

        Returns:
            list: Lista de comentários gerados pelo modelo.
        """
        prompt = f"""
        Você é um assistente especializado em revisão de código.
        Analise as alterações no arquivo "{file_name}" e identifique problemas ou melhorias no código.
        Dê feedback construtivo e claro.

        Aqui está o diff do código:
        ```diff
        {diff_content}
        ```
        Retorne sua análise em formato JSON, com o seguinte formato:
        {{
            "comments": [
                {{
                    "line": <número_da_linha_no_diff>,
                    "comment": "<seu_comentário_aqui>"
                }}
            ]
        }}
        """
        response = openai.ChatCompletion.create(
            model=ai_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.2,
        )
        try:
            ai_feedback = response["choices"][0]["message"]["content"]
            return eval(ai_feedback)["comments"]
        except Exception as e:
            return [{"line": None, "comment": f"Erro ao processar o arquivo: {str(e)}"}]

    def post_review_comments(pr, comments):
        """
        Publica comentários diretamente no PR.
        """
        for comment in comments:
            if comment["line"] is not None:
                pr.create_review_comment(
                    body=comment["comment"],
                    commit_id=pr.head.sha,
                    path=comment["file"],
                    position=comment["line"],
                )

    try:
        diff_content = get_diff_from_pr(pr)
        diff_lines = diff_content.split("\n")

        # Processa os diffs por arquivo
        feedback = []
        for file in pr.get_files():
            file_name = file.filename
            file_diff = "\n".join([line for line in diff_lines if file_name in line])
            if not file_diff.strip():
                continue

            # Analisa as alterações no arquivo
            comments = analyze_diff_with_openai(file_name, file_diff)
            for comment in comments:
                comment["file"] = file_name
            feedback.extend(comments)

        # Posta os comentários diretamente no PR
        post_review_comments(pr, feedback)

        print("Revisão do PR finalizada com sucesso!")
    except Exception as e:
        print(f"Erro ao revisar o PR: {e}")
