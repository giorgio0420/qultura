@echo off
cd /d "%~dp0.."
set "PY=C:\Users\giode\miniconda\python.exe"
if not exist "%PY%" set "PY=python"
git pull --rebase -q >> vm\vod_watch.log 2>&1
"%PY%" vm\vod_watch.py >> vm\vod_watch.log 2>&1
