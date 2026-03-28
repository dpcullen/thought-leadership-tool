@echo off
title TL Engine - Thought Leadership Tool
echo.
echo  ========================================
echo   Starting Thought Leadership Engine...
echo  ========================================
echo.
echo  Your browser will open automatically.
echo  Keep this window open while using the tool.
echo  Close this window to stop the server.
echo.

:: Start the Flask app and open browser
start http://localhost:5001
"C:\Users\dalla\AppData\Local\Programs\Python\Python311\python.exe" "%~dp0app.py"

pause
