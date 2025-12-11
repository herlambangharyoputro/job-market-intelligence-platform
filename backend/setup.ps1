# Setup Script untuk Job Listings NLP Backend
# Run: powershell -ExecutionPolicy Bypass -File setup.ps1

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Job Listings NLP - Quick Start Setup" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python Version..." -ForegroundColor Green
try {
    $pythonVersion = python --version 2>&1
    Write-Host $pythonVersion
    Write-Host "OK Python is installed" -ForegroundColor Green
} catch {
    Write-Host "ERROR Python not found" -ForegroundColor Red
    exit 1
}

# Create directory structure
Write-Host ""
Write-Host "Creating Directory Structure..." -ForegroundColor Green

$directories = @(
    "app",
    "app\api",
    "app\api\v1",
    "app\api\v1\endpoints",
    "app\models",
    "app\schemas",
    "app\services",
    "app\services\preprocessing",
    "app\services\nlp",
    "app\services\analytics",
    "app\database",
    "app\core",
    "app\utils",
    "tests",
    "data\raw",
    "data\processed",
    "data\models",
    "notebooks"
)

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "OK Created: $dir\" -ForegroundColor Green
    } else {
        Write-Host "SKIP Already exists: $dir\" -ForegroundColor Yellow
    }
}

# Create __init__.py files
Write-Host ""
Write-Host "Creating __init__.py files..." -ForegroundColor Green
$initFiles = @(
    "app\__init__.py",
    "app\api\__init__.py",
    "app\api\v1\__init__.py",
    "app\api\v1\endpoints\__init__.py",
    "app\models\__init__.py",
    "app\schemas\__init__.py",
    "app\services\__init__.py",
    "app\services\preprocessing\__init__.py",
    "app\services\nlp\__init__.py",
    "app\services\analytics\__init__.py",
    "app\database\__init__.py",
    "app\core\__init__.py",
    "app\utils\__init__.py",
    "tests\__init__.py"
)

foreach ($file in $initFiles) {
    if (!(Test-Path $file)) {
        New-Item -ItemType File -Path $file -Force | Out-Null
    }
}
Write-Host "OK Created all __init__.py files" -ForegroundColor Green

# Create .env file
Write-Host ""
Write-Host "Creating .env file..." -ForegroundColor Green
$envContent = @"
# Application Settings
APP_NAME="Job Listings NLP API"
APP_VERSION="1.0.0"
DEBUG=True

# Database Configuration
DATABASE_URL=postgresql://job_admin:strongpassword123@localhost:5432/job_listings_nlp

# Alternative format
DB_USER=job_admin
DB_PASSWORD=strongpassword123
DB_HOST=localhost
DB_PORT=5432
DB_NAME=job_listings_nlp

# API Settings
API_V1_PREFIX=/api/v1
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]

# Security
SECRET_KEY=your-secret-key-here-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# NLP Settings
MAX_TEXT_LENGTH=10000
DEFAULT_LANGUAGE=id
ENABLE_SENTIMENT_ANALYSIS=True
ENABLE_SKILL_EXTRACTION=True

# Pagination
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
"@

$envContent | Out-File -FilePath ".env" -Encoding UTF8
Write-Host "OK Created .env file" -ForegroundColor Green

# Create .gitignore
Write-Host ""
Write-Host "Creating .gitignore..." -ForegroundColor Green
$gitignoreContent = @"
# Python
__pycache__/
*.py[cod]
*.so
.Python
env/
venv/
ENV/
build/
dist/
*.egg-info/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/

# Database
*.db
*.sqlite

# Data
data/raw/*
data/processed/*
data/models/*
"@

$gitignoreContent | Out-File -FilePath ".gitignore" -Encoding UTF8
Write-Host "OK Created .gitignore" -ForegroundColor Green

# Create requirements.txt
Write-Host ""
Write-Host "Creating requirements.txt..." -ForegroundColor Green
$requirementsContent = @"
# FastAPI
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0

# Database
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
alembic==1.13.1

# NLP
nltk==3.8.1
spacy==3.7.2
scikit-learn==1.4.0

# Data
pandas==2.2.0
numpy==1.26.3

# Utilities
python-dotenv==1.0.0
python-multipart==0.0.6

# Testing
pytest==7.4.4
httpx==0.26.0
"@

$requirementsContent | Out-File -FilePath "requirements.txt" -Encoding UTF8
Write-Host "OK Created requirements.txt" -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "OK Setup Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Create virtual environment:"
Write-Host "   python -m venv venv" -ForegroundColor Cyan

Write-Host ""
Write-Host "2. Activate virtual environment:"
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan

Write-Host ""
Write-Host "3. Install dependencies:"
Write-Host "   pip install -r requirements.txt" -ForegroundColor Cyan

Write-Host ""
Write-Host "4. Update .env with your database credentials"

Write-Host ""
Write-Host "5. Create database in PostgreSQL:"
Write-Host "   psql -U postgres" -ForegroundColor Cyan
Write-Host "   CREATE DATABASE job_listings_nlp;" -ForegroundColor Cyan
Write-Host "   exit" -ForegroundColor Cyan

Write-Host ""
Write-Host "6. Run the application:"
Write-Host "   uvicorn app.main:app --reload" -ForegroundColor Cyan

Write-Host ""
Write-Host "Happy coding!" -ForegroundColor Green
Write-Host ""
