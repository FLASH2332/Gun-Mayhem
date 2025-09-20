@echo off
cmake --build .
if %ERRORLEVEL% NEQ 0 (
    exit /b %ERRORLEVEL%
)
.\GunMayhem.exe
