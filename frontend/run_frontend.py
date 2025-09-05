#!/usr/bin/env python3
"""
Script to run the PDF RAG Chatbot Frontend
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Run the Streamlit frontend application"""
    frontend_dir = Path(__file__).parent
    os.chdir(frontend_dir)

    # Install requirements if needed
    requirements_file = frontend_dir / "requirements.txt"
    if requirements_file.exists():
        print("📦 Installing requirements...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

    # Run Streamlit
    print("🚀 Starting PDF RAG Chatbot Frontend...")
    print(f"📍 Frontend directory: {frontend_dir}")
    print("🌐 Open your browser to http://localhost:8501")
    print("-" * 50)

    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Frontend stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start frontend: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
