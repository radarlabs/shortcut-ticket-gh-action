import os
from github import Github
from bs4 import BeautifulSoup
import requests
import json
from markdownify import markdownify

GITHUB_API = 'https://api.github.com'
SHORTCUT_API = 'https://api.app.shortcut.com/api/v3'

github_token = os.environ['GITHUB_TOKEN']
git = Github(github_token)

shortcut_token = os.environ['SHORTCUT_TOKEN']

def html_to_markdown(body):
    description = markdownify(body, strip=['details'])
    return description

def get_alerts(repo_name, alert_type):
    
    repo = git.get_repo(repo_name)
    pulls = repo.get_pulls(state='open', sort='created', base='master')

    dependabots = {}

    for pr in pulls:
        if pr.body and alert_type in pr.body:
            
            dependabots[pr.title] = (pr.number, str(html_to_markdown(pr.body)))

    return dependabots

def _create_story(title, body):
    
    headers = {'Shortcut-Token': shortcut_token, 'Content-Type': 'application/json'}
    data = {'name': title, 'project_id': '5255', 'epic_id': '7311', 'description': body, 'owner_ids': ['60e499c8-6469-421b-b1a5-0ec647212fbe']}
    res = requests.post(SHORTCUT_API + '/stories', data=json.dumps(data), headers=headers)
    story_url = res.json()['app_url']
    if res.status_code != 201:
        print('STATUS_CODE:' + str(res.status_code))
        print('ERROR: ' + str(res.reason))
        return None
    return story_url


def link_story_to_pr(repo_name, pr_num, story_link):
    repo = git.get_repo(repo_name)
    pr = repo.get_pull(pr_num)
    pr.create_issue_comment(body=story_link)

def create_stories(repo_name, dependabots):
    
    tickets = 0
    for title, pr in dependabots.items():
        story_link = _create_story(title, pr[1])
        if story_link:
            tickets += 1
            link_story_to_pr(repo_name, pr[0], story_link)
    
    return tickets

def main():

    repo_name = ''
    if 'GITHUB_REPOSITORY' in os.environ:
        repo_name = os.environ['GITHUB_REPOSITORY']
    else:
        repo_name = 'radarlabs/server'

    alert_type = ''
    if 'ALERT_TYPE' in os.environ:
        alert_type = os.environ['ALERT_TYPE']
    else:
        alert_type = 'dependabot'

    dependabots = get_alerts(repo_name, alert_type)
    tickets = create_stories(repo_name, dependabots)
    print('Total number of tickets created: ' + str(tickets))

if __name__ == "__main__":
    main()
