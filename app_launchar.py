#!/usr/bin/env python3
"""
Container Loading Optimizer Launcher
Simple launcher script for the enhanced container loading optimizer
"""

import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['numpy', 'matplotlib', 'tkinter']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            else:
                __import__(package)
            print(f"✅ {package} - OK")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - Missing")
    
    return missing_packages

def install_dependencies(missing_packages):
    """Install missing dependencies"""
    if not missing_packages:
        return True
    
    print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
    
    # Handle tkinter separately as it's not pip-installable
    if 'tkinter' in missing_packages:
        print("❌ tkinter is missing. Please install it through your system package manager:")
        print("   Ubuntu/Debian: sudo apt-get install python3-tk")
        print("   CentOS/RHEL: sudo yum install tkinter")
        print("   macOS: tkinter should be included with Python")
        print("   Windows: tkinter should be included with Python")
        return False
    
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def run_application():
    """Run the main application"""
    try:
        # Import and run the main application
        from main import ContainerLoadingGUI
        import tkinter as tk
        
        print("\n🚀 Starting Container Loading Optimizer...")
        root = tk.Tk()
        app = ContainerLoadingGUI(root)
        root.mainloop()
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import main application: {e}")
        print("Make sure the main.py file is in the same directory.")
        return False
    except SyntaxError as e:
        print(f"❌ Syntax error in main.py: {e}")
        print(f"Line {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"❌ Application error: {str(e)}")
        import traceback
        print("\nDetailed error information:")
        print("="*60)
        traceback.print_exc()
        print("="*60)
        return False

def main():
    """Main launcher function"""
    print("="*60)
    print("🏗️  ENHANCED CONTAINER LOADING OPTIMIZER")
    print("="*60)
    
    # Check Python version
    if not check_python_version():
        input("Press Enter to exit...")
        return
    
    print("\n🔍 Checking dependencies...")
    
    # Check dependencies
    missing_packages = check_dependencies()
    
    # Install missing dependencies if any
    if missing_packages:
        if not install_dependencies(missing_packages):
            print("\n❌ Failed to install required dependencies.")
            input("Press Enter to exit...")
            return
    
    print("\n✨ All dependencies are satisfied!")
    
    # Run the main application
    if not run_application():
        input("Press Enter to exit...")
        return

if __name__ == "__main__":
    main()