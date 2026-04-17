#!/usr/bin/env bash

authbench_flag_enabled() {
  case "$1" in
    1|true|TRUE|yes|YES|on|ON)
      return 0
      ;;
    0|false|FALSE|no|NO|off|OFF|'')
      return 1
      ;;
    *)
      return 2
      ;;
  esac
}

authbench_apply_default_package_mirrors() {
  if authbench_flag_enabled "${AUTHBENCH_USE_NJU_GHCR:-0}"; then
    : "${AUTHBENCH_GHCR_MIRROR_PREFIX:=ghcr.nju.edu.cn}"
  else
    case $? in
      1)
        ;;
      2)
        echo "Unsupported AUTHBENCH_USE_NJU_GHCR value: ${AUTHBENCH_USE_NJU_GHCR}" >&2
        exit 1
        ;;
    esac
  fi

  if authbench_flag_enabled "${AUTHBENCH_USE_TUNA:-0}"; then
    : "${AUTHBENCH_UBUNTU_APT_MIRROR:=http://mirrors.tuna.tsinghua.edu.cn/ubuntu/}"
    : "${AUTHBENCH_UBUNTU_SECURITY_APT_MIRROR:=http://mirrors.tuna.tsinghua.edu.cn/ubuntu/}"
    : "${AUTHBENCH_DEBIAN_APT_MIRROR:=http://mirrors.tuna.tsinghua.edu.cn/debian/}"
    : "${AUTHBENCH_DEBIAN_SECURITY_APT_MIRROR:=http://mirrors.tuna.tsinghua.edu.cn/debian-security/}"
    : "${PIP_INDEX_URL:=https://pypi.tuna.tsinghua.edu.cn/simple}"
    : "${PIP_TRUSTED_HOST:=pypi.tuna.tsinghua.edu.cn}"
  else
    case $? in
      1)
        ;;
      2)
        echo "Unsupported AUTHBENCH_USE_TUNA value: ${AUTHBENCH_USE_TUNA}" >&2
        exit 1
        ;;
    esac
  fi

  export AUTHBENCH_GHCR_MIRROR_PREFIX
  export AUTHBENCH_UBUNTU_APT_MIRROR
  export AUTHBENCH_UBUNTU_SECURITY_APT_MIRROR
  export AUTHBENCH_DEBIAN_APT_MIRROR
  export AUTHBENCH_DEBIAN_SECURITY_APT_MIRROR
  export PIP_INDEX_URL
  export PIP_TRUSTED_HOST
}
