@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo .venv not found at "%cd%\.venv". Create it first with: python -m venv .venv
    goto :error
)

set "VENV_PY=%cd%\.venv\Scripts\python.exe"

echo Activating virtual environment...
call .venv\Scripts\activate.bat || goto :error

:: Only seed on a fresh database — skip if Media rows already exist.
:: To force a full reseed (e.g. after JSON edits), delete instance\watchlist.db first,
:: or run:  python scripts\seeds.py --clear
"%VENV_PY%" -c "import sys,os; sys.path.insert(0,'.'); from app import create_app; from app.models.media import Media; app=create_app(); ctx=app.app_context(); ctx.push(); sys.exit(0 if Media.query.count()>0 else 1)"
if %ERRORLEVEL% NEQ 0 (
    echo Fresh database -- running scripts\seeds.py (app\data -^> DB^)...
    "%VENV_PY%" scripts\seeds.py || goto :error
) else (
    echo Database already seeded -- skipping seed scripts.
)

echo Starting backend in new window...
start "BACKEND" /D "%~dp0" cmd /k ""%VENV_PY%" run.py"

echo Setting up frontend...
cd frontend || goto :error

call npm install || goto :error

echo Starting frontend in new window...
start "FRONTEND" cmd /k "npm run dev"

echo.
echo All services started:
echo - Backend window: BACKEND
echo - Frontend window: FRONTEND
echo.
echo Close those windows to stop the servers.
goto :eof

:error
echo.
echo Something failed. Check the error above.
pause
exit /b 1