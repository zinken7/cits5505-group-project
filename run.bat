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

echo Seeding media...
"%VENV_PY%" scripts\seed_media.py || goto :error

echo Seeding items...
"%VENV_PY%" scripts\seed_items.py || goto :error

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