"""
WSGI server entrypoint. Can be called from the `abctf` script.
"""

from . import create_app

app = create_app()
