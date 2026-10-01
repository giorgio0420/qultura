@echo off
cd /d "%~dp0.."
set "PY=C:\Users\giode\miniconda\python.exe"
if not exist "%PY%" set "PY=python"
git pull --rebase -q >> vm\live_watch.log 2>&1
"%PY%" vm\live_watch.py >> vm\live_watch.log 2>&1
