docker-compose up --build -d
timeout /t 5 >nul
start http://localhost:8080