# ---------- Stage 1: Build ----------
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app

# Dependency layer — re-runs only when pyproject/uv.lock change.
# yt-dlp kept unpinned (-U) for fresh YouTube extractors on dep rebuilds;
# it must stay ABOVE `COPY . .` so source edits never touch this layer.
COPY pyproject.toml uv.lock ./
RUN uv export --format requirements-txt --no-hashes -o requirements.txt \
 && uv pip install --system -r requirements.txt \
 && uv pip install --system --break-system-packages -U yt-dlp \
 && uv pip install --system --break-system-packages -U bgutil-ytdlp-pot-provider

# App source last so code edits don't invalidate anything above.
COPY . .


# ---------- Stage 2: Runtime ----------
FROM python:3.12-slim
WORKDIR /app

# Heavy static tooling FIRST — independent of Python deps and app source.
# Stays cached across dependency bumps and every code deploy.
RUN apt-get update && apt-get install -y unzip curl ffmpeg \
    && curl -fsSL https://github.com/denoland/deno/releases/download/v2.9.5/deno-x86_64-unknown-linux-gnu.zip \
        -o /tmp/deno.zip \
    && unzip -o /tmp/deno.zip -d /usr/local/bin \
    && rm /tmp/deno.zip \
    && chmod +x /usr/local/bin/deno \
    && deno --version
ENV PATH="/usr/local/bin:${PATH}"

# Python packages + entry points from builder (changes only on lockfile bump).
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# App source.
COPY --from=builder /app/src ./src
COPY --from=builder /app/celery_app ./celery_app



EXPOSE 5000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "5000"]
