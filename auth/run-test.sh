#!/bin/bash

URL="http://auth:5000"
DELAY=5  # Задержка между запросами (в секундах)

while true; do
    status_code=$(curl --write-out %{http_code} --silent --output /dev/null $URL)

    if [ $status_code -eq 404 ]; then
        break
    fi

    echo "Сервис не доступен"

    sleep $DELAY
done

pytest /app/tests/functional
