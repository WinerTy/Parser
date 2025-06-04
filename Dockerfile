FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
# Эту строку можно убрать
# ENV PATH="/root/.local/bin:${PATH}"

# First copy only the dependency files to leverage Docker cache
COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-dev

# Now copy the rest of the application
COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# ENV PATH="/app/.venv/bin:$PATH" # uv run сам разберется с PATH для venv


CMD ["uv", "run", "python", "src/parcer/main.py"]
