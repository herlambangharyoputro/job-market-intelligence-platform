"""
Script untuk diagnosa struktur project
Run: python check_structure.py
"""

import os
import sys

print("=" * 60)
print("Project Structure Diagnostic")
print("=" * 60)
print()

# Check current directory
print(f"Current Directory: {os.getcwd()}")
print()

# Check if app folder exists
print("Checking folders...")
folders_to_check = [
    "app",
    "app/api",
    "app/api/v1",
    "app/api/v1/endpoints",
    "app/models",
    "app/schemas",
    "app/services",
    "app/database",
    "app/core",
    "app/utils",
]

for folder in folders_to_check:
    exists = "✓" if os.path.exists(folder) else "✗"
    print(f"  {exists} {folder}")

print()

# Check if important files exist
print("Checking files...")
files_to_check = [
    "app/__init__.py",
    "app/main.py",
    "app/config.py",
    "app/database/__init__.py",
    "app/database/base.py",
    "app/database/session.py",
]

for file in files_to_check:
    exists = "✓" if os.path.exists(file) else "✗"
    print(f"  {exists} {file}")

print()

# Check Python path
print("Python Path:")
for path in sys.path:
    print(f"  - {path}")

print()

# Try to import app
print("Trying to import app...")
try:
    import app
    print("  ✓ app imported successfully")
    print(f"  Location: {app.__file__}")
except ImportError as e:
    print(f"  ✗ Failed to import app")
    print(f"  Error: {e}")

print()

# Try to import app.main
print("Trying to import app.main...")
try:
    import app.main
    print("  ✓ app.main imported successfully")
    print(f"  Location: {app.main.__file__}")
except ImportError as e:
    print(f"  ✗ Failed to import app.main")
    print(f"  Error: {e}")

print()
print("=" * 60)

# Recommendations
print("Recommendations:")
print("=" * 60)

if not os.path.exists("app"):
    print("❌ 'app' folder not found!")
    print("   → Create folder structure or ensure you're in the correct directory")
elif not os.path.exists("app/__init__.py"):
    print("❌ 'app/__init__.py' not found!")
    print("   → Create empty __init__.py file in app folder")
elif not os.path.exists("app/main.py"):
    print("❌ 'app/main.py' not found!")
    print("   → Create main.py file with FastAPI app")
else:
    print("✓ Basic structure looks good!")
    print("  If still getting import error, try:")
    print("  1. Restart PowerShell/terminal")
    print("  2. Deactivate and reactivate venv")
    print("  3. Check for syntax errors in app/main.py")

print()
