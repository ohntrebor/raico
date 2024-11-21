import requests
from github import Github

class GithubPRHandler:
    def __init__(self, github_token):
        """
        Classe para lidar com Pull Requests no GitHub.

        Args:
            github_token (str): Token de autenticação para a API do GitHub.
        """
        self.github_token = github_token
        self.github_client = Github(github_token)

    def get_pull_request(self, repo_name, pr_number):
        """
        Obtém o objeto do Pull Request.

        Args:
            repo_name (str): Nome do repositório no formato "owner/repo".
            pr_number (int): Número do Pull Request.

        Returns:
            PullRequest: Objeto do Pull Request.
        """
        repo = self.github_client.get_repo(repo_name)
        return repo.get_pull(int(pr_number))

    def delete_previous_comments(self, pr, bot_username="github-actions[bot]"):
        """
        Deleta os comentários anteriores feitos pelo bot no Pull Request.

        Args:
            pr (PullRequest): Objeto do Pull Request.
            bot_username (str): Nome do bot que fez os comentários (padrão: github-actions[bot]).
        """
        headers = {"Authorization": f"Bearer {self.github_token}"}
        comments = pr.get_issue_comments()
        for comment in comments:
            if comment.user.login == bot_username:
                try:
                    url = f"https://api.github.com/repos/{pr.base.repo.full_name}/issues/comments/{comment.id}"
                    response = requests.delete(url, headers=headers)
                    if response.status_code == 204:
                        print(f"Comentário deletado: {comment.id}")
                    else:
                        print(f"Erro ao deletar comentário {comment.id}: {response.text}")
                except Exception as e:
                    print(f"Erro ao deletar comentário {comment.id}: {e}")

    def post_feedback_comment(self, repo_name, pr_number, feedback_list):
        """
        Monta e publica um comentário no Pull Request com base no feedback.

        Args:
            repo_name (str): Nome do repositório no formato "owner/repo".
            pr_number (int): Número do Pull Request.
            feedback_list (list): Lista de strings contendo o feedback gerado.
        """
        # Adiciona cabeçalho ao comentário
        ascii_art = """
```python
     .---.     
    } n n {    
     \_-_/     
.'c ."|_|". n`.
'--'  /_\  `--'
     /| |\     
    [_] [_]     

**Olá, sou o agente RAICO!**  
Realizei uma análise detalhada do seu Pull Request com base no prompt fornecido.  
Seguem minhas sugestões e observações para ajudar a aprimorar seu código.  
<hr> """ # Monta o corpo do comentário com feedback consolidado feedback_body = "\n\n".join([ascii_art] + feedback_list)

    try:
        # Obtém o PR e posta o comentário
        pr = self.get_pull_request(repo_name, pr_number)
        pr.create_issue_comment(feedback_body)
        print("Comentário criado com sucesso!")
    except Exception as e:
        print(f"Erro ao criar comentário no PR: {e}")

def post_error_comment(self, repo_name, pr_number, error_message):
    """
    Publica um comentário no Pull Request indicando que ocorreu um erro.

    Args:
        repo_name (str): Nome do repositório no formato "owner/repo".
        pr_number (int): Número do Pull Request.
        error_message (str): Mensagem de erro a ser publicada.
    """
    try:
        pr = self.get_pull_request(repo_name, pr_number)
        pr.create_issue_comment(f"**Erro no review automatizado pelo RAICO 🤖:**\n\n{error_message}")
        print("Comentário de erro criado com sucesso!")
    except Exception as e:
        print(f"Erro ao criar comentário de erro no PR: {e}")
