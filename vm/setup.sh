#!/usr/bin/env bash
# One-time setup on the Oracle VM (Ubuntu, ARM/aarch64). Run as the login user.
set -euo pipefail

sudo apt-get update
sudo apt-get install -y python3-venv python3-pip ffmpeg git

REPO_URL="${1:?usage: setup.sh <git-remote-url-with-token>}"

cd ~
git clone "$REPO_URL" qultura
cd qultura
git config user.name "qultura-vm"
git config user.email "vm@qultura.local"

python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt -r vm/requirements.txt

cp vm/.env.example vm/.env
echo "Now edit vm/.env (YOUTUBE_API_KEY at least), then:"
echo "  sudo cp vm/qultura-live.service /etc/systemd/system/"
echo "  sudo systemctl enable --now qultura-live"
echo "  crontab -e   # add the vod_watch.py line from vm/README (see chat)"
