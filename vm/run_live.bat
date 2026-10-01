@echo off
cd /d "%~dp0.."
git pull --rebase -q >> vm\live_watch.log 2>&1
"C:\Users\giode\miniconda\python.exe" vm\live_watch.py >> vm\live_watch.log 2>&1
