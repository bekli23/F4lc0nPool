@echo off
cd /d %~dp0
echo Running main.py...

:: Try to use available Python command
where python >nul 2>&1
if %errorlevel%==0 (
    python main.py
    goto END
)

where python3 >nul 2>&1
if %errorlevel%==0 (
    python3 main.py
    goto END
)

where py >nul 2>&1
if %errorlevel%==0 (
    py main.py
    goto END
)

echo.
echo [ERROR] Python is not installed or not added to PATH.

:END
echo.
pause
