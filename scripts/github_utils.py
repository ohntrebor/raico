import requests
from github import Github

def post_comment_on_pr(github_token, repo_name, pr_number, commit_id, file_path, feedback, position=1):
    """
    Função para comentar em um arquivo dentro de um PR no GitHub.
    """
    try:
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(int(pr_number))

        pr.create_review_comment(
            body=feedback,
            path=file_path,
            position=position,
            commit_id=commit_id
        )
        print(f"Comentário adicionado no arquivo: {file_path}")
    except Exception as e:
        print(f"Erro ao comentar no arquivo {file_path}: {e}")
        raise e

def post_error_comment(github_token, repo_name, pr_number, error_message):
    """
    Função para adicionar um comentário geral no PR em caso de erro.
    """
    try:
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(int(pr_number))

        pr.create_issue_comment(
            f"**Erro na análise automatizada pela RAICO:**\n\n{str(error_message)}"
        )
        print(f"Comentário de erro adicionado no PR #{pr_number}")
    except Exception as e:
        print(f"Falha ao postar o erro no PR: {e}")
