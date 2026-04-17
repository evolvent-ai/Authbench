ARG AUTHBENCH_PYTHON_PY313_PLAIN_BASE=authbench-python-py313-plain-base:local
ARG AUTHBENCH_GHCR_PREFIX=ghcr.io
FROM ${AUTHBENCH_GHCR_PREFIX}/openclaw/openclaw:2026.3.7@sha256:70c5677580a958f704eb27297a62661b501534c3b2b9dec7a61e5ed5aa0c24cf AS openclaw_runtime
FROM ${AUTHBENCH_PYTHON_PY313_PLAIN_BASE}

ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY
ARG http_proxy
ARG https_proxy
ARG no_proxy
ARG AUTHBENCH_UBUNTU_APT_MIRROR
ARG AUTHBENCH_UBUNTU_SECURITY_APT_MIRROR
ARG AUTHBENCH_DEBIAN_APT_MIRROR
ARG AUTHBENCH_DEBIAN_SECURITY_APT_MIRROR

COPY --from=openclaw_runtime /app /opt/openclaw
COPY --from=openclaw_runtime /usr/local/bin/node /usr/local/bin/node
COPY libs/openclaw_replay_assets/openclaw_plugins/authbench-policy-guard /opt/authbench/plugins/authbench-policy-guard
RUN chmod 755 /opt/authbench/plugins /opt/authbench/plugins/authbench-policy-guard \
    && chmod 644 /opt/authbench/plugins/authbench-policy-guard/index.js \
    /opt/authbench/plugins/authbench-policy-guard/openclaw.plugin.json
COPY libs/openclaw_replay_assets/authbench-landlock/authbench_landlock_launch.c /tmp/authbench_landlock_launch.c
RUN set -eu; \
    ubuntu_mirror="${AUTHBENCH_UBUNTU_APT_MIRROR:-}"; \
    ubuntu_security_mirror="${AUTHBENCH_UBUNTU_SECURITY_APT_MIRROR:-}"; \
    debian_mirror="${AUTHBENCH_DEBIAN_APT_MIRROR:-}"; \
    debian_security_mirror="${AUTHBENCH_DEBIAN_SECURITY_APT_MIRROR:-}"; \
    if [ -n "$ubuntu_mirror" ] && [ -f /etc/apt/sources.list.d/ubuntu.sources ]; then \
        ubuntu_mirror="${ubuntu_mirror%/}"; \
        sed -i -E "s|URIs: https?://archive\\.ubuntu\\.com/ubuntu/?|URIs: ${ubuntu_mirror}|g" /etc/apt/sources.list.d/ubuntu.sources; \
    fi; \
    if [ -n "$ubuntu_security_mirror" ] && [ -f /etc/apt/sources.list.d/ubuntu.sources ]; then \
        ubuntu_security_mirror="${ubuntu_security_mirror%/}"; \
        sed -i -E "s|URIs: https?://security\\.ubuntu\\.com/ubuntu/?|URIs: ${ubuntu_security_mirror}|g" /etc/apt/sources.list.d/ubuntu.sources; \
    fi; \
    if [ -n "$debian_mirror" ] && [ -f /etc/apt/sources.list.d/debian.sources ]; then \
        debian_mirror="${debian_mirror%/}"; \
        sed -i -E "s|URIs: https?://deb\\.debian\\.org/debian/?|URIs: ${debian_mirror}|g" /etc/apt/sources.list.d/debian.sources; \
    fi; \
    if [ -n "$debian_security_mirror" ] && [ -f /etc/apt/sources.list.d/debian.sources ]; then \
        debian_security_mirror="${debian_security_mirror%/}"; \
        sed -i -E "s|URIs: https?://security\\.debian\\.org/debian-security/?|URIs: ${debian_security_mirror}|g" /etc/apt/sources.list.d/debian.sources; \
    fi
RUN export HTTP_PROXY="${HTTP_PROXY}" HTTPS_PROXY="${HTTPS_PROXY}" NO_PROXY="${NO_PROXY}" \
        http_proxy="${http_proxy:-${HTTP_PROXY}}" https_proxy="${https_proxy:-${HTTPS_PROXY}}" no_proxy="${no_proxy:-${NO_PROXY}}"; \
    apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y gcc libc6-dev \
    && gcc -O2 -Wall -Wextra -o /usr/local/bin/authbench-landlock-launch /tmp/authbench_landlock_launch.c \
    && rm /tmp/authbench_landlock_launch.c \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /opt/openclaw/openclaw.mjs /usr/local/bin/openclaw

ENV TEST_DIR=/tests
