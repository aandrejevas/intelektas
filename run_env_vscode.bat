@echo off

cd /D "%~dp0"

set VENV_NAME=venv
set REQUIREMENTS_FILE=requirements.txt

if not exist %VENV_NAME%\Scripts\activate (
    echo =================================
    echo Creating a virtual environment...
    echo =================================
    python -m venv %VENV_NAME%
)

echo =============================================================
echo Activating virtual environment and installing Python packages
echo =============================================================
call install_requirements.bat %VENV_NAME% %REQUIREMENTS_FILE%

set /p choice=Do you want to launch GROBID service needed to extract figures/tables (y/n):
if "%choice%"=="y" (
    echo =======================================================
    echo Starting GROBID service. Do not close the new terminal
    echo =======================================================
	start cmd /k "bash serve_grobid_modified.sh"
) else if "%choice%"=="n" (
    rem Do nothing
) else (
    echo Invalid choice. Please enter 'y' or 'n'.
)

echo ==================================================================
echo Opening VS Code workspace. Terminal can be closed after it starts.
echo ==================================================================
code intelektas.code-workspace

exit