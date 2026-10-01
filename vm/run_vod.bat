@echo off
cd /d "%~dp0.."
git pull --rebase -q >> vm\vod_watch.log 2>&1
"C:\Users\giode\miniconda\python.exe" vm\vod_watch.py >> vm\vod_watch.log 2>&1
