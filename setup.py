#!/usr/bin/env python3
"""
Setup script for Bridged Demo - Natural Language to Pinecone Query Agent
This script helps set up the environment and install dependencies
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, shell=True):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=shell, check=True, capture_output=True, text=True)
        print(f"✅ {command}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {command}")
        print(f"Error: {e.stderr}")
        return False, e.stderr

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible. Need Python 3.9+")
        return False

def setup_with_pip():
    """Setup using pip and virtual environment"""
    print("\n🐍 Setting up with pip and virtual environment...")
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists("venv"):
        success, _ = run_command("python -m venv venv")
        if not success:
            return False
    
    # Activate and install dependencies
    if os.name == 'nt':  # Windows
        activate_cmd = r".\venv\Scripts\activate"
        pip_cmd = r".\venv\Scripts\pip"
    else:  # Unix/Linux/Mac
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    success, _ = run_command(f"{pip_cmd} install --upgrade pip")
    if not success:
        return False
        
    success, _ = run_command(f"{pip_cmd} install -r requirements.txt")
    return success

def setup_with_poetry():
    """Setup using Poetry"""
    print("\n🎭 Setting up with Poetry...")
    
    # Check if poetry is installed
    success, _ = run_command("poetry --version")
    if not success:
        print("❌ Poetry not found. Please install Poetry first:")
        print("   curl -sSL https://install.python-poetry.org | python3 -")
        return False
    
    # Install dependencies
    success, _ = run_command("poetry install --no-root")
    return success

def setup_with_uv():
    """Setup using uv"""
    print("\n⚡ Setting up with uv...")
    
    # Check if uv is installed
    success, _ = run_command("uv --version")
    if not success:
        print("❌ uv not found. Please install uv first:")
        print("   curl -LsSf https://astral.sh/uv/install.sh | sh")
        return False
    
    # Install dependencies
    success, _ = run_command("uv pip install -r requirements.txt")
    return success

def main():
    print("🚀 Bridged Demo Setup")
    print("=" * 50)
    
    if not check_python_version():
        sys.exit(1)
    
    # Try different package managers
    setup_methods = [
        ("pip", setup_with_pip),
        ("poetry", setup_with_poetry),
        ("uv", setup_with_uv)
    ]
    
    for name, setup_func in setup_methods:
        try:
            if setup_func():
                print(f"\n✅ Setup completed successfully with {name}!")
                print("\nNext steps:")
                print("1. Run the Flask app: python simple_frontend.py")
                print("2. Run the FastAPI app: python fastapi_app.py")
                print("3. Or use the provided scripts in the scripts/ directory")
                return
        except Exception as e:
            print(f"❌ Setup with {name} failed: {e}")
            continue
    
    print("\n❌ All setup methods failed. Please check the errors above.")
    sys.exit(1)

if __name__ == "__main__":
    main()
