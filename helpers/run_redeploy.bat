@echo off
echo ================================
echo Deploy Trashlight auf Docker Pi
echo ================================

REM --------- KONFIGURATION ----------
set PI_USER=phri4docker
set PI_HOST=192.168.1.112
set PI_SCRIPT=/home/phri4docker/deploy_trashlight.sh
REM ----------------------------------

echo Verbinde mit %PI_USER%@%PI_HOST% ...
echo.

ssh %PI_USER%@%PI_HOST% "bash %PI_SCRIPT%"

echo.
echo ================================
echo Deployment-Befehl abgeschlossen
echo ================================

pause
