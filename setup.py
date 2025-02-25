from setuptools import setup, find_packages

# Configurações para empacotamento do projeto usando setuptools.
setup(
    # Nome do pacote/projeto.
    name="raico",

    # Versão do pacote. Siga o padrão de versionamento semântico: MAJOR.MINOR.PATCH.
    version="0.1.1",

    # Define os pacotes a serem incluídos. `find_packages()` detecta automaticamente os pacotes no diretório.
    packages=find_packages(),

    # Lista de dependências que serão instaladas automaticamente junto com este pacote.
    install_requires=[
        "requests",   # Biblioteca para fazer requisições HTTP.
        "openai",     # Biblioteca para integração com a API OpenAI.
        "PyGithub",   # Biblioteca para interagir com a API do GitHub.
        "anthropic"   # Biblioteca oficial da API Claude AI (Anthropic).
    ],

    # Especifica a versão mínima do Python necessária para rodar este pacote.
    #python_requires=">=3.8",

    # Descrição breve do pacote, usada em ferramentas como o PyPI.
    description="AI-powered code review tool",  # "Ferramenta de revisão de código impulsionada por IA".

    # Autor
    author="ohntrebor",

    # Licença do pacote
    license="MIT",
)
