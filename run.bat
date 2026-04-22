@echo off
setlocal

echo Activating virtual environment...
call .venv\Scripts\activate

echo Seeding media...
python scripts\seed_media.py || goto :error

echo Seeding items...
python scripts\seed_items.py || goto :error

echo Starting backend in new window...
start "BACKEND" cmd /k "call .venv\Scripts\activate && python run.py"

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