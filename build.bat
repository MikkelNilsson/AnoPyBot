@echo off
docker compose --env-file ./.env -f ./remote_files/docker-compose.yml -p bot_test up --build