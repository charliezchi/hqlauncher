#Requires -Version 5.1
<#
.SYNOPSIS
    Build script for HqLauncher.
.DESCRIPTION
    Replaces the old make.bat. Provides clean, build, and PATH registration.
    This is a PowerShell script, not GNU Make.
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet("build", "clean", "help", "")]
    [string]$Command = ""
)

$ErrorActionPreference = "Stop"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Definition
$PROXY_DIR = Join-Path $env:APPDATA "hqlauncher"

function Show-Help {
    Write-Host "Usage: .\build.ps1 [command]"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  build    Build hqlauncher.exe using PyInstaller"
    Write-Host "  clean    Remove build artifacts (exe, logs, temp files)"
    Write-Host "  help     Show this help message"
    Write-Host ""
    Write-Host "Default (no command): clean + build + register PATH"
}

function Invoke-Clean {
    Write-Host "Cleaning build artifacts and temporary files..." -ForegroundColor Cyan
    Write-Host ""

    $items = @(
        @{ Path = "hqlauncher.exe"; Type = "file"; Label = "hqlauncher.exe" },
        @{ Path = "*.log"; Type = "glob"; Label = "log files" },
        @{ Path = "*.dump"; Type = "glob"; Label = "dump files" },
        @{ Path = "dist"; Type = "dir"; Label = "dist/" },
        @{ Path = "build"; Type = "dir"; Label = "build/" },
        @{ Path = "*.spec"; Type = "glob"; Label = "spec files" },
        @{ Path = "_build_entry.py"; Type = "file"; Label = "_build_entry.py" },
        @{ Path = (Join-Path $PROXY_DIR ".no_path_tip"); Type = "file"; Label = ".no_path_tip flag" }
    )

    foreach ($item in $items) {
        $fullPath = Join-Path $SCRIPT_DIR $item.Path
        if ($item.Type -eq "glob") {
            $matches = Get-ChildItem -Path $fullPath -ErrorAction SilentlyContinue
            if ($matches) {
                $matches | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
                Write-Host "  [OK] Removed $($item.Label)" -ForegroundColor Green
            }
        }
        elseif ($item.Type -eq "dir") {
            if (Test-Path $fullPath) {
                Remove-Item -Path $fullPath -Recurse -Force -ErrorAction SilentlyContinue
                Write-Host "  [OK] Removed $($item.Label)" -ForegroundColor Green
            }
        }
        else {
            if (Test-Path $fullPath) {
                Remove-Item -Path $fullPath -Force -ErrorAction SilentlyContinue
                Write-Host "  [OK] Removed $($item.Label)" -ForegroundColor Green
            }
        }
    }

    Write-Host ""
    Write-Host "Done." -ForegroundColor Green
}

function Invoke-Build {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Building hqlauncher.exe" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""

    # Check Python
    try {
        $pyVersion = python --version 2>&1
    }
    catch {
        Write-Host "[FAIL] Python is not installed or not in PATH." -ForegroundColor Red
        exit 1
    }

    # Check / Install PyInstaller
    Write-Host "Checking PyInstaller..."
    try {
        $piVersion = python -m PyInstaller --version 2>&1
        Write-Host "PyInstaller $piVersion"
    }
    catch {
        Write-Host "PyInstaller not found. Installing..."
        python -m pip install pyinstaller
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[FAIL] Failed to install PyInstaller." -ForegroundColor Red
            exit 1
        }
    }

    # Create temporary entry point
    Write-Host ""
    Write-Host "Preparing build entry point..."
    $entryFile = Join-Path $SCRIPT_DIR "_build_entry.py"
    @"
from hqlauncher.__main__ import main
main()
"@ | Set-Content -Path $entryFile -Encoding UTF8

    # Clean previous build
    Write-Host "Cleaning previous build artifacts..."
    $cleanItems = @("dist", "build", "hqlauncher.spec", "hqlauncher.exe")
    foreach ($ci in $cleanItems) {
        $cp = Join-Path $SCRIPT_DIR $ci
        if (Test-Path $cp) {
            Remove-Item -Path $cp -Recurse -Force -ErrorAction SilentlyContinue
        }
    }

    # Build
    Write-Host ""
    Write-Host "Building hqlauncher.exe..."
    python -m PyInstaller --onefile --name hqlauncher "$entryFile"
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "[FAIL] Build failed." -ForegroundColor Red
        if (Test-Path $entryFile) { Remove-Item $entryFile -Force }
        exit 1
    }

    # Copy to root
    $src = Join-Path $SCRIPT_DIR "dist\hqlauncher.exe"
    $dst = Join-Path $SCRIPT_DIR "hqlauncher.exe"
    Copy-Item -Path $src -Destination $dst -Force
    if ($LASTEXITCODE -ne 0 -and -not (Test-Path $dst)) {
        Write-Host "[FAIL] Failed to copy hqlauncher.exe." -ForegroundColor Red
        if (Test-Path $entryFile) { Remove-Item $entryFile -Force }
        exit 1
    }
    Write-Host "[OK] hqlauncher.exe created." -ForegroundColor Green

    # Clean temporary files
    if (Test-Path $entryFile) { Remove-Item $entryFile -Force }
    Remove-Item -Path (Join-Path $SCRIPT_DIR "dist") -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path (Join-Path $SCRIPT_DIR "build") -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path (Join-Path $SCRIPT_DIR "hqlauncher.spec") -Force -ErrorAction SilentlyContinue
    Write-Host "[OK] Cleaned temporary files." -ForegroundColor Green

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  Build Complete" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""

    Invoke-Register
}

function Invoke-Register {
    Write-Host "Registering hqlauncher to user PATH..." -ForegroundColor Cyan
    Write-Host ""

    if (-not (Test-Path (Join-Path $SCRIPT_DIR "hqlauncher.exe"))) {
        Write-Host "[FAIL] hqlauncher.exe not found in project directory." -ForegroundColor Red
        Write-Host "       Please run '.\build.ps1 build' first." -ForegroundColor Red
        exit 1
    }

    if (-not (Test-Path $PROXY_DIR)) {
        New-Item -ItemType Directory -Path $PROXY_DIR -Force | Out-Null
    }

    # Remove old proxy bat from previous versions
    $oldBat = Join-Path $PROXY_DIR "hqlauncher.bat"
    if (Test-Path $oldBat) { Remove-Item $oldBat -Force -ErrorAction SilentlyContinue }

    $src = Join-Path $SCRIPT_DIR "hqlauncher.exe"
    $dst = Join-Path $PROXY_DIR "hqlauncher.exe"
    Copy-Item -Path $src -Destination $dst -Force
    Write-Host "[OK] Copied hqlauncher.exe to proxy directory." -ForegroundColor Green

    # Read current user PATH
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")

    # Check if already in PATH
    $pathParts = if ($userPath) { $userPath -split ";" } else { @() }
    if ($pathParts -contains $PROXY_DIR) {
        Write-Host "[OK] Already in user PATH." -ForegroundColor Green
        return
    }

    # Add to PATH
    $newPath = if ($userPath) { "$userPath;$PROXY_DIR" } else { $PROXY_DIR }
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")

    if ($?) {
        Write-Host "[OK] Added to user PATH." -ForegroundColor Green
    }
    else {
        Write-Host "[WARN] Failed to update PATH automatically." -ForegroundColor Yellow
        Write-Host "       Please add the following path to your PATH manually:" -ForegroundColor Yellow
        Write-Host "       $PROXY_DIR" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "Please restart your terminal to use 'hqlauncher'." -ForegroundColor Cyan
}

# Route command
switch ($Command.ToLower()) {
    "" {
        Invoke-Clean
        Invoke-Build
    }
    "build" {
        Invoke-Build
    }
    "clean" {
        Invoke-Clean
    }
    "help" {
        Show-Help
    }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host "Run '.\build.ps1 help' for usage."
        exit 1
    }
}
