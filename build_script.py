import os
import subprocess
import sys
from pathlib import Path

def build():
    print("Starting build process for UUID Generator Pro...")
    
    # Check if pyinstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller is not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
    main_file = Path("main.py")
    if not main_file.exists():
        print("Error: main.py not found in the current directory.")
        sys.exit(1)
        
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name", "UUID_Generator_Pro",
        "--clean",
        "main.py"
    ]
    
    # We use --onedir instead of --onefile to make it start faster, but if 
    # the user strictly wants a single EXE, they can use --onefile.
    # The prompt asked for "Single EXE"
    cmd_single = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name", "UUID_Generator_Pro",
        "--clean",
        "main.py"
    ]
    
    print(f"Running: {' '.join(cmd_single)}")
    subprocess.check_call(cmd_single)
    
    print("Build complete! Check the 'dist' folder for the executable.")

if __name__ == "__main__":
    build()
