#!/usr/bin/env python
r"""
Setup shared Python virtual environment for all u-blox build scripts.

Run this once at repo root to create and configure the shared .venv:
    python setup_venv.py

Then activate it:
    # Windows CMD:
    .venv\Scripts\activate.bat
    # Windows PowerShell:
    .venv\Scripts\Activate.ps1
    # Linux/macOS/WSL:
    source .venv/bin/activate

All build scripts (iris_w10_build.py, nora_w50_w51_build.py, etc.) will work
with this shared venv. It installs 'west' (MCUXpresso SDK manager) which all
variants need.
"""

import os
import sys
import subprocess
import platform

def get_repo_root():
    """Get repository root directory."""
    return os.path.dirname(os.path.abspath(__file__))

def create_venv():
    """Create virtual environment."""
    repo_root = get_repo_root()
    venv_path = os.path.join(repo_root, ".venv")
    
    if os.path.exists(venv_path):
        print(f"✅ Virtual environment already exists: {venv_path}")
        return venv_path
    
    print(f"📦 Creating virtual environment at {venv_path}...")
    subprocess.check_call([sys.executable, "-m", "venv", venv_path])
    print(f"✅ Virtual environment created")
    return venv_path

def get_pip_executable(venv_path):
    """Get pip executable for this platform."""
    # Check for Unix-style first (Linux, macOS, WSL, Git Bash/MSYS2)
    unix_pip = os.path.join(venv_path, "bin", "pip")
    if os.path.exists(unix_pip) or os.path.exists(unix_pip + ".exe"):
        return unix_pip + ".exe" if os.path.exists(unix_pip + ".exe") else unix_pip
    
    # Fall back to Windows-style
    windows_pip = os.path.join(venv_path, "Scripts", "pip.exe")
    if os.path.exists(windows_pip):
        return windows_pip
    
    # Return most likely based on platform (for error message)
    if platform.system() == "Windows":
        return windows_pip
    else:
        return unix_pip

def install_west(venv_path):
    """Install/update west in the virtual environment."""
    pip_exe = get_pip_executable(venv_path)
    
    if not os.path.exists(pip_exe):
        print("❌ pip not found in venv. Virtual environment may be corrupted.")
        sys.exit(1)
    
    print("📥 Installing/updating 'west' (MCUXpresso SDK manager)...")
    subprocess.check_call([pip_exe, "install", "-U", "west"])
    print("✅ west installed successfully")

def get_activation_command():
    """Get activation command for this platform."""
    if platform.system() == "Windows":
        # Check if we're in Git Bash/MSYS2 by looking for MSYSTEM env var
        if os.environ.get("MSYSTEM"):
            return "source .venv/Scripts/activate"  # Git Bash uses Unix-style source
        else:
            return ".venv\\Scripts\\activate.bat"  # Pure Windows CMD
    else:
        return "source .venv/bin/activate"

def main():
    print("🔧 u-blox Build Scripts - Virtual Environment Setup\n")
    
    try:
        venv_path = create_venv()
        install_west(venv_path)
        
        activate_cmd = get_activation_command()
        
        print(f"\n{'='*60}")
        print("✅ Setup complete!\n")
        print("Next step: Activate the virtual environment\n")
        print(f"  {activate_cmd}\n")
        print(f"Then run any build script, e.g.:\n")
        print(f"  python IRIS-W10-GettingStartedSDK/iris_w10_build.py doctor")
        print(f"\nTo deactivate later, run:")
        print(f"  deactivate")
        print(f"{'='*60}\n")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
