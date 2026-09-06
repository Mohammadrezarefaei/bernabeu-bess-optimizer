cat << 'EOF' > debug.py
import os
import importlib.util

def run_diagnostics():
    print("--- 🔍 BESS Dashboard Diagnostics ---")
    required_files = [
        "app.py",
        "bernabeu_layout.png",
        "utils/scenarios.py",
        "models/optimizer.py",
        "models/financials.py",
        "requirements.txt"
    ]
    print("\n[File Check]")
    for file_path in required_files:
        exists = os.path.exists(file_path)
        print(f"  - {file_path}: {'✅ Found' if exists else '❌ Missing'}")
        
    required_packages = [
        "streamlit",
        "pandas",
        "numpy",
        "matplotlib",
        "PIL",
        "pulp",
        "streamlit_image_coordinates"
    ]
    print("\n[Package Check]")
    for pkg in required_packages:
        spec = importlib.util.find_spec(pkg)
        print(f"  - {pkg}: {'✅ Installed' if spec is not None else '❌ Missing / Not Found'}")

if __name__ == "__main__":
    run_diagnostics()
EOF
python3 debug.py
