@echo off
docker compose --env-file ./1.env -f ./remote_files/docker-compose.yml -p bot_test up --build