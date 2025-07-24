import subprocess
import sys

def run_test():
    try:
        subprocess.run(
            [sys.executable, "test_connect.py"],
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False

if __name__ == "__main__":
    if run_test():
        print("✅ Connection OK. Running main.py")
        subprocess.run([sys.executable, "main.py"])
    else:
        print("❌ Connection failed. Exiting.")
