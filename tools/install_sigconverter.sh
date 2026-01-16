#!/usr/bin/env bash
set -euo pipefail

# Installs and runs sigconverter.io locally on a Linux box using Docker.
#
# This matches the upstream project's recommended Docker flow:
#   docker build -t sigconverter.io .
#   docker run -d -p 8000:8000 sigconverter.io
# citeturn1view0

PORT="${SIGCONVERTER_PORT:-8000}"
REPO_DIR="${SIGCONVERTER_REPO_DIR:-/opt/sigconverter.io}"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker not found. Install Docker and re-run." >&2
  exit 1
fi

sudo mkdir -p "$(dirname "$REPO_DIR")"
if [ ! -d "$REPO_DIR" ]; then
  sudo git clone --depth 1 https://github.com/magicsword-io/sigconverter.io "$REPO_DIR"
fi

sudo docker build -t sigconverter.io "$REPO_DIR"
# Restart container if exists
sudo docker rm -f sigconverter 2>/dev/null || true
sudo docker run -d --restart unless-stopped --name sigconverter -p "${PORT}:8000" sigconverter.io

echo "sigconverter.io is running on http://localhost:${PORT}"
