from app import app

try:
    import config
except ImportError:
    print("No config.py found!")
    exit(1)
