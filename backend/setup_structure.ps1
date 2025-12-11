# Buat semua folder
$folders = @(
    "app\api\v1\endpoints",
    "app\models",
    "app\schemas",
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

foreach ($folder in $folders) {
    New-Item -ItemType Directory -Path $folder -Force | Out-Null
    Write-Host "Created: $folder" -ForegroundColor Green
}

# Buat semua file __init__.py
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
    New-Item -ItemType File -Path $file -Force | Out-Null
}
Write-Host "Created all __init__.py files" -ForegroundColor Green