"""
Script untuk test import dependencies
Run: python test_imports.py
"""

print("=" * 60)
print("Testing Package Imports")
print("=" * 60)
print()

# Core packages
packages = {
    "Core": [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        ("pydantic_settings", "Pydantic Settings"),
    ],
    "Database": [
        ("sqlalchemy", "SQLAlchemy"),
        ("pymysql", "PyMySQL"),
        ("cryptography", "Cryptography"),
        ("alembic", "Alembic"),
    ],
    "Data": [
        ("pandas", "Pandas"),
        ("numpy", "NumPy"),
    ],
    "Utils": [
        ("dotenv", "Python Dotenv"),
    ],
    "Testing": [
        ("pytest", "Pytest"),
        ("httpx", "HTTPX"),
    ],
    "NLP (Optional)": [
        ("sklearn", "Scikit-learn"),
        ("nltk", "NLTK"),
        ("spacy", "Spacy"),
        ("textblob", "TextBlob"),
    ],
}

results = {"success": [], "failed": []}

for category, items in packages.items():
    print(f"\n{category}:")
    print("-" * 40)
    for module, name in items:
        try:
            __import__(module)
            print(f"  ✓ {name}")
            results["success"].append(name)
        except ImportError:
            status = "(optional)" if category == "NLP (Optional)" else "(REQUIRED)"
            print(f"  ✗ {name} {status}")
            results["failed"].append(name)

print()
print("=" * 60)
print("Summary")
print("=" * 60)
print(f"✓ Installed: {len(results['success'])}")
print(f"✗ Missing: {len(results['failed'])}")
print()

# Check core requirements
core_modules = ["fastapi", "sqlalchemy", "pymysql", "pydantic"]
core_installed = all(module in [pkg[0] for pkg in packages["Core"] + packages["Database"]] 
                     for module in core_modules)

if core_installed:
    print("✅ Core dependencies OK! You can start the server.")
    print()
    print("Next steps:")
    print("  1. python test_connection.py")
    print("  2. uvicorn app.main:app --reload")
else:
    print("❌ Missing core dependencies!")
    print()
    print("Install with:")
    print("  pip install fastapi uvicorn sqlalchemy pymysql pydantic pydantic-settings")

print()
print("=" * 60)
