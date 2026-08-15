@echo off
:: =============================================================================
:: build.bat — Reproducible Windows build script for FourBarSimulator v2.0
::
:: Usage:
::   build.bat
::
:: Prerequisites (run once):
::   pip install pyinstaller
::   pip install -r requirements.txt
::
:: Output:
::   dist\FourBarSimulator\            <- runnable application folder
::   FourBarSimulator_v2.0_Windows.zip <- distribution ZIP
:: =============================================================================

setlocal EnableDelayedExpansion

echo.
echo ============================================================
echo  Four-Bar Kinematic Chain Simulator
echo  Version 2.0 — Windows Build Script
echo ============================================================
echo.

:: ---------------------------------------------------------------------------
:: Verify prerequisites
:: ---------------------------------------------------------------------------
where pyinstaller >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] PyInstaller not found.
    echo         Install it with:  pip install pyinstaller
    echo.
    exit /b 1
)

where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python not found on PATH.
    echo.
    exit /b 1
)

if not exist "FourBarSimulator.spec" (
    echo [ERROR] FourBarSimulator.spec not found.
    echo         Run this script from the project root directory.
    echo.
    exit /b 1
)

if not exist "version_info.txt" (
    echo [ERROR] version_info.txt not found.
    echo.
    exit /b 1
)

:: ---------------------------------------------------------------------------
:: Step 1 — Clean previous build output
:: ---------------------------------------------------------------------------
echo [1/5] Cleaning previous build artefacts...

if exist build\   rmdir /s /q build
if exist dist\    rmdir /s /q dist
if exist FourBarSimulator_v2.0_Windows.zip del /q FourBarSimulator_v2.0_Windows.zip

:: Remove __pycache__ from source tree (skip venv / .venv)
for /d /r . %%D in (__pycache__) do (
    if exist "%%D" (
        echo %%D | findstr /i "venv" >nul 2>&1 || rmdir /s /q "%%D"
    )
)

:: Remove stale compiled Python files from source tree
del /s /q *.pyc >nul 2>&1
del /s /q *.pyo >nul 2>&1

echo     Done.
echo.

:: ---------------------------------------------------------------------------
:: Step 2 — Run PyInstaller
::   --clean     : clear PyInstaller's own cache before building
::   --noconfirm : overwrite dist\ without interactive prompt
:: ---------------------------------------------------------------------------
echo [2/5] Running PyInstaller (this may take a few minutes)...
echo.

pyinstaller --clean --noconfirm FourBarSimulator.spec

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] PyInstaller failed. See output above for details.
    echo.
    exit /b 1
)

echo.

:: ---------------------------------------------------------------------------
:: Step 3 — Verify the EXE was actually produced
:: ---------------------------------------------------------------------------
echo [3/5] Verifying build output...

if not exist "dist\FourBarSimulator\FourBarSimulator.exe" (
    echo [ERROR] FourBarSimulator.exe not found in dist\FourBarSimulator\.
    echo         The build may have silently failed.
    echo.
    exit /b 1
)

echo     FourBarSimulator.exe found. OK.
echo.

:: ---------------------------------------------------------------------------
:: Step 4 — Post-build cleanup inside dist\
::   Removes __pycache__ and stray .pyc files that PyInstaller may leave.
::   Does NOT remove DLLs, Qt plugins, or any runtime-required files.
:: ---------------------------------------------------------------------------
echo [4/5] Cleaning dist folder (removing __pycache__ and .pyc only)...

for /d /r dist\ %%D in (__pycache__) do (
    if exist "%%D" rmdir /s /q "%%D"
)

:: .pyc files inside dist\_internal are harmless but tidy them away
for /r dist\ %%F in (*.pyc) do del /q "%%F" >nul 2>&1
for /r dist\ %%F in (*.pyo) do del /q "%%F" >nul 2>&1

echo     Done.
echo.

:: ---------------------------------------------------------------------------
:: Step 5 — Create the distribution ZIP
::   PowerShell's Compress-Archive is available on Windows 10+/11 without
::   any additional tools.
:: ---------------------------------------------------------------------------
echo [5/5] Creating distribution ZIP...

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "Compress-Archive -Path 'dist\FourBarSimulator' -DestinationPath 'FourBarSimulator_v2.0_Windows.zip' -Force"

if %ERRORLEVEL% neq 0 (
    echo [WARNING] ZIP creation failed. The dist\FourBarSimulator\ folder is
    echo           still complete and can be zipped manually.
    echo.
) else (
    echo     FourBarSimulator_v2.0_Windows.zip created. OK.
    echo.
)

:: ---------------------------------------------------------------------------
:: Success summary
:: ---------------------------------------------------------------------------
echo ============================================================
echo  BUILD SUCCEEDED
echo.
echo  Application folder : dist\FourBarSimulator\
echo  Distribution ZIP   : FourBarSimulator_v2.0_Windows.zip
echo.
echo  Distribute the ZIP to your faculty and friends.
echo  Recipients unzip and run FourBarSimulator.exe directly —
echo  no Python installation required.
echo ============================================================
echo.

endlocal
