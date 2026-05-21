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
    echo [OK] SIMHUB_INSTALL_PATH = %SIMHUB_INSTALL_PATH%
    echo.
)

:: ------------------------------------------------------------------
:: Step 2: Check that SimHub DLLs exist (so the build won't fail)
:: ------------------------------------------------------------------
if not exist "%SIMHUB_INSTALL_PATH%\SimHub.Plugins.dll" (
    echo [ERROR] SimHub.Plugins.dll not found at %SIMHUB_INSTALL_PATH%
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

:: Check if nuget.exe is available, otherwise try the built-in MSBuild restore
where nuget.exe >nul 2>&1
if %errorlevel% equ 0 (
    nuget restore "%~dp0User.ActiveBeltTensioner.sln"
) else (
    :: Fallback: try MSBuild restore (VS 2017+)
    where msbuild >nul 2>&1
    if %errorlevel% equ 0 (
        msbuild "%~dp0User.ActiveBeltTensioner.sln" /t:Restore /p:Configuration=Release
    ) else (
        echo [WARN]  Neither nuget.exe nor msbuild found in PATH.
        echo        Trying to restore via dotnet CLI...
        where dotnet >nul 2>&1
        if %errorlevel% equ 0 (
            dotnet restore "%~dp0User.ActiveBeltTensioner.sln"
        ) else (
            echo [ERROR] No package manager found. Install nuget.exe or Visual Studio Build Tools.
            goto :end
        )
    )
)

if %errorlevel% neq 0 (
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

:: Find msbuild - try VS 2022, then VS 2019, then PATH
set "MSBUILD="
if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe" (
    set "MSBUILD=C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe"
)
if exist "C:\Program Files\Microsoft Visual Studio\2022\BuildTools\MSBuild\Current\Bin\MSBuild.exe" (
    set "MSBUILD=C:\Program Files\Microsoft Visual Studio\2022\BuildTools\MSBuild\Current\Bin\MSBuild.exe"
)
if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\MSBuild\Current\Bin\MSBuild.exe" (
    set "MSBUILD=C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\MSBuild\Current\Bin\MSBuild.exe"
)
if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\MSBuild\Current\Bin\MSBuild.exe" (
    set "MSBUILD=C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\MSBuild\Current\Bin\MSBuild.exe"
)

if defined MSBUILD (
    "!MSBUILD!" "%~dp0User.ActiveBeltTensioner.sln" /p:Configuration=Release /p:Platform="Any CPU" /verbosity:minimal
) else (
    :: Try PATH
    where msbuild >nul 2>&1
    if %errorlevel% equ 0 (
        msbuild "%~dp0User.ActiveBeltTensioner.sln" /p:Configuration=Release /p:Platform="Any CPU" /verbosity:minimal
    ) else (
        echo [ERROR] MSBuild not found. Install Visual Studio 2022 Community or Build Tools.
        echo        https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022
        echo        Select ".NET desktop build tools" during installation.
        goto :end
    )
)

if %errorlevel% neq 0 (
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
:: Step 6: Ask to copy to SimHub if post-build didn't run
:: ------------------------------------------------------------------
echo [3/3] Deploying to SimHub...
echo.

set "SIMHUB_DLL=%SIMHUB_INSTALL_PATH%\User.ActiveBeltTensioner.dll"
set "SIMHUB_PDB=%SIMHUB_INSTALL_PATH%\User.ActiveBeltTensioner.pdb"
set "SIMHUB_LANG=%SIMHUB_INSTALL_PATH%\Languages"
set "SOURCE_DLL=%~dp0bin\Release\User.ActiveBeltTensioner.dll"
set "SOURCE_PDB=%~dp0bin\Release\User.ActiveBeltTensioner.pdb"
set "SOURCE_LANG=%~dp0Languages"

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
echo   - Auto-Calibrate (Tuning tab) - consistent feel across all cars
echo   - Auto-Reconnect (Connection tab) - no more blocking popups
echo   - Korean language support
echo   - Game-switching reliability fix
echo.
echo ============================================

:end
echo.
pause
endlocal
