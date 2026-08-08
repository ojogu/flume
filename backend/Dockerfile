# ---------- Stage 1: Build ----------
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv export --format requirements-txt --no-hashes -o requirements.txt
RUN uv pip install --system -r requirements.txt
COPY . .
RUN uv pip install --system --break-system-packages -U yt-dlp


# ---------- Stage 2: Runtime ----------
FROM python:3.12-slim
WORKDIR /app

# Copy installed packages from builder (this is what you're missing)
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

RUN apt-get update && apt-get install -y unzip curl ffmpeg \
    && curl -fsSL https://github.com/denoland/deno/releases/download/v2.9.5/deno-x86_64-unknown-linux-gnu.zip \
        -o /tmp/deno.zip \
    && unzip -o /tmp/deno.zip -d /usr/local/bin \
    && rm /tmp/deno.zip \
    && chmod +x /usr/local/bin/deno \
    && deno --version
ENV PATH="/usr/local/bin:${PATH}"

# Copy app source
COPY --from=builder /app/src ./src
COPY --from=builder /app/celery_app ./celery_app



EXPOSE 5000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "5000"]