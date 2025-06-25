#!/usr/bin/env python3
"""
Setup script for the multi-agent solution.
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, check=True):
    """Run a shell command and return the result."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if check and result.returncode != 0:
        print(f"Error running command: {command}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)
    
    return result


def check_python_version():
    """Check if Python version is 3.10 or later."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("Error: Python 3.10 or later is required.")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        sys.exit(1)
    
    print(f"✓ Python version {version.major}.{version.minor}.{version.micro} is supported")


def check_virtual_environment():
    """Check if running in a virtual environment."""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✓ Running in virtual environment")
        return True
    else:
        print("⚠ Not running in virtual environment")
        print("It's recommended to use a virtual environment:")
        print("  python -m venv venv")
        print("  source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
        
        response = input("Continue anyway? (y/N): ").strip().lower()
        if response != 'y':
            sys.exit(1)
        return False


def install_dependencies():
    """Install required Python packages."""
    print("\nInstalling dependencies...")
    
    # Upgrade pip first
    run_command(f"{sys.executable} -m pip install --upgrade pip")
    
    # Install requirements
    if os.path.exists("requirements.txt"):
        run_command(f"{sys.executable} -m pip install -r requirements.txt")
        print("✓ Dependencies installed successfully")
    else:
        print("Error: requirements.txt not found")
        sys.exit(1)


def setup_environment_file():
    """Set up the environment configuration file."""
    print("\nSetting up environment configuration...")
    
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if not env_example.exists():
        print("Error: .env.example file not found")
        sys.exit(1)
    
    if env_file.exists():
        print("✓ .env file already exists")
        response = input("Overwrite existing .env file? (y/N): ").strip().lower()
        if response != 'y':
            print("Skipping .env file creation")
            return
    
    # Copy .env.example to .env
    shutil.copy(env_example, env_file)
    print("✓ Created .env file from template")
    print("\nIMPORTANT: Please edit .env file with your Azure AI Foundry credentials:")
    print("- AZURE_AI_INFERENCE_ENDPOINT")
    print("- AZURE_AI_INFERENCE_API_KEY")
    print()


def run_tests():
    """Run the test suite to verify installation."""
    print("\nRunning tests to verify installation...")
    
    try:
        result = run_command(f"{sys.executable} -m pytest tests/ -v", check=False)
        if result.returncode == 0:
            print("✓ All tests passed")
        else:
            print("⚠ Some tests failed (this may be expected without Azure configuration)")
    except FileNotFoundError:
        print("⚠ pytest not found, skipping tests")


def verify_azure_configuration():
    """Verify Azure configuration (optional)."""
    print("\nChecking Azure configuration...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠ .env file not found, please run setup first")
        return False
    
    # Check for required environment variables
    required_vars = [
        "AZURE_AI_INFERENCE_ENDPOINT",
        "AZURE_AI_INFERENCE_API_KEY"
    ]
    
    missing_vars = []
    
    with open(env_file, 'r') as f:
        content = f.read()
        for var in required_vars:
            if f"{var}=" not in content or f"{var}=your-" in content:
                missing_vars.append(var)
    
    if missing_vars:
        print("⚠ Missing or incomplete Azure configuration:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease update your .env file with actual Azure credentials")
        return False
    else:
        print("✓ Azure configuration appears complete")
        return True


def run_demo():
    """Run a basic demo to test the setup."""
    print("\nRunning basic demo...")
    
    if not verify_azure_configuration():
        print("Skipping demo due to incomplete configuration")
        return
    
    try:
        result = run_command(f"{sys.executable} examples/basic_agent_demo.py", check=False)
        if result.returncode == 0:
            print("✓ Demo completed successfully")
        else:
            print("⚠ Demo failed - check your Azure configuration")
            print("Error output:")
            print(result.stderr)
    except Exception as e:
        print(f"⚠ Could not run demo: {e}")


def main():
    """Main setup function."""
    print("Microsoft Semantic Kernel Multi-Agent Solution Setup")
    print("=" * 55)
    
    # Check Python version
    check_python_version()
    
    # Check virtual environment
    check_virtual_environment()
    
    # Install dependencies
    install_dependencies()
    
    # Setup environment file
    setup_environment_file()
    
    # Run tests
    run_tests()
    
    print("\n" + "=" * 55)
    print("Setup completed!")
    print("\nNext steps:")
    print("1. Edit .env file with your Azure AI Foundry credentials")
    print("2. Run: python examples/basic_agent_demo.py")
    print("3. Explore other examples in the examples/ directory")
    print("\nFor more information, see README.md")
    
    # Ask if user wants to run demo
    response = input("\nWould you like to run the basic demo now? (y/N): ").strip().lower()
    if response == 'y':
        run_demo()


if __name__ == "__main__":
    main()
