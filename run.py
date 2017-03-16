import os
import sys
try:
    import config
except ImportError:
    print("No config.py found!")
    exit(1)
from app import app, manager

if __name__ == '__main__':
    manager.run()
