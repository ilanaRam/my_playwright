import json
import pytest

from collections.abc import Generator
from playwright.sync_api import Playwright, Page, APIRequestContext, expect

# initializations

GITHUB_API_TOKEN = "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" # relevant to 7 days only after it I will to go to GitHub and to re create
assert GITHUB_API_TOKEN, "GITHUB_API_TOKEN is not set"

GITHUB_USER = "ilanaRam"
assert GITHUB_USER, "GITHUB_USER_NAME is not set"

GIT_TEST_REPO_NAME = "test-repo"
GIT_TEST_REPO_NAME1 = "test-repo1"

GIT_HUB_SITE = "https://api.github.com"

# in this File I will access GitHub api with playwright via creation of context (browser)


# this fixture is a function that get parameter and returns parameters, it receives an object of Playwright,
# and by using this Playwright obj it does:  here we ara going to request information from the API
# and it returns a list of type Generator


# scope="session" (=this fixture function will run 1 time only for all tests)
# autouse=True  (=the execution of it is automatic (no need to call it explicitly)
# fixtured func get a param playwright using which it will be able to create context (browser), it returns object context
@pytest.fixture(scope="session",autouse=True)
def api_create_context(playwright: Playwright) -> Generator[APIRequestContext, None, None]:
    # this fixtured func separated into 2 parts
    # part 1 runs before yield: here we define all that we need to be ready before test starts running
    # part 2 runs after yield: here we define all that will run after test finished executing

    headers = {"Accept": "application/vnd.github.v3+json",     # what portion of GIT we are accessing and the file type (which is json)
               "Authorization": f"token {GITHUB_API_TOKEN}"}  # we need a TOKEN to access github api

    # create new context (= instance of the browser)
    request_context = playwright.request.new_context(base_url=GIT_HUB_SITE,
                                                     extra_http_headers=headers)
    yield request_context

    # this part will run after test execution finished - here I ask to kill context (browser)
    request_context.dispose()


@pytest.fixture(scope="session", autouse=True)
def create_test_repo(api_create_context: APIRequestContext)->Generator[None, None, None]:
    # test wishes to create repo in GitHub, do operations, delete repo after test completed (so nothing will be left in GitHub after test finished
    # Define the repository data (customize this as needed)
    repo_data = {
        "name": GIT_TEST_REPO_NAME1,  # Name of the repository
        "description": "This is a description of my new test repo1",  # Optional description
        "private": False,  # Set to True to create a private repository
        "auto_init": True,  # Automatically initialize the repository with a README
    }

    # post creates new resource file to my repo
    new_repo = api_create_context.post(url="https://api.github.com/user/repos",
                                        data=json.dumps(repo_data)) # data
    print(f"New repo name: {new_repo}, status: {new_repo.status}, status_name: {new_repo.status_text}")
    # check if repo was created
    assert new_repo.ok

    yield
    #the repo we created in GitHub, should be deleted
    resp = api_create_context.delete(url=f"/repos/{GITHUB_USER}/{GIT_TEST_REPO_NAME1}/")
    print(f"The response is: {resp}, the response code: {resp.status}")

    # check that repo deleted indeed
    #assert deleted_repo.ok
    try:
        assert resp.status, 204  # while deleting the 204 means Success !!!
    except:
        print(f"REST API to delete {GIT_TEST_REPO_NAME1} - Failed !")
    else:
        print("REST API to delete {GIT_TEST_REPO_NAME1}, sent ok!")
        print(resp)


def test_report_a_bug(api_create_context: APIRequestContext) -> None:
    data = {"title": "[Bug] report 1",
            "report": "Bug description"}
    new_issue = api_create_context.post(url=f"{GIT_HUB_SITE}/repos/{GITHUB_USER}/{GIT_TEST_REPO_NAME1}/issues",
                                         data=data)
    if new_issue.ok:
        print(f"New issue name: {new_issue.json()}")
    else:
        print(f"Failed to create issue. Status Code: {new_issue.status}")
    # check new issue was created ok
    assert new_issue.ok

    # ask to get back all issues
    issues = api_create_context.get(url=f"{GIT_HUB_SITE}/repos/{GITHUB_USER}/{GIT_TEST_REPO_NAME1}/issues")
    assert issues.ok

    if issues.ok:
        issues_response = issues.json()
        print(f"issue: {issues_response}")
        print(f"The number of issues: {len(issues_response)}")

        # filter is a condition that is applied on each item in iterable, if item satisfies the condition then it passes to a list, else it is dropped
        issue = list(filter(lambda issue: issue["title"] == "[Bug] report 1", issues_response))[0]
        print(f"The issue: {issue}")
    else:
        print("Issue failed to be created")