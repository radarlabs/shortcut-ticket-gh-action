import os, sys

from requests.api import head
from github import Github
from bs4 import BeautifulSoup
import requests
import json
from datetime import date
from markdownify import markdownify

GITHUB_API = 'https://api.github.com'
SHORTCUT_API = 'https://api.app.shortcut.com/api/v3'

github_token = os.environ['GITHUB_TOKEN']
git = Github(github_token)

shortcut_token = os.environ['SHORTCUT_TOKEN']

def get_stories(project_id, alert_type):
    headers = {'Shortcut-Token': shortcut_token, 'Content-Type': 'application/json'}
    data = { "includes_description": True }
    res = requests.get(SHORTCUT_API + '/projects/{0}/stories'.format(project_id),data=json.dumps(data), headers=headers)
    data = res.json()

    stories = []
    for story in data:
        stories.append(story['name'])
    return stories


def html_to_markdown(body):
    description = markdownify(body, strip=['details'])
    return description

def get_pr_and_create_ticket(repo_name, project_id, alert_type, pull_request):

    stories = get_stories(project_id, alert_type)
    repo = git.get_repo(repo_name)
    created = False
    pr = repo.get_pull(int(pull_request))
    print(pr)
    print(pr.body)
    if pr.body:
        if pr.title not in stories and (alert_type in pr.body or alert_type in pr.title):
            story_link = _create_story(project_id, pr.title, str(html_to_markdown(pr.body)))
            if story_link:
                link_story_to_pr(repo_name, pr.number, story_link)
                created = True

        # check if pr is for remote data refresh
        elif alert_type == 'ip2loc-data-refresh' and 'ip2loc' in pr.title:
            date_str = date.today().strftime('%m-%d-%Y')
            title = pr.title + ' ' + date_str
            if title not in stories:
                story_link = _create_story(project_id, title, str(html_to_markdown(pr.body)))
                if story_link:
                    link_story_to_pr(repo_name, pr.number, story_link)
                    created = True

    return created
    

def _create_story(project_id, title, body):
    
    headers = {'Shortcut-Token': shortcut_token, 'Content-Type': 'application/json'}
    data = ''
    if 'ip2loc' in title:
        data = {'name': title, 'project_id': project_id, 'description': body, "story_type": 'chore', "workflow_state_id": 500000006, 'group_id': "600c97de-b7ac-4730-bed0-c7cb4f80c3a4"}
    else:
        data = {'name': title, 'project_id': project_id, 'epic_id': '7311', 'description': body, "workflow_state_id": 500000008, 'group_id': "600c97de-b7ac-4730-bed0-c7cb4f80c3a4", 'owner_ids': ['60e499c8-6469-421b-b1a5-0ec647212fbe']}
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
    
    project_id = ''
    if 'PROJECT_ID' in os.environ:
        project_id = os.environ['PROJECT_ID']
    else:
        project_id = '5255'

    pull_request = ''
    if 'PULL_REQUEST' in os.environ:
        pull_request = os.environ['PULL_REQUEST']
    else:
        sys.exit('No pull request number provided!')

    created = get_pr_and_create_ticket(repo_name, project_id, alert_type, pull_request)

    print('Ticket created: ' + str(created))
    print(f"::set-output name=tickets::{created}")

if __name__ == "__main__":
    main()
