#!/bin/bash
if ! command -v python3 &>/dev/null; then
    echo "Python 3 не установлен. Установите Python 3.13 или новее."
    exit 1
fi


if ! command -v uv &>/dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

uv venv --python python3.13

source .venv/bin/activate

uv pip install -r requirements.txt

uv run python src/parcer/main.py