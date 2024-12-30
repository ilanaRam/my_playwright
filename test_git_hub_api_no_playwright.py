import json
import requests


# let's create Github token

# initializations
GITHUB_API_TOKEN = "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" # relevant to 7 days only after it I will to go to GitHub and to re create
assert GITHUB_API_TOKEN, "GITHUB_API_TOKEN is not set"

GITHUB_USER = "ilanaRam"
assert GITHUB_USER, "GITHUB_USER_NAME is not set"

HEADERS = {
        "Authorization": f"token {GITHUB_API_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

GIT_TEST_REPO_NAME = "test-repo1"
GIT_HUB_SITE = "https://api.github.com"

# !!!!  In this file I will work without PLAYWRIGHT
# I will work without creating a context (browser) !!!!
# simply by sending REST APIs to a Github site
# while as next step I will add a playwright

def test_create_repo():
    # Repository data (replace with your repo name and settings)
    data = {
        "name": GIT_TEST_REPO_NAME,  # The name of the repository
        "description": "This is a description of my new repo",  # Optional description
        "private": False,  # Set to True if you want the repo to be private
    }

    # Send POST request to create the repository
    resp = requests.post(url=f"{GIT_HUB_SITE}/user/repos",
                         headers=HEADERS,
                         data=json.dumps(data))
    print(f"The response is: {resp}, the response code: {resp.status_code}")

    # Check the response
    try:
        assert resp.status_code, 201
    except:
        print(f"Create repository - Failed !")
    else:
        print("Repository created successfully!")
        print(resp.json())


def test_delete_repo():
    # Send the DELETE request
    resp = requests.delete(url=f"{GIT_HUB_SITE}/repos/{GITHUB_USER}/{GIT_TEST_REPO_NAME}",
                           headers=HEADERS)
    print(f"The response is: {resp}, the response code: {resp.status_code}")

    # Check the response
    try:
        assert resp.status_code, 204  # while deleting the 204 means Success !!!
    except:
        print(f"REST API to delete 'test-repo1' - Failed !")
    else:
        print("REST API to delete 'test-repo1', sent ok!")
        print(resp)


def test_get_all_repos():
    repos = []
    url = f"{GIT_HUB_SITE}/users/{GITHUB_USER}/repos"

    while url:
        resp = requests.get(url=f"{GIT_HUB_SITE}/users/{GITHUB_USER}/repos",
                            headers=HEADERS)
        print(f"The response is: {resp}, the response code: {resp.status_code}")

        if resp.status_code == 200:
            print("REST API to get all repos, sent ok!")
            repos.extend(resp.json())

            # links is a dict
            url = resp.links.get('next', {}).get('url')
        else:
            print(f"Failed to fetch repos")
            break

    if repos:
        for repo in repos:
            print(f"- repo name: {repo['name']}, repo URL: {repo['html_url']}")
    else:
        print(f"{GITHUB_USER} has no repositories.")


def test_report_a_bug():
    data = {"title": "[Bug] report 1",
            "report": "Bug description"}
    new_issue = requests.post(url=f"{GIT_HUB_SITE}/repos/{GITHUB_USER}/{GIT_TEST_REPO_NAME}/issues",
                              headers=HEADERS,
                              data=json.dumps(data)) #json=data
    if new_issue.ok:
        print(f"New issue name: {new_issue.json()}")
    else:
        print(f"Failed to create issue. Status Code: {new_issue.status_code}")
    # check new issue was created ok
    assert new_issue.ok

    # ask to get back all issues
    print(f"Going to get ask for all bugs ever posted to repo, by cmd: {GIT_HUB_SITE}/repos/{GITHUB_USER}/{GIT_TEST_REPO_NAME}/issues")
    issues = requests.get(url=f"{GIT_HUB_SITE}/repos/{GITHUB_USER}/{GIT_TEST_REPO_NAME}/issues",
                          headers=HEADERS)
    if issues.ok:
        issues_response = issues.json()
        print(f"issue: {issues_response}")
        print(f"The number of issues: {len(issues_response)}")

        # filter is a condition that is applied on each item in iterable, if item satisfies the condition then it passes to a list, else it is dropped
        issue = list(filter(lambda issue: issue["title"] == "[Bug] report 1", issues_response))[0]
        print(f"The issue: {issue}")
    else:
        print("Issue failed to be created")


