@echo off
setlocal EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

:: Route command
if "%~1"=="" goto :DoDefault
if /i "%~1"=="help" goto :ShowHelp
if /i "%~1"=="/?" goto :ShowHelp
if /i "%~1"=="-h" goto :ShowHelp
if /i "%~1"=="--help" goto :ShowHelp
if /i "%~1"=="build" goto :DoBuild
if /i "%~1"=="clean" goto :DoClean


echo Unknown command: %~1
echo Run 'make help' for usage.
exit /b 1

:DoDefault
call :DoClean
call :DoBuild
exit /b 0

:ShowHelpAndPause
call :ShowHelp
exit /b 0

:ShowHelp
echo Usage: make [command]
echo.
echo Commands:
echo   build      Build hqlauncher.exe using PyInstaller
echo   clean      Remove build artifacts (exe, logs, temp files)

echo   help       Show this help message
exit /b 0

:DoBuild
echo ========================================
echo   Building hqlauncher.exe
echo ========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [FAIL] Python is not installed or not in PATH.
    exit /b 1
)

:: Check / Install PyInstaller
echo Checking PyInstaller...
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo [FAIL] Failed to install PyInstaller.
        exit /b 1
    )
)
python -m PyInstaller --version

:: Create temporary entry point
echo.
echo Preparing build entry point...
set "ENTRY_FILE=_build_entry.py"
(
    echo from hqlauncher.__main__ import main
    echo main^(^)
) > "%ENTRY_FILE%"

:: Clean previous build
echo Cleaning previous build artifacts...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "hqlauncher.spec" del /f "hqlauncher.spec"
if exist "hqlauncher.exe" del /f "hqlauncher.exe"

:: Build
echo.
echo Building hqlauncher.exe...
python -m PyInstaller --onefile --name hqlauncher "%ENTRY_FILE%"
if errorlevel 1 (
    echo.
    echo [FAIL] Build failed.
    if exist "%ENTRY_FILE%" del /f "%ENTRY_FILE%"
    exit /b 1
)

:: Copy to root
copy /y "dist\hqlauncher.exe" "hqlauncher.exe" >nul
if errorlevel 1 (
    echo [FAIL] Failed to copy hqlauncher.exe.
    if exist "%ENTRY_FILE%" del /f "%ENTRY_FILE%"
    exit /b 1
)
echo [OK] hqlauncher.exe created.

:: Clean temporary files
if exist "%ENTRY_FILE%" del /f "%ENTRY_FILE%"
rmdir /s /q "dist"
rmdir /s /q "build"
del /f "hqlauncher.spec"
echo [OK] Cleaned temporary files.

echo.
echo ========================================
echo   Build Complete
echo ========================================
echo.

call :DoRegister
exit /b 0

:DoClean
echo Cleaning build artifacts and temporary files...
echo.

if exist "hqlauncher.exe" (
    del /f "hqlauncher.exe"
    echo [OK] Removed hqlauncher.exe
)

if exist "*.log" (
    del /f *.log
    echo [OK] Removed log files
)

if exist "cut_merge.do" (
    del /f "cut_merge.do"
)

if exist "*.dump" (
    del /f *.dump
    echo [OK] Removed dump files
)

if exist "dist" (
    rmdir /s /q "dist"
    echo [OK] Removed dist/
)

if exist "build" (
    rmdir /s /q "build"
    echo [OK] Removed build/
)

if exist "*.spec" (
    del /f *.spec
    echo [OK] Removed spec files
)

if exist "_build_entry.py" (
    del /f "_build_entry.py"
    echo [OK] Removed _build_entry.py
)

if exist "%APPDATA%\hqlauncher\.no_path_tip" (
    del /f "%APPDATA%\hqlauncher\.no_path_tip" 2>nul
    echo [OK] Removed .no_path_tip flag
)

echo.
echo Done.
exit /b 0

:DoRegister
echo Registering hqlauncher to user PATH...
echo.

:: Project directory (where make.bat resides)
set "PROJECT_DIR=%~dp0"
set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"

:: Proxy directory (same as config.json)
set "PROXY_DIR=%APPDATA%\hqlauncher"
if not exist "%PROXY_DIR%" mkdir "%PROXY_DIR%"

:: Check if hqlauncher.exe exists in project dir
if not exist "%PROJECT_DIR%\hqlauncher.exe" (
    echo [FAIL] hqlauncher.exe not found in project directory.
    echo        Please run 'make build' first.
    exit /b 1
)

:: Remove old proxy bat from previous versions
if exist "%PROXY_DIR%\hqlauncher.bat" del /f "%PROXY_DIR%\hqlauncher.bat" 2>nul

copy /y "%PROJECT_DIR%\hqlauncher.exe" "%PROXY_DIR%\hqlauncher.exe" >nul
if errorlevel 1 (
    echo [FAIL] Failed to copy hqlauncher.exe to proxy directory.
    exit /b 1
)
echo [OK] Copied hqlauncher.exe to proxy directory.

:: Read current user PATH
set "USER_PATH="
for /f "tokens=1,2*" %%a in ('reg query HKCU\Environment /v Path 2^>nul') do (
    if /i "%%a"=="Path" set "USER_PATH=%%c"
)

:: Check if proxy dir is already in PATH
if defined USER_PATH (
    echo ;%USER_PATH%; | find /i ";%PROXY_DIR%;" >nul && (
        echo [OK] Already in user PATH.
        exit /b 0
    )
)

:: Add proxy dir to PATH
if defined USER_PATH (
    setx Path "%USER_PATH%;%PROXY_DIR%" >nul 2>&1
) else (
    setx Path "%PROXY_DIR%" >nul 2>&1
)

if !errorlevel! equ 0 (
    echo [OK] Added to user PATH.
) else (
    echo [WARN] Failed to update PATH automatically.
    echo        Please add the following path to your PATH manually:
    echo        %PROXY_DIR%
)

echo.
echo Please restart your terminal to use 'hqlauncher'.
exit /b 0
