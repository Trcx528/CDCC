#!/usr/bin/env python3

import os
import sys
from app import app

try:
    import config
    if __name__ == '__main__':
        if config.prod["DEBUG"] == None or config.prod["DEBUG"] == True:
            os.environ["FLASK_DEBUG"] = "True"
        os.environ["FLASK_APP"] = sys.argv[0]
        os.system('"' + sys.executable + '" -m flask ' + ' '.join(sys.argv[1:]) )
except ImportError:
    print("No config.py found!")
    exit(1)
