echo 'Building docker image...'
docker build --no-cache -t github-actions-image .

echo 'Starting docker container...'
#export PULL_REQUEST="$( curl -H "Authorization: token $GITHUB_TOKEN"  -H "Accept: application/vnd.github.v3+json" https://api.github.com/repos/radarlabs/server/pulls/3517 )"
docker run --env-file .env -e PULL_REQUEST="$(echo $PULL_REQUEST)" github-actions-image