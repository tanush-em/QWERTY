@echo off
echo 🚀 Starting CSE-AIML ERP System...

echo 🔧 Starting Flask backend...
start "Backend" cmd /k "cd backend && python app.py"

timeout /t 3 /nobreak >nul

echo 🎨 Starting Next.js frontend...
start "Frontend" cmd /k "cd frontend && npm run dev"

echo ✅ Both servers are starting...
echo.
echo 🌐 Frontend: http://localhost:3002
echo 🔧 Backend:  http://localhost:5000
echo.
echo Press any key to exit
pause >nul
