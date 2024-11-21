import requests
from github import Github

# Função principal para revisar um Pull Request (PR) utilizando a API Gemini e GitHub.
def review_pr_gemini(ai_api_key, github_token, repo_name, pr_number, prompt_path, ai_model, ai_version):
    
    # Função auxiliar para carregar o prompt a partir de um arquivo.
    # O prompt é utilizado para orientar a análise dos arquivos pela IA.
    def load_prompt():
        try:
            # Abre e lê o conteúdo do arquivo de prompt especificado pelo caminho.
            with open(prompt_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            # Levanta um erro se o arquivo de prompt não for encontrado.
            raise FileNotFoundError(f"Prompt file não encontrado em: {prompt_path}")

    # Função para enviar o conteúdo de um arquivo para análise pela API Gemini.
    def analyze_file_with_gemini(file_path, file_content, prompt):
        # Define a URL da API Gemini com os parâmetros fornecidos.
        url = f"https://generativelanguage.googleapis.com/{ai_version}/models/{ai_model}:generateContent?key={ai_api_key}"
        headers = {"Content-Type": "application/json"}
        
        # Cria o payload para a requisição, combinando o prompt e o conteúdo do arquivo.
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
            # Envia a requisição POST para a API Gemini.
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()  # Lança exceção se houver erro na resposta.

            # Extrai o texto gerado pela IA a partir da resposta.
            data = response.json()
            generated_text = (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "Nenhuma análise fornecida.")
            )
            return generated_text.strip()  # Retorna o texto gerado pela IA.
        except requests.RequestException as e:
            # Retorna uma mensagem de erro se houver problema na requisição.
            return f"Erro ao processar o arquivo {file_path} com o Gemini: {e}"

    try:
        # Carrega o prompt utilizando a função auxiliar.
        prompt = load_prompt()

        # Autentica no GitHub usando o token fornecido.
        g = Github(github_token)
        repo = g.get_repo(repo_name)  # Obtém o repositório pelo nome fornecido.
        pr = repo.get_pull(int(pr_number))  # Obtém o Pull Request específico.

        # Deleta comentários anteriores feitos pelo bot no PR.
        comments = pr.get_issue_comments()  # Obtém todos os comentários do PR.
        bot_username = "github-actions[bot]"  # Nome padrão do bot utilizado pelo GitHub Actions.
        headers = {"Authorization": f"Bearer {github_token}"}  # Cabeçalhos para autenticação na API.

        for comment in comments:
            # Filtra apenas os comentários feitos pelo bot.
            if comment.user.login == bot_username:
                try:
                    # Deleta o comentário através da API REST do GitHub.
                    url = f"https://api.github.com/repos/{repo_name}/issues/comments/{comment.id}"
                    response = requests.delete(url, headers=headers)
                    if response.status_code == 204:
                        print(f"Comentário deletado: {comment.id}")
                    else:
                        print(f"Erro ao deletar comentário {comment.id}: {response.text}")
                except Exception as e:
                    print(f"Erro ao deletar comentário {comment.id}: {e}")

        # Adiciona o cabeçalho criativo ao comentário
        ascii_art = """
```diff
     .---.     
    } n n {    
     \_-_/     
.'c ."|_|". n`.
'--'  /_\  `--'
     /| |\     
    [_] [_]     

**Olá, sou a agente RAICO!**  
Realizei uma análise detalhada do seu Pull Request com base no prompt fornecido.  
Seguem minhas sugestões e observações para ajudar a aprimorar seu código.  
```

<hr>
<br>
"""

        overall_feedback = [ascii_art]

        # Itera sobre os arquivos modificados no PR.
        for file in pr.get_files():
            file_path = file.filename  # Caminho do arquivo no repositório.
            if not file.patch:
                # Ignora arquivos que não possuem alterações no PR.
                print(f"Ignorando {file_path} (sem alterações no PR).")
                continue

            # Obtém o conteúdo bruto do arquivo utilizando sua URL.
            file_content = requests.get(file.raw_url).text
            # Analisa o arquivo utilizando a função auxiliar e armazena o feedback.
            feedback = analyze_file_with_gemini(file_path, file_content, prompt)

            if "Erro ao processar o arquivo" in feedback:
                # Adiciona mensagens de erro ao feedback consolidado.
                overall_feedback.append(
                    f"**Erro ao analisar o arquivo `{file_path}`:**\n\n{feedback}\n\n---"
                )
            else:
                # Adiciona feedback gerado pela IA ao feedback consolidado.
                overall_feedback.append(
                    f"### Arquivo: `{file_path}`\n\n{feedback}\n\n---"
                )

        # Cria o comentário final com todo o feedback consolidado.
        summary = "\n\n".join(overall_feedback)
        pr.create_issue_comment(summary)  # Adiciona o comentário ao PR.
        print("Comentário do resumo do PR criado com sucesso!")  # Confirmação de sucesso.

    except Exception as e:
        # Captura erros gerais e cria um comentário de erro no PR.
        print(f"Erro ao revisar o PR com Gemini: {e}")
        pr.create_issue_comment(f"**Erro no review automatizado pelo RAICO 🤖:**\n\n{str(e)}")

