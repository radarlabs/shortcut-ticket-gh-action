echo 'Building docker image...'
docker build --no-cache -t github-actions-image .

echo 'Starting docker container...'


# use for snyk and dependabot prs because these alerts use pr event context
#export PULL_REQUEST="$( curl -H "Authorization: token $GITHUB_TOKEN"  -H "Accept: application/vnd.github.v3+json" https://api.github.com/repos/radarlabs/server/pulls/3517 )"
#docker run --env-file .env -e PULL_REQUEST="$(echo $PULL_REQUEST)" github-actions-image


# use for ip2loc prs since these prs are triggered by cron/dispatch workflows so it doesn't have pr event context
# and uses pr number from create-pull-request step
docker run --env-file .env github-actions-image