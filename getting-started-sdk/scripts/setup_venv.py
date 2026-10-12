#!/usr/bin/env python3
r"""
Setup shared Python virtual environment for all u-blox build scripts.

Creates and configures the shared .venv at the getting-started-sdk root:
    cd getting-started-sdk
    python scripts/setup_venv.py

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
import shutil
import sysconfig

def get_sdk_root():
    """Get the SDK root directory (the parent of scripts/)."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def is_mingw_python(platform_tag=None):
    """True for MSYS2/MinGW CPython (e.g. C:\\msys64\\ucrt64\\bin\\python.exe)."""
    tag = sysconfig.get_platform() if platform_tag is None else platform_tag
    return tag.startswith("mingw")


def find_native_python():
    """A python.org/Store CPython 3.10+ found through the py launcher, or None."""
    py = shutil.which("py")
    if not py:
        return None
    probe = ("import sys, sysconfig; "
             "ok = not sysconfig.get_platform().startswith('mingw') and sys.version_info >= (3, 10); "
             "print(sys.executable if ok else '')")
    try:
        result = subprocess.run([py, "-3", "-c", probe], capture_output=True,
                                text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    exe = result.stdout.strip()
    return exe or None


def select_base_python():
    """Interpreter that creates the venv. On Windows it must not be MSYS2/MinGW."""
    if platform.system() != "Windows" or not is_mingw_python():
        return sys.executable
    print(f"[WARNING] {sys.executable} is an MSYS2/MinGW Python.")
    print("          Its venv has no Scripts\\python.exe (ubx-sdk.cmd ignores it) and")
    print("          psutil, needed by pylink-square, has no wheels for it.")
    native = find_native_python()
    if native:
        print(f"[INFO] Creating the venv with {native} instead.\n")
        return native
    print("[FAIL] No native Windows Python 3.10+ found through the py launcher.")
    print("       Install one from https://www.python.org/downloads/ and rerun:")
    print("       py -3 scripts\\setup_venv.py")
    sys.exit(1)


def create_venv():
    """Create virtual environment in getting-started-sdk/.venv."""
    sdk_root = get_sdk_root()
    venv_path = os.path.join(sdk_root, ".venv")

    # Check if venv already exists
    if os.path.exists(venv_path):
        if (platform.system() == "Windows"
                and not os.path.exists(os.path.join(venv_path, "Scripts", "python.exe"))):
            print(f"[FAIL] {venv_path} has no Scripts\\python.exe; it was created by an")
            print("       MSYS2, Git Bash or WSL Python. Remove it and rerun this script.")
            sys.exit(1)
        print(f"[OK] Virtual environment already exists: {venv_path}")
        return venv_path

    print(f"Creating virtual environment at {venv_path}...")
    subprocess.check_call([select_base_python(), "-m", "venv", venv_path])
    print("[OK] Virtual environment created")
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
        print("[FAIL] pip not found in venv. Virtual environment may be corrupted.")
        sys.exit(1)

    print("Installing/updating 'west' (MCUXpresso SDK manager)...")
    subprocess.check_call([pip_exe, "install", "-U", "west"])
    print("[OK] west installed successfully")

def install_optional_dependencies(venv_path):
    """Install optional dependencies for serial logging and flashing.

    Returns the list of packages that could not be installed.
    """
    pip_exe = get_pip_executable(venv_path)
    failed = []

    if not os.path.exists(pip_exe):
        return ["pyserial", "pylink-square"]

    print("Installing optional dependencies (pyserial, pylink, pytest, pytest-cov)...")
    for package, purpose in (("pyserial", "serial logging"),
                             ("pylink-square", "J-Link flashing"),
                             ("pytest", "launcher tests"),
                             ("pytest-cov", "test coverage")):
        try:
            subprocess.run([pip_exe, "install", package], check=True, capture_output=True)
            print(f"   [OK] {package} (for {purpose})")
        except subprocess.CalledProcessError as e:
            detail = (e.stderr or b"").decode(errors="replace").strip().splitlines()
            print(f"   [WARNING] {package} could not be installed")
            if detail:
                print(f"             {detail[-1]}")
            failed.append(package)

    return failed

def get_activation_command():
    """Get activation command for this platform."""
    if platform.system() == "Windows":
        if os.environ.get("MSYSTEM"):
            return "source .venv/Scripts/activate"
        return ".venv\\Scripts\\activate.bat   (PowerShell: .venv\\Scripts\\Activate.ps1)"
    return "source .venv/bin/activate"

def main():
    print("u-blox Build Scripts - Virtual Environment Setup\n")

    try:
        venv_path = create_venv()
        install_west(venv_path)
        failed = install_optional_dependencies(venv_path)

        activate_cmd = get_activation_command()

        print(f"\n{'='*60}")
        print("[OK] Setup complete!\n")
        print(f"Virtual environment location: {venv_path}\n")
        if failed:
            print("[WARNING] These optional packages are missing: "
                  f"{', '.join(failed)}")
            print("          --flash and --log require them. Install manually with:")
            print(f"          {get_pip_executable(venv_path)} install {' '.join(failed)}\n")
        launcher = "ubx-sdk.cmd" if platform.system() == "Windows" else "./ubx-sdk.sh"
        print("Next step: the launchers pick up .venv automatically, e.g.:\n")
        print(f"  {launcher} iris-w10 --doctor\n")
        print("To use the venv in your own shell, activate it with:\n")
        print(f"  {activate_cmd}")
        print(f"{'='*60}\n")

    except subprocess.CalledProcessError as e:
        print(f"\n[FAIL] Setup failed: {e}")
        sys.exit(1)
    except OSError as e:
        print(f"\n[FAIL] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
