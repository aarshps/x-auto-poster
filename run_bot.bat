@echo off
REM Batch script to run the X Auto-Poster Bot with virtual environment on Windows
REM Usage: run_bot.bat

echo Activating virtual environment and starting X Auto-Poster Bot...

REM Check if venv exists
if not exist "venv" (
    echo Error: Virtual environment not found.
    echo Run "python setup_venv.py" first to create the virtual environment.
    exit /b 1
)

REM Activate the virtual environment and run the bot
call venv\Scripts\activate.bat
python src\twitter_bot\main.py