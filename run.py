try:
    import config
except ImportError:
    print("No config.py found!")
    exit(1)
from app import manager

if __name__ == '__main__':
    manager.run()
