from setuptools import setup, find_packages

# Configurações para empacotamento do projeto usando setuptools.
setup(
    # Nome do pacote/projeto.
    name="raico",

    # Versão do pacote. Siga o padrão de versionamento semântico: MAJOR.MINOR.PATCH.
    version="0.1.0",

    # Define os pacotes a serem incluídos. `find_packages()` detecta automaticamente os pacotes no diretório.
    packages=find_packages(),

    # Lista de dependências que serão instaladas automaticamente junto com este pacote.
    install_requires=[
        "openai",     # Biblioteca para integração com a API OpenAI.
        "PyGithub",   # Biblioteca para interagir com a API do GitHub.
        "requests"    # Biblioteca para fazer requisições HTTP.
    ],

    # Descrição breve do pacote, usada em ferramentas como o PyPI.
    description="AI-powered code review tool",  # "Ferramenta de revisão de código impulsionada por IA".

    # Autor 
    author="ohntrebor",

    # Licença do pacote
    license="MIT",
)
