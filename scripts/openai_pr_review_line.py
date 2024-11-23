import openai
from github import Github
import json

def openai_pr_review_line(ai_api_key, github_token, repo_name, pr_number, ai_model):
    """
    Revisa linhas modificadas em um Pull Request no GitHub e comenta diretamente nas linhas alteradas.

    Args:
        ai_api_key (str): Chave da API OpenAI.
        github_token (str): Token da API do GitHub.
        repo_name (str): Nome do repositório no formato "owner/repo".
        pr_number (str/int): Número do Pull Request.
        ai_model (str): Modelo OpenAI a ser utilizado.
    """
    # Autenticação OpenAI e GitHub
    openai.api_key = ai_api_key
    github_client = Github(github_token)

    try:
        # Convertendo o PR_NUMBER para inteiro, caso necessário
        pr_number = int(pr_number)
    except ValueError:
        raise ValueError(f"PR_NUMBER '{pr_number}' deve ser um número inteiro.")

    try:
        # Obter o repositório e o PR
        repo = github_client.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        print(f"Revisando PR: {pr.title} no repositório {repo_name}")

        # Obter os diffs do PR
        files = pr.get_files()
        diffs = [{"file_name": file.filename, "patch": file.patch} for file in files if file.patch]

        if not diffs:
            print("Nenhuma alteração encontrada no PR.")
            return

        # Processar cada arquivo alterado
        for diff in diffs:
            file_name = diff["file_name"]
            patch = diff["patch"]

            # Chamada para análise com OpenAI
            comments = analyze_diff_with_openai(file_name, patch, ai_model)

            # Criar comentários diretamente no PR
            create_comments_on_pr(pr, comments, file_name)

        print("Revisão do PR finalizada com sucesso!")
    except Exception as e:
        print(f"Erro ao revisar o Pull Request: {e}")


def analyze_diff_with_openai(file_name, diff_content, ai_model):
    """
    Envia o diff para a API OpenAI e retorna os comentários.

    Args:
        file_name (str): Nome do arquivo.
        diff_content (str): Conteúdo do diff.
        ai_model (str): Modelo OpenAI a ser utilizado.

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
    try:
        response = openai.ChatCompletion.create(
            model=ai_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.2,
        )
        ai_feedback = json.loads(response["choices"][0]["message"]["content"])
        return ai_feedback["comments"]
    except Exception as e:
        print(f"Erro ao processar análise com OpenAI: {e}")
        return []


def create_comments_on_pr(pr, comments, file_name):
    """
    Cria comentários diretamente nas linhas alteradas do PR.

    Args:
        pr (PullRequest): Objeto do Pull Request.
        comments (list): Lista de comentários gerados pela análise.
        file_name (str): Nome do arquivo.
    """
    for comment in comments:
        try:
            pr.create_review_comment(
                body=comment["comment"],
                commit_id=pr.head.sha,
                path=file_name,
                position=comment["line"]
            )
            print(f"Comentário criado na linha {comment['line']}: {comment['comment']}")
        except Exception as e:
            print(f"Erro ao criar comentário na linha {comment['line']}: {e}")
