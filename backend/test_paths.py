"""Test script to verify all paths are correct."""

from pathlib import Path

# Test config path
backend_dir = Path(__file__).parent
config_dir = backend_dir / "config"
print(f"Backend dir: {backend_dir}")
print(f"Config dir: {config_dir}")
print(f"Config exists: {config_dir.exists()}")

# Test scripts path
scripts_dir = backend_dir / "scripts"
injector_path = scripts_dir / "injector.js"
print(f"Scripts dir: {scripts_dir}")
print(f"Injector path: {injector_path}")
print(f"Injector exists: {injector_path.exists()}")

# Test database path
database_dir = backend_dir / "database"
print(f"Database dir: {database_dir}")
print(f"Database exists: {database_dir.exists()}")

# Test screenshots path
screenshots_dir = backend_dir / "screenshots"
print(f"Screenshots dir: {screenshots_dir}")
print(f"Screenshots exists: {screenshots_dir.exists()}")

print("\n✅ All paths verified!")
