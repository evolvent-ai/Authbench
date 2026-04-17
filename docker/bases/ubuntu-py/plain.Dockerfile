FROM ubuntu:24.04

ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY
ARG http_proxy
ARG https_proxy
ARG no_proxy
ARG PIP_INDEX_URL
ARG PIP_EXTRA_INDEX_URL
ARG PIP_TRUSTED_HOST
ARG AUTHBENCH_UBUNTU_APT_MIRROR
ARG AUTHBENCH_UBUNTU_SECURITY_APT_MIRROR
ARG AUTHBENCH_DEBIAN_APT_MIRROR
ARG AUTHBENCH_DEBIAN_SECURITY_APT_MIRROR

ENV DEBIAN_FRONTEND=noninteractive

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

RUN set -eu; \
    if [ -n "${PIP_INDEX_URL:-}" ] || [ -n "${PIP_EXTRA_INDEX_URL:-}" ] || [ -n "${PIP_TRUSTED_HOST:-}" ]; then \
        { \
            echo "[global]"; \
            if [ -n "${PIP_INDEX_URL:-}" ]; then echo "index-url = ${PIP_INDEX_URL}"; fi; \
            if [ -n "${PIP_EXTRA_INDEX_URL:-}" ]; then echo "extra-index-url = ${PIP_EXTRA_INDEX_URL}"; fi; \
            if [ -n "${PIP_TRUSTED_HOST:-}" ]; then echo "trusted-host = ${PIP_TRUSTED_HOST}"; fi; \
        } > /etc/pip.conf; \
    else \
        rm -f /etc/pip.conf; \
    fi

RUN export HTTP_PROXY="${HTTP_PROXY}" HTTPS_PROXY="${HTTPS_PROXY}" NO_PROXY="${NO_PROXY}" \
        http_proxy="${http_proxy:-${HTTP_PROXY}}" https_proxy="${https_proxy:-${HTTPS_PROXY}}" no_proxy="${no_proxy:-${NO_PROXY}}"; \
    apt-get update \
    && apt-get install -y \
        asciinema \
        ca-certificates \
        curl \
        python3 \
        python3-pytest \
        strace \
        tmux \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
