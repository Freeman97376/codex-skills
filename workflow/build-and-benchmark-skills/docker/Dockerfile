# syntax=docker/dockerfile:1

ARG SKILLBENCH_REV=d05557e1370704fda56aebf587bd7ca51cc8571f
ARG CODEX_VERSION=0.146.0

FROM rust:1.90-bookworm AS skillbench-builder
ARG SKILLBENCH_REV
RUN apt-get update \
    && apt-get install --yes --no-install-recommends ca-certificates git \
    && rm -rf /var/lib/apt/lists/*
RUN cargo install \
    --locked \
    --git https://github.com/SunChJ/skillbench.git \
    --rev "${SKILLBENCH_REV}" \
    --root /opt/skillbench

FROM node:22-bookworm-slim AS runtime
ARG CODEX_VERSION
LABEL org.opencontainers.image.title="Codex SkillBench runner"
LABEL org.opencontainers.image.description="Pinned Linux runner for low-usage SkillBench comparisons"

RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        ca-certificates \
        curl \
        git \
        python3 \
        python-is-python3 \
    && rm -rf /var/lib/apt/lists/*
RUN npm install --global "@openai/codex@${CODEX_VERSION}" \
    && npm cache clean --force

COPY --from=skillbench-builder /opt/skillbench/bin/skillbench /usr/local/bin/skillbench

RUN useradd --create-home --uid 10001 runner \
    && mkdir --parents /workspace /run/codex-auth \
    && chown --recursive runner:runner /workspace /run/codex-auth

USER runner
ENV HOME=/home/runner
WORKDIR /workspace

CMD ["skillbench", "--help"]
