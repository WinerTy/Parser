#!/bin/bash


if ! command -v uv &>/dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi


if [ ! -d ".venv" ]; then
    uv venv --python python3.13
fi

source .venv/bin/activate

if [ -f "requirements.txt" ];then
    uv pip install -r requirements.txt
else
    uv pip sync
fi

cd src/parser/ && uv run python main.py