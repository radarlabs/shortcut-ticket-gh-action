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

def html_to_markdown(body):
    description = markdownify(body, strip=['details'])
    return description

def get_pr_and_create_ticket(repo_name, project_id, alert_type, pull_request):

    created = False
    if alert_type == 'snyk' or alert_type == 'dependabot':
        # use pr event context and create ticket
        body = pull_request['body']
        title = pull_request['title']
        number = pull_request['number']

        story_link = _create_story(project_id, title, str(html_to_markdown(body)))
        if story_link:
            link_story_to_pr(repo_name, number, story_link)
            created = True

        # check if pr is for remote data refresh
    elif alert_type == 'ip2loc-data-refresh':
        # fetch pr info and create ticket
        repo = git.get_repo(repo_name)
        pr = repo.get_pull(int(pull_request))
        
        # created a alternate title with date so we don't create tickets with same title
        date_str = date.today().strftime('%m-%d-%Y')
        alt_title = pr.title + ' ' + date_str 
        
        story_link = _create_story(project_id, alt_title, str(html_to_markdown(pr.body)))
        if story_link:
            link_story_to_pr(repo_name, pr.number, story_link)
            created = True

    return created
    

def _create_story(project_id, title, body):
    
    headers = {'Shortcut-Token': shortcut_token, 'Content-Type': 'application/json'}
    data = ''

    # project_id: Shortcut project id for Security Ops (5255) or Engineering (5409) projects
    # workflow_state_id: #now (500000006) column, #next(500000008)
    # group_id: Shortcut group id for Engineers (600c97de-b7ac-4730-bed0-c7cb4f80c3a4)
    # epic_id: Vulnerability Remediation (7311)
    # owner_id: Shortcut member id for Joe Kuttickal (60e499c8-6469-421b-b1a5-0ec647212fbe)

    # if ip2loc pr then create a shortcut ticket with state #now in project Engineering
    if 'ip2loc' in title:
        data = {'name': title, 'project_id': project_id, 'description': body, 'story_type': 'chore', 'workflow_state_id': 500000006, 'group_id': '600c97de-b7ac-4730-bed0-c7cb4f80c3a4'}
    # else if it's a dependabot/snyk alert, create a shortcut ticket with state #next in Security Ops project, assign it to Joe Kuttickal and assign it to Vulnerability Remediation
    else:
        data = {'name': title, 'project_id': project_id, 'epic_id': '7311',  'story_type': 'chore', 'description': body, 'workflow_state_id': 500000008, 'group_id': '600c97de-b7ac-4730-bed0-c7cb4f80c3a4', 'owner_ids': ['60e499c8-6469-421b-b1a5-0ec647212fbe']}
    
    story_url = None
    res = None
    while story_url is None:
        res = requests.post(SHORTCUT_API + '/stories', data=json.dumps(data), headers=headers, timeout=(20, 40))
        if res.json()['story_url']:
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

    # For more info about these environment variables
    # check out the README: https://github.com/radarlabs/shortcut-ticket-gh-action/blob/main/README.md 
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
        project_id = '5255' #Project ID for Security Ops

    
    pull_request = ''
    
    # dependabot and snyk will be using the PULL_REQUEST env var
    # and it will contain the pr event json as a string
    if 'PULL_REQUEST' in os.environ:
        pull_request = json.loads(os.environ['PULL_REQUEST'], strict=False)
    # ip2loc will be using PULL_REQUEST_NUMBER env var
    # and it will only contain the pr number
    elif 'PULL_REQUEST_NUMBER' in os.environ:
        pull_request = os.environ['PULL_REQUEST_NUMBER']
    else:
        sys.exit('No pull request context provided!')

    created = get_pr_and_create_ticket(repo_name, project_id, alert_type, pull_request)

    print('Ticket created: ' + str(created))
    
    # https://docs.github.com/en/actions/creating-actions/metadata-syntax-for-github-actions#outputs-for-composite-actions
    print(f"::set-output name=tickets::{created}")

if __name__ == "__main__":
    main()
