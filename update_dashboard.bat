@echo off
title Update HEUNG A Dashboard
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0update_dashboard.ps1" %1
