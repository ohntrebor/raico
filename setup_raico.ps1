Write-Host "Iniciando a configuração do projeto RAICO..."

# 1. Verificar se o Python 3.8+ está instalado
Write-Host "🔍 Verificando a versão do Python instalada..."
$python = Get-Command python -ErrorAction SilentlyContinue

if ($python) {
    # Obtém a versão do Python como string
    $pythonVersion = &python --version 2>&1

    # Verifica se a saída contém a palavra "Python" e extrai os números da versão
    if ($pythonVersion -like "Python*") {
        $versionString = $pythonVersion -replace "Python ", "" # Remove o prefixo "Python "
        $versionParts = $versionString.Split(".") # Divide a versão em partes

        $major = [int]$versionParts[0]
        $minor = [int]$versionParts[1]

        # Verifica se a versão é menor que 3.8
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
            Write-Host "❌ Python $pythonVersion encontrado. É necessário Python 3.8 ou superior para continuar."
            Write-Host "Por favor, atualize o Python: https://www.python.org/downloads/"
            exit 1
        } else {
            Write-Host "✅ Python $pythonVersion encontrado. A versão é compatível com o projeto RAICO."
        }
    } else {
        Write-Host "❌ Não foi possível determinar a versão do Python instalada. Certifique-se de que o Python está configurado corretamente."
        exit 1
    }
} else {
    Write-Host "❌ Python não encontrado no sistema."
    Write-Host "Por favor, instale o Python 3.8 ou superior para continuar: https://www.python.org/downloads/"
    exit 1
}

# 2. Criar ambiente virtual
Write-Host "🔨 Criando ambiente virtual..."
if (Test-Path -Path "venv") {
    Write-Host "⚠️ Ambiente virtual já existe. Pulando a criação."
} else {
    &python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Falha ao criar o ambiente virtual."
        exit 1
    }
}

# 3. Ativar ambiente virtual
Write-Host "🔧 Ativando o ambiente virtual..."
$activatePath = Join-Path -Path "venv" -ChildPath "Scripts/Activate.ps1"
if (Test-Path -Path $activatePath) {
    & $activatePath
} else {
    Write-Host "❌ Não foi possível ativar o ambiente virtual."
    Write-Host "Ative manualmente: venv\Scripts\Activate.ps1"
    exit 1
}

# 4. Atualizar pip
Write-Host "⬆️ Atualizando o pip..."
pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Falha ao atualizar o pip."
    exit 1
}

# 5. Instalar dependências
Write-Host "📦 Instalando dependências do projeto..."
pip install -r scripts/requirements.txt
pip install pytest
pip install python-dotenv
pip install --upgrade PyGithub
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Falha ao instalar dependências."
    exit 1
}

# 6. Configurar o arquivo .env
Write-Host "📄 Verificando arquivo .env..."
if (-not (Test-Path ".env")) {
    @"
AI_PROVIDER="gemini"
AI_API_KEY="sua_chave_api_gemini"
AI_MODEL="gemini-1.5-flash-latest"
AI_VERSION="v1beta"
GITHUB_REPOSITORY="github.com/seu-usuario/seu-repo"
GITHUB_TOKEN="seu_token_github"
PR_NUMBER="7"
PROMPT_PATH="scripts/prompts/default_prompt.txt"
"@ > .env
    Write-Host "✅ Arquivo .env criado."
} else {
    Write-Host "⚠️ Arquivo .env já existe. Pulando a criação."
}

# 7. Verificar arquivo de prompt
Write-Host "📄 Verificando arquivo de prompt..."
if (-not (Test-Path "scripts/prompts/default_prompt.txt")) {
    New-Item -ItemType Directory -Path "scripts/prompts" -Force | Out-Null
    "Este é um prompt genérico para revisão de Pull Requests." > "scripts/prompts/default_prompt.txt"
    Write-Host "✅ Arquivo de prompt criado."
} else {
    Write-Host "⚠️ Arquivo de prompt já existe."
}

Write-Host "✅ Configuração concluída com sucesso! O projeto RAICO está pronto para uso local. Não se esqueça de atualizar o .env, se necessário."
