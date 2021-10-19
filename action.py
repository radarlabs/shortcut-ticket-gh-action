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

def get_dependabot_alerts():
    
    repo = git.get_repo('radarlabs/server')
    pulls = repo.get_pulls(state='open', sort='created', base='master')

    dependabots = {}

    for pr in pulls:
        if pr.body and 'dependabot' in pr.body:
            
            dependabots[pr.title] = (pr.number, str(html_to_markdown(pr.body)))

    return dependabots

def _create_story(title, number, body):
    
    headers = {'Shortcut-Token': shortcut_token, 'Content-Type': 'application/json'}
    data = {'name': title, 'project_id': '5255', 'epic_id': '7311', 'description': body, 'owner_ids': ['60e499c8-6469-421b-b1a5-0ec647212fbe']}
    # data = {'name': title, 'project_id': '5255', 'epic_id': '7311', 'description': body }
    res = requests.post(SHORTCUT_API + '/stories', data=json.dumps(data), headers=headers)
    if res.status_code != 201:
        print('STATUS_CODE:' + str(res.status_code))
        print('ERROR: ' + str(res.reason))
        return False
    return True

def create_stories(dependabots):
    
    tickets = 0
    for title, pr in dependabots.items():
        if _create_story(title, pr[0], pr[1]):
            tickets += 1
    
    return tickets


def main():

    dependabots = get_dependabot_alerts()
    tickets = create_stories(dependabots)
    print('Total number of tickets created: ' + str(tickets))

if __name__ == "__main__":
    main()
