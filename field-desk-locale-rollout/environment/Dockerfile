FROM node:20.19.5-bookworm-slim@sha256:9e70124bd00f47dd023e349cd587132ae61892acc0e47ed641416c3e18f401c3 AS node
FROM python:3.12.12-slim-bookworm@sha256:593bd06efe90efa80dc4eee3948be7c0fde4134606dd40d8dd8dbcade98e669c
RUN apt-get update && apt-get install -y --no-install-recommends git curl ca-certificates ripgrep \
 && pip install --no-cache-dir playwright==1.56.0 \
 && playwright install --with-deps chromium \
 && rm -rf /var/lib/apt/lists/*
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
COPY install_codex.py /tmp/install_codex.py
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
 && python /tmp/install_codex.py && rm /tmp/install_codex.py && codex --version
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY seed/app/ /app/
RUN mkdir -p /app/output && git init && git add . && git -c user.name=Assignment -c user.email=assignment@example.invalid commit -m 'Original Field Desk starter'
CMD ["sleep", "infinity"]
