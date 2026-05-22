@echo off
setlocal enabledelayedexpansion
title SABT Plugin Build ^& Deploy

echo.
echo ============================================
echo   Simple Active Belt Tensioner - Build Tool
echo ============================================
echo.

:: ------------------------------------------------------------------
:: Step 1: Find or set SIMHUB_INSTALL_PATH
:: ------------------------------------------------------------------
if not defined SIMHUB_INSTALL_PATH (
    if exist "C:\Program Files (x86)\SimHub\SimHubWPF.exe" (
        set "SIMHUB_INSTALL_PATH=C:\Program Files (x86)\SimHub"
        echo [INFO] Auto-detected SimHub at: !SIMHUB_INSTALL_PATH!
        echo [INFO] Run this to make it permanent: setx SIMHUB_INSTALL_PATH "!SIMHUB_INSTALL_PATH!"
        echo.
    ) else (
        echo [ERROR] SIMHUB_INSTALL_PATH is not set and SimHub was not found at the default location.
        echo.
        echo Please set it manually before running this script:
        echo    setx SIMHUB_INSTALL_PATH "C:\Your\Path\To\SimHub"
        echo.
        echo Then restart this command prompt and run build.bat again.
        goto :end
    )
) else (
    echo [OK] SIMHUB_INSTALL_PATH = !SIMHUB_INSTALL_PATH!
    echo.
)

:: ------------------------------------------------------------------
:: Step 2: Check that SimHub DLLs exist (so the build won't fail)
:: ------------------------------------------------------------------
if not exist "%SIMHUB_INSTALL_PATH%\SimHub.Plugins.dll" (
    echo [ERROR] SimHub.Plugins.dll not found at !SIMHUB_INSTALL_PATH!
    echo        Is SimHub installed? The plugin references DLLs from this folder.
    goto :end
)
echo [OK] SimHub references found
echo.

:: ------------------------------------------------------------------
:: Step 3: Restore NuGet packages
:: ------------------------------------------------------------------
echo [1/3] Restoring NuGet packages...
echo.

:: Find MSBuild first (same paths as build step) for both restore and build
set "MSBUILD="
if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe" (
    set "MSBUILD=C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe"
)
if exist "C:\Program Files\Microsoft Visual Studio\2022\BuildTools\MSBuild\Current\Bin\MSBuild.exe" (
    set "MSBUILD=C:\Program Files\Microsoft Visual Studio\2022\BuildTools\MSBuild\Current\Bin\MSBuild.exe"
)
if exist "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\MSBuild\Current\Bin\MSBuild.exe" (
    set "MSBUILD=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\MSBuild\Current\Bin\MSBuild.exe"
)
if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\MSBuild\Current\Bin\MSBuild.exe" (
    set "MSBUILD=C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\MSBuild\Current\Bin\MSBuild.exe"
)
if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\MSBuild\Current\Bin\MSBuild.exe" (
    set "MSBUILD=C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\MSBuild\Current\Bin\MSBuild.exe"
)

:: Ensure nuget.exe is available (download if needed)
where nuget.exe >nul 2>&1
if errorlevel 1 (
    if not exist "%~dp0nuget.exe" (
        echo [INFO] Downloading nuget.exe...
        powershell -Command "Invoke-WebRequest -Uri 'https://dist.nuget.org/win-x86-commandline/latest/nuget.exe' -OutFile '%~dp0nuget.exe'" >nul 2>&1
        if not exist "%~dp0nuget.exe" (
            echo [WARN]  Could not download nuget.exe. Trying MSBuild restore instead...
        )
    )
    if exist "%~dp0nuget.exe" (
        set "NUGET=%~dp0nuget.exe"
    )
) else (
    set "NUGET=nuget.exe"
)

if defined NUGET (
    "!NUGET!" restore "%~dp0User.ActiveBeltTensioner.sln"
) else if defined MSBUILD (
    :: Fallback: use discovered MSBuild for restore
    "!MSBUILD!" "%~dp0User.ActiveBeltTensioner.sln" /t:Restore /p:Configuration=Release
) else (
    :: Fallback: try MSBuild on PATH
    where msbuild >nul 2>&1
    if not errorlevel 1 (
        msbuild "%~dp0User.ActiveBeltTensioner.sln" /t:Restore /p:Configuration=Release
    ) else (
        echo [WARN]  Neither nuget.exe nor msbuild found.
        echo        Trying to restore via dotnet CLI...
        where dotnet >nul 2>&1
        if not errorlevel 1 (
            dotnet restore "%~dp0User.ActiveBeltTensioner.sln"
        ) else (
            echo [ERROR] No package manager found. Install nuget.exe or Visual Studio Build Tools.
            goto :end
        )
    )
)

if errorlevel 1 (
    echo.
    echo [ERROR] NuGet restore failed. Check the output above for details.
    goto :end
)
echo [OK] Packages restored
echo.

:: ------------------------------------------------------------------
:: Step 4: Build the plugin in Release mode
:: ------------------------------------------------------------------
echo [2/3] Building plugin (Release)...
echo.

"!MSBUILD!" "%~dp0User.ActiveBeltTensioner.sln" /p:Configuration=Release /p:Platform="Any CPU" /verbosity:minimal

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed. Check the output above for compile errors.
    goto :end
)
echo [OK] Build succeeded
echo.

:: ------------------------------------------------------------------
:: Step 5: Verify the output DLL exists
:: ------------------------------------------------------------------
if not exist "%~dp0bin\Release\User.ActiveBeltTensioner.dll" (
    echo [ERROR] Output DLL not found. The build may have succeeded but output is missing.
    echo        Expected: %~dp0bin\Release\User.ActiveBeltTensioner.dll
    goto :end
)

:: ------------------------------------------------------------------
:: Step 6: Deploy to SimHub
:: ------------------------------------------------------------------
echo [3/3] Deploying to SimHub...
echo.

set "BACKUP_DIR=%~dp0backups"
set "SIMHUB_DLL=%SIMHUB_INSTALL_PATH%\User.ActiveBeltTensioner.dll"
set "SIMHUB_PDB=%SIMHUB_INSTALL_PATH%\User.ActiveBeltTensioner.pdb"
set "SIMHUB_LANG=%SIMHUB_INSTALL_PATH%\Languages"
set "SOURCE_DLL=%~dp0bin\Release\User.ActiveBeltTensioner.dll"
set "SOURCE_PDB=%~dp0bin\Release\User.ActiveBeltTensioner.pdb"
set "SOURCE_LANG=%~dp0Languages"
set "RESTORE=0"

:: Offer to restore a previous backup if one exists
if exist "%BACKUP_DIR%\User.ActiveBeltTensioner.dll" (
    echo.
    echo ============================================
    echo   A previous backup was found:
    echo ============================================
    echo.
    for %%F in ("%BACKUP_DIR%\User.ActiveBeltTensioner.dll") do (
        echo   Date: %%~tF
        echo   Size: %%~zF bytes
    )
    echo.
    choice /C YN /M "        Restore backup instead of deploying new build"
    if not errorlevel 2 (
        set "RESTORE=1"
    )
    echo.
)

if "!RESTORE!"=="1" (
    :: Check if SimHub is running
    tasklist /FI "IMAGENAME eq SimHubWPF.exe" 2>NUL | find /I /N "SimHubWPF.exe" >NUL
    if !errorlevel! equ 0 (
        echo [WARN]  SimHub appears to be running!
        echo        The DLL cannot be replaced while SimHub is open.
        echo.
        choice /C YN /M "        Close SimHub now and continue"
        if errorlevel 2 goto :end
        echo.
        echo        Please close SimHub manually, then press any key to continue...
        pause >nul
        echo.
    )
    echo        Restoring backup...
    copy /Y "%BACKUP_DIR%\User.ActiveBeltTensioner.dll" "%SIMHUB_DLL%" >nul 2>&1
    if !errorlevel! equ 0 (
        echo        [OK] Backup restored to SimHub
    ) else (
        echo        [ERROR] Failed to restore backup.
        goto :end
    )
    if exist "%BACKUP_DIR%\User.ActiveBeltTensioner.pdb" (
        copy /Y "%BACKUP_DIR%\User.ActiveBeltTensioner.pdb" "%SIMHUB_PDB%" >nul 2>&1
    )
    goto :done
)

:: Check if SimHub is running (DLL in use)
tasklist /FI "IMAGENAME eq SimHubWPF.exe" 2>NUL | find /I /N "SimHubWPF.exe" >NUL
if %errorlevel% equ 0 (
    echo [WARN]  SimHub appears to be running!
    echo        The DLL cannot be replaced while SimHub is open.
    echo.
    choice /C YN /M "        Close SimHub now and continue"
    if errorlevel 2 goto :end
    echo.
    echo        Please close SimHub manually, then press any key to continue...
    pause >nul
    echo.
)

:: Back up existing DLL before overwriting
if exist "%SIMHUB_DLL%" (
    if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
    echo        Backing up current DLL...
    copy /Y "%SIMHUB_DLL%" "%BACKUP_DIR%\User.ActiveBeltTensioner.dll" >nul 2>&1
    if exist "%SIMHUB_PDB%" (
        copy /Y "%SIMHUB_PDB%" "%BACKUP_DIR%\User.ActiveBeltTensioner.pdb" >nul 2>&1
    )
    echo        [OK] Current version backed up
)

:: Copy DLL
echo        Copying User.ActiveBeltTensioner.dll ...
copy /Y "%SOURCE_DLL%" "%SIMHUB_DLL%" >nul 2>&1
if %errorlevel% equ 0 (
    echo        [OK] DLL deployed
) else (
    echo        [ERROR] Failed to copy DLL. Check permissions or path.
    goto :end
)

:: Copy PDB (optional, for debugging)
if exist "%SOURCE_PDB%" (
    copy /Y "%SOURCE_PDB%" "%SIMHUB_PDB%" >nul 2>&1
)

:: Copy language files
echo        Copying language files...
xcopy /Y /Q "%SOURCE_LANG%\*.resx" "%SIMHUB_LANG%\" >nul 2>&1
if %errorlevel% equ 0 (
    echo        [OK] Language files deployed
) else (
    echo        [WARN] Could not copy language files (may not affect functionality)
)

:done

:: ------------------------------------------------------------------
:: Done
:: ------------------------------------------------------------------
echo.
echo ============================================
echo   BUILD COMPLETE
echo ============================================
echo.
echo   Plugin deployed to:
echo   %SIMHUB_INSTALL_PATH%
echo.
echo   Language files deployed to:
echo   %SIMHUB_LANG%
echo.
echo   Next steps:
echo   1. Launch SimHub
echo   2. Look for "Simple Active Belt Tensioner" in the left sidebar
echo   3. Check the log window for: SABT: Initialising...
echo   4. If this is a first-time setup, click "Setup Motors"
echo.
echo   New features in this build:
echo   - Massage Chair button (Connection tab) - for fun!
echo   - Test Motor: full torque + visual animation
echo   - Auto-Calibrate v2: rolling window (1s-10s, no config needed)
echo   - Suppress Activation Warning toggle (default ON, Connection tab)
echo   - Tab bar always visible (per-tab scroll, compact graph)
echo   - Smoother motor control (back-EMF info in Smoothing label)
echo   - Slider units: m/s^2 for limits, seconds for reconnect
echo   - Korean + German + French + Italian translations
echo   - Auto-Reconnect after failure (Connection tab)
echo   - Game-switching reliability fix
echo.
echo ============================================

:end
echo.
pause
endlocal
