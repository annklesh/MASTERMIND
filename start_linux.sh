#!/bin/bash

VENV_DIR="venv"

if [ ! -f "$VENV_DIR/bin/python" ]; then
    python3 -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/python" -c "import PySide6" >/dev/null 2>&1

if [ $? -ne 0 ]; then
    "$VENV_DIR/bin/python" -m pip install PySide6
fi

"$VENV_DIR/bin/python" app.py