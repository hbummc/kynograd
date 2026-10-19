@echo off
rem Kynograd tracker: pulls gold and the town bank from EarthMC every 5 minutes.
rem Double-click to start. Close the window to stop.
cd /d "%~dp0"
title Kynograd tracker
where py >nul 2>nul && (py scripts\update.py --watch 5) || (python scripts\update.py --watch 5)
echo.
echo The tracker stopped. If it says Python was not found, install it from python.org
echo (tick "Add python.exe to PATH" during setup) and double-click this file again.
pause
