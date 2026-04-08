from app.core.auth import hash_password
import sys
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    pw = sys.argv[1] if len(sys.argv) > 1 else "Uptarget2026!"
    print(f"Password: {pw}")
    print(f"Hash for JSON: {hash_password(pw)}")