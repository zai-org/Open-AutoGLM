@echo off
echo ===========================================
echo AutoGLM Android App Installer
echo ===========================================

REM Check if adb is in PATH
where adb >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] ADB is not found in your PATH.
    echo Please install Android Platform Tools and add it to your PATH.
    pause
    exit /b 1
)

REM Check for connected devices
echo Checking for connected devices...
adb devices
adb get-state >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] No device connected or authorized.
    echo Please connect your Android phone via USB and enable USB Debugging.
    pause
    exit /b 1
)

REM Check if gradlew.bat exists
if not exist "gradlew.bat" (
    echo [ERROR] gradlew.bat not found.
    echo Please run this script from the android-app directory.
    pause
    exit /b 1
)

echo.
echo Starting build and install process...
echo This may take a few minutes...
echo.

call gradlew.bat installDebug

if %errorlevel% equ 0 (
    echo.
    echo ===========================================
    echo Installation Success!
    echo ===========================================
    echo You can now launch the app on your phone.
) else (
    echo.
    echo ===========================================
    echo Installation Failed
    echo ===========================================
)

pause
