#!/usr/bin/env python3
"""
DePIN Simulator UI Launcher

Ensures dependencies are installed and launches the Streamlit interface.
"""

import subprocess
import sys
import os

def check_and_install_dependencies():
    """Check and install required dependencies"""
    try:
        import streamlit
        import plotly
        print("✅ All UI dependencies are installed")
        return True
    except ImportError:
        print("📦 Installing missing UI dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit", "plotly"])
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False

def launch_streamlit():
    """Launch the Streamlit application"""
    try:
        print("🚀 Launching DePIN Simulator UI...")
        print("📍 Open your browser to: http://localhost:8501")
        print("🛑 Press Ctrl+C to stop the server")
        print("-" * 50)
        
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])
        
    except KeyboardInterrupt:
        print("\n👋 DePIN Simulator UI stopped")
    except Exception as e:
        print(f"❌ Error launching UI: {e}")

if __name__ == "__main__":
    print("🚀 DePIN Simulator UI Launcher")
    print("=" * 50)
    
    # Check dependencies
    if check_and_install_dependencies():
        # Launch UI
        launch_streamlit()
    else:
        print("❌ Cannot launch UI due to dependency issues")
        print("💡 Try manually installing: pip install streamlit plotly")