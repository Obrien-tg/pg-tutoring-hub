#!/usr/bin/env python
"""
Wrapper for backend/manage.py - allows running Django commands from repo root.
Usage: python manage.py <command> [args]
"""
import os
import sys
import subprocess

if __name__ == "__main__":
    # Forward all commands to backend/manage.py
    backend_manage = os.path.join(os.path.dirname(__file__), 'backend', 'manage.py')
    result = subprocess.run([sys.executable, backend_manage] + sys.argv[1:])
    sys.exit(result.returncode)
