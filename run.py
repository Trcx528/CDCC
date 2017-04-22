#!/usr/bin/env python3
"""This file is just for easy startup in a development enviroment"""
import sys
import re
import os
from app import app

# for uwsgi
application = app

if __name__ == '__main__':
    try:
        import config
        if config.prod["DEBUG"] is None or config.prod["DEBUG"] is True:
            os.environ["FLASK_DEBUG"] = "True"
        os.environ["FLASK_APP"] = sys.argv[0]
        os.environ["FLASK_INLINE"] = "True"
        os.system('"' + sys.executable + '" -m flask ' + ' '.join(sys.argv[1:]))
    except ImportError:
        print("No config.py found!")
        exit(1)
else:
    if "FLASK_INLINE" not in os.environ:
        print("Launching %s for vscode debugger" % app.name)
        from flask.cli import main
        sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
        #sys.exit(main())
