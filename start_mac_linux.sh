docker-compose up --build -d
sleep 5

if [[ "$OSTYPE" == "darwin"* ]]; then
    # MacOS
    open "http://localhost:8080"
else
    # Linux (Ubuntu, etc.)
    xdg-open "http://localhost:8080" 2> /dev/null || echo "Konnte Browser nicht automatisch öffnen. Bitte gehe zu http://localhost:8080"
fi