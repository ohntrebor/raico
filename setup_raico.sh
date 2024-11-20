#!/bin/bash

# Função para verificar se um comando está instalado
command_exists() {
    command -v "$1" &> /dev/null
}

echo "Iniciando a configuração do projeto RAICO..."

# 1. Verificar se o Python 3.8+ está instalado
if command_exists python3; then
    # Captura a versão do Python e verifica se é 3.8 ou superior
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    echo "Python encontrado: Versão $PYTHON_VERSION"

    # Extrai os valores principais da versão (exemplo: 3.9.7 -> 3 9)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    # Verifica se a versão é 3.8 ou superior
    if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]; }; then
        echo "Versão do Python incompatível. É necessário Python 3.8 ou superior."
        echo "Atualize o Python: https://www.python.org/downloads/"
        exit 1
    fi
else
    # Python não encontrado
    echo "Python 3 não encontrado."
    echo "Instale o Python 3.8 ou superior para continuar."
    echo "Linux: sudo apt install python3 python3-venv python3-pip"
    echo "Windows: Baixe e instale de https://www.python.org/downloads/"
    exit 1
fi

# 2. Criar ambiente virtual
echo "Criando o ambiente virtual..."
if [ -d "venv" ]; then
    echo "Ambiente virtual já existe. Pulando a criação."
else
    python3 -m venv venv || { echo "Falha ao criar o ambiente virtual"; exit 1; }
fi

# 3. Ativar o ambiente virtual
echo "Ativando o ambiente virtual..."
if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
    # Ativação para Linux/macOS
    source venv/bin/activate
elif [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "win32"* ]]; then
    # Ativação para Windows
    venv\\Scripts\\activate
else
    echo "Sistema operacional não suportado automaticamente. Ative o ambiente virtual manualmente."
    exit 1
fi

# 4. Atualizar o pip
echo "Atualizando o pip para a última versão..."
pip install --upgrade pip || { echo "Falha ao atualizar o pip"; exit 1; }

# 5. Instalar dependências do projeto
echo "Instalando as dependências do projeto..."
pip install -r scripts/requirements.txt || { echo "Falha ao instalar dependências"; exit 1; }
pip install pytest
pip install python-dotenv
pip install --upgrade PyGithub

# 6. Configurar o arquivo .env
echo "Verificando o arquivo .env..."
if [ ! -f ".env" ]; then
    # Cria o arquivo .env se não existir
    cat <<EOT > .env
AI_PROVIDER="gemini"
AI_API_KEY="sua_chave_api_gemini"
AI_MODEL="gemini-1.5-flash-latest"
AI_VERSION="v1beta"
GITHUB_REPOSITORY="github.com/seu-usuario/seu-repo"
GITHUB_TOKEN="seu_token_github"
PR_NUMBER="7"
PROMPT_PATH="scripts/prompts/default_prompt.txt"
EOT
    echo "Arquivo .env criado."
else
    echo "Arquivo .env já existe. Pulando a criação."
fi

# 7. Verificar a existência do arquivo de prompt
echo "Verificando o arquivo de prompt..."
if [ ! -f "scripts/prompts/default_prompt.txt" ]; then
    # Cria o arquivo de prompt se não existir
    mkdir -p scripts/prompts
    echo "Este é um prompt genérico para revisão de Pull Requests." > scripts/prompts/default_prompt.txt
    echo "Arquivo de prompt criado."
else
    echo "Arquivo de prompt já existe."
fi


echo "✅ Configuração concluída com sucesso! O projeto RAICO está pronto para uso local, não se esqueça de atualizar o .env"
