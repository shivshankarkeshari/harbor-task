FROM python:3.12.12-slim-bookworm@sha256:593bd06efe90efa80dc4eee3948be7c0fde4134606dd40d8dd8dbcade98e669c
RUN apt-get update && apt-get install -y --no-install-recommends git curl ca-certificates ripgrep \
 && pip install --no-cache-dir playwright==1.56.0 \
 && playwright install --with-deps chromium \
 && rm -rf /var/lib/apt/lists/*
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY seed/app/ /app/
RUN mkdir -p /app/output && git init && git add . && git -c user.name=Assignment -c user.email=assignment@example.invalid commit -m 'Original Field Desk starter'
CMD ["sleep", "infinity"]
