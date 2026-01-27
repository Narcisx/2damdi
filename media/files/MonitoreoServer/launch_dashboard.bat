@echo off
echo Starting Backend Server...
start /B py server.py
echo Waiting for server to initialize...
timeout /t 3 /nobreak >nul
echo Opening Dashboard...
start index.html
echo ====================================================
echo  Server is running in background.
echo  Close this window to stop the server (mostly).
echo  (To fully kill it, run: taskkill /f /im python.exe)
echo ====================================================
pause
