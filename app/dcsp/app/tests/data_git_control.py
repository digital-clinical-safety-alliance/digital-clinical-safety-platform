"""Data for testing git and Github functionality"""

import app.functions.constants as c
from unittest.mock import call

CREDENTIALS_CHECK_REPO_EXISTS = {
    "github_username_exists": True,
    "github_organisation_exists": True,
    "repo_exists": True,
    "permission": "admin",
}

CREDENTIALS_CHECK_REPO_DOES_NOT_EXIST = {
    "github_username_exists": True,
    "github_organisation_exists": True,
    "repo_exists": False,
    "permission": None,
}

CREDENTIALS_CHECK_USERNAME_BAD = {
    "github_username_exists": False,
    "github_organisation_exists": True,
    "repo_exists": True,
    "permission": None,
}


CREDENTIALS_CHECK_ORGANISATION_BAD = {
    "github_username_exists": True,
    "github_organisation_exists": False,
    "repo_exists": False,
    "permission": None,
}

ORGANISATION_NAME_GOOD = "good_repo_name"
ORGANISATION_NAME_BAD = "bad_repo_name"
REPO_NAME_CURRENT = "test-repo-exists"
REPO_NAME_NEW = "test-repo-new"
REPO_BAD_NAME = "bad_name_repo"
GET_REPOS_RETURN = ["test-repo-exists"]

AVAILABLE_HAZARD_LABELS_FULL = [
    {
        "name": "hazard",
        "description": "A hazard which is logged.",
        "color": "892CBB",
    },
    {
        "name": "new-hazard-for-triage",
        "description": "A new hazard which needs to be triaged for severity and likelihood, scored and assigned.",
        "color": "892CBB",
    },
    {
        "name": "deprecated-hazard",
        "description": "A hazard which is no longer considered relevant.",
        "color": "892CBB",
    },
    {
        "name": "likelihood-very-high",
        "description": "Certain or almost certain; highly likely to occur.",
        "color": "C5D9F1",
    },
    {
        "name": "likelihood-high",
        "description": "Not certain but very possible; reasonably expected to occur in the majority of cases.",
        "color": "C5D9F1",
    },
    {
        "name": "likelihood-medium",
        "description": "Possible.",
        "color": "C5D9F1",
    },
    {
        "name": "likelihood-low",
        "description": "Could occur but in the great majority of occasions will not.",
        "color": "C5D9F1",
    },
    {
        "name": "likelihood-very-low",
        "description": "Negligible or nearly negligible possibility of occurring.",
        "color": "C5D9F1",
    },
    {
        "name": "severity-catastrophic",
        "description": "Death, 2+. Severe injury or lifechanging incapacity, 2+.",
        "color": "D8E4BC",
    },
    {
        "name": "severity-major",
        "description": "Death, 1; Severe injury or life-changing incapacity, 1; Psychological trauma, 2+.",
        "color": "D8E4BC",
    },
    {
        "name": "severity-considerable",
        "description": "Severe injury, 1, severe incapacity, recovery expected; Significant psych. trauma, 2+.",
        "color": "D8E4BC",
    },
    {
        "name": "severity-significant",
        "description": "Minor injury, long term, 1; Significant psych. trauma, 1; Minor inj/psych trauma, 2+.",
        "color": "D8E4BC",
    },
    {
        "name": "severity-minor",
        "description": "Minor injury, short term recovery; minor psychological upset; inconvenience; negligible consequence.",
        "color": "D8E4BC",
    },
    {
        "name": "risk-level-1-acceptable",
        "description": "Acceptable, no further action required",
        "color": "0E8A16",
    },
    {
        "name": "risk-level-2-acceptable",
        "description": "Acceptable if cost of further reduction > benefits, or further risk reduction is impractical",
        "color": "FBCA04",
    },
    {
        "name": "risk-level-3-undesirable",
        "description": "Undesirable level of risk. Attempts should be made to eliminate the hazard or implement controls",
        "color": "D93F0B",
    },
    {
        "name": "risk-level-4-mandatory-risk-elimination",
        "description": "Mandatory elimination of hazard or addition of controls to reduce risk to an acceptable level",
        "color": "ED5D40",
    },
    {
        "name": "risk-level-5-unacceptable",
        "description": "Unacceptable level of risk",
        "color": "B60205",
    },
]


AVAILABLE_HAZARD_LABELS_NAME_ONLY = [
    "hazard",
    "new-hazard-for-triage",
    "deprecated-hazard",
    "likelihood-very-high",
    "likelihood-high",
    "likelihood-medium",
    "likelihood-low",
    "likelihood-very-low",
    "severity-catastrophic",
    "severity-major",
    "severity-considerable",
    "severity-significant",
    "severity-minor",
    "risk-level-1-acceptable",
    "risk-level-2-acceptable",
    "risk-level-3-undesirable",
    "risk-level-4-mandatory-risk-elimination",
    "risk-level-5-unacceptable",
]

ISSUES_LABELS_PATH_BAD = "123123123abc/dd"
ENV_PATH_BAD = "123123123123/abc"

VALUE_BAD = "234123421430909898hhjk324"
EMAIL_BAD = "bad email address"

LABEL_NAME_BAD = "wrong label name"

git_contoller_args = {
    "github_username": "Bob",
    "email": "bob@domain.com",
    "github_organisation": "org",
    "github_repo": "a_repo",
    "github_token": "a_token",
    "repo_path_local": c.REPO_PATH_LOCAL,
    "env_location": c.ENV_PATH_PLACEHOLDERS,
}

CHECK_CREDENTIALS_GET_CALLS = [
    call(
        f"https://api.github.com/users/{ git_contoller_args['github_username'] }",
        auth=(
            git_contoller_args["github_username"],
            git_contoller_args["github_token"],
        ),
        timeout=10,
    ),
    call(
        f"https://api.github.com/users/{ git_contoller_args['github_organisation'] }",
        auth=(
            git_contoller_args["github_organisation"],
            git_contoller_args["github_token"],
        ),
        timeout=10,
    ),
    call(
        f"https://api.github.com/repos/{ git_contoller_args['github_organisation'] }/{ git_contoller_args['github_repo'] }",
        auth=(
            git_contoller_args["github_organisation"],
            git_contoller_args["github_token"],
        ),
        timeout=10,
    ),
]


"""urls = [
    "users",
    "users/" + git_contoller_args["github_organisation"],
    f"repos/{git_contoller_args['github_organisation']}/{git_contoller_args['github_repo']}",
]

CHECK_CREDENTIALS_CALLS = [
    call(
        f"https://api.github.com/{url}",
        auth=(
            git_contoller_args["github_organisation"]
            if "repos" in url
            else git_contoller_args["github_username"],
            git_contoller_args["github_token"],
        ),
    )
    for url in urls
]"""


CHECK_CREDENTIALS_GITHUB_CALL = (
    git_contoller_args["github_username"],
    git_contoller_args["github_token"],
)


CHECK_CREDENTIALS_REPO_CALL = f"{ git_contoller_args['github_organisation'] }/{ git_contoller_args['github_repo'] }"


GET_REPOS = ["repo_1", "repo_2"]

TIME_ERROR_MESSAGE = "Timeout while connecting to GitHub API"
NO_CONNECTION_ERROR_MESSAGE = "No connection available to GitHub API"
