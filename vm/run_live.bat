@echo off
cd /d "%~dp0.."
set "PY=C:\Users\giode\miniconda\python.exe"
if not exist "%PY%" set "PY=python"
git rebase --abort >nul 2>&1
git fetch -q origin main >> vm\live_watch.log 2>&1
git rebase -X ours -q origin/main >> vm\live_watch.log 2>&1 || git rebase --abort >> vm\live_watch.log 2>&1
"%PY%" -m pip install -U -q yt-dlp >> vm\live_watch.log 2>&1
"%PY%" vm\live_watch.py --once >> vm\live_watch.log 2>&1
