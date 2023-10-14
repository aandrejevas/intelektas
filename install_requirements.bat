set VENV_NAME=%1
set REQUIREMENTS_FILE=%2

call %VENV_NAME%\Scripts\activate
pip install -r %REQUIREMENTS_FILE%

deactivate
