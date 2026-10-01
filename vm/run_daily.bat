@echo off
rem Same job as .github/workflows/daily.yml, run from a PC as a second daily pass.
rem Use a dedicated clone (not the vod/live one): hard reset below wipes local state.
rem Needs GEMINI_API_KEY in .env at the repo root (build.py reads it).
cd /d "%~dp0.."
set "PY=C:\Users\giode\miniconda\python.exe"
if not exist "%PY%" set "PY=python"
call :main >> vm\daily.log 2>&1
exit /b

:main
echo === %date% %time%
git fetch -q origin main
git reset -q --hard origin/main
"%PY%" build.py
if errorlevel 1 (
    rem build.py deletes queue files as it reads them: put them back on failure
    git checkout -q -- .
    echo build fallito
    exit /b 1
)
git add data.json yt_transcripts
git diff --staged --quiet && (echo nessuna novita & exit /b 0)
git commit -q -m "data: pc %date%"
for /l %%i in (1,1,3) do (
    git pull --rebase -q && git push -q && (echo pubblicato & exit /b 0)
    git rebase --abort 2>nul
    ping -n 6 127.0.0.1 >nul
)
echo push fallito
exit /b 1
