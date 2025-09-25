@echo off
echo 🚀 Setting up CSE-AIML ERP System...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.7+ first.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 16+ first.
    pause
    exit /b 1
)

echo 📦 Installing Python dependencies...
pip install -r requirements.txt

echo 📦 Installing Node.js dependencies...
cd frontend
npm install
cd ..

echo 🗄️ Setting up database...
cd backend
python sample_data.py
cd ..

echo ✅ Setup complete!
echo.
echo To start the application:
echo 1. Start MongoDB (if not already running)
echo 2. Run: start.bat
echo.
echo Or start manually:
echo Backend:  cd backend ^&^& python app.py
echo Frontend: cd frontend ^&^& npm run dev
pause
