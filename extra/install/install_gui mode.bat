@echo off
cd /d %~dp0
echo Running install_gui.py...

:: Try to use available Python command
where python >nul 2>&1
if %errorlevel%==0 (
    python install_gui.py
    goto END
)

where python3 >nul 2>&1
if %errorlevel%==0 (
    python3 install_gui.py
    goto END
)

where py >nul 2>&1
if %errorlevel%==0 (
    py install_gui.py
    goto END
)

echo.
echo [ERROR] Python is not installed or not added to PATH.

:END
echo.
pause
