echo 'Building docker image...'
docker build --no-cache -t github-actions-image .

echo 'Starting docker container...'
docker run --env-file .env github-actions-image