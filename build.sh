docker compose pull
docker compose --env-file ./dev.env -f ./remote_files/docker-compose.yml -p bot_test up --build