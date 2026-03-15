@echo off
cd /d "%~dp0"

echo Installing required packages...
pip install -r requirements.txt -q

echo.
echo Starting the Animal Words Game...
echo Open your browser at http://localhost:8501
echo.
streamlit run app.py
pause
