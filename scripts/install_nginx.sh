#!/usr/bin/env bash
set -euo pipefail

LOG_FILE="logs/provisioning.log"

log() {
  local level="$1"
  local msg="$2"
  echo "$(date '+%Y-%m-%d %H:%M:%S') | ${level} | bash | ${msg}" | tee -a "$LOG_FILE"
}

log "INFO" "Nginx install script started"

if [[ "${EUID}" -ne 0 ]]; then
  log "ERROR" "This script must be run as root (use sudo)."
  exit 1
fi

if command -v apt-get >/dev/null 2>&1; then
  PKG_MGR="apt"
elif command -v dnf >/dev/null 2>&1; then
  PKG_MGR="dnf"
elif command -v yum >/dev/null 2>&1; then
  PKG_MGR="yum"
elif command -v apk >/dev/null 2>&1; then
  PKG_MGR="apk"
else
  log "ERROR" "No supported package manager found (apt/dnf/yum/apk)."
  exit 2
fi

if command -v nginx >/dev/null 2>&1; then
  log "INFO" "Nginx already installed. Skipping installation."
  log "INFO" "Nginx install script finished"
  exit 0
fi

log "INFO" "Installing nginx using ${PKG_MGR}..."

case "$PKG_MGR" in
  apt)
    apt-get update -y
    apt-get install -y nginx
    ;;
  dnf)
    dnf install -y nginx
    ;;
  yum)
    yum install -y nginx
    ;;
  apk)
    apk add --no-cache nginx
    ;;
esac

log "INFO" "Nginx installed successfully"
log "INFO" "Nginx install script finished"
