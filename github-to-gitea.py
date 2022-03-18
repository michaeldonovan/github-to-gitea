#!/usr/bin/env python -B

"""
Based on code by Jan-Piet Mens
https://jpmens.net/2019/04/15/i-mirror-my-github-repositories-to-gitea/
"""

import argparse
import json
import sys
import urllib.parse

import requests
from github import Github


def get_gitea_uid(gitea_session: requests.Session, gitea_url: str) -> int:
    with gitea_session.get(f"{gitea_url}/user") as r:
        r.raise_for_status()
        user = json.loads(r.text)
        return user["id"]


def mirror_repo(
    gitea_session: requests.Session,
    gitea_url: str,
    gitea_uid: int,
    github_user: str,
    github_token: str,
    gh_repo,
) -> None:
    repo_name = gh_repo.full_name.split("/")[1]
    mirror_request = {
        "repo_name": repo_name,
        "description": gh_repo.description or "",
        "clone_addr": gh_repo.clone_url,
        "mirror": True,
        "private": gh_repo.private,
        "uid": gitea_uid,
    }

    if gh_repo.private:
        mirror_request["auth_username"] = github_user
        mirror_request["auth_password"] = github_token

    r = gitea_session.post(
        f"{gitea_url}/repos/migrate", data=json.dumps(mirror_request)
    )

    if r.status_code == 201:  # created
        print("-> Mirror successfully created\n")
    else:
        if r.status_code == 409:  # repository exists
            print("-> ignoring existing mirror\n")
        else:
            r.raise_for_status()


def mirror_all(
    gitea_url: str,
    gitea_token: str,
    github_user: str,
    github_token: str,
    include_forks: bool,
) -> None:
    gitea_session = requests.Session()  # Gitea
    gitea_session.headers.update(
        {
            "Content-type": "application/json",
            "Authorization": f"token {gitea_token}",
        }
    )

    gitea_uid = get_gitea_uid(gitea_session, gitea_url)

    gh = Github(github_token)

    gh_repos = gh.get_user().get_repos()
    gh_repo_count = gh_repos.totalCount
    for i, repo in enumerate(gh_repos):
        print(f"[{i}/{gh_repo_count}] - {repo.full_name}")
        if repo.fork and not include_forks:
            print("-> ignoring forked repo\n")
            continue

        mirror_repo(
            gitea_session,
            gitea_url,
            gitea_uid,
            github_user,
            github_token,
            repo,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates Gitea mirrors for all Github repositories owned by a user"
    )
    parser.add_argument(
        "--gitea-url", help="Gitea instance URL", required=True, type=str
    )
    parser.add_argument(
        "--gitea-token", help="Gitea access token", required=True, type=str
    )
    parser.add_argument(
        "--github-user", help="GitHub username", required=True, type=str
    )
    parser.add_argument(
        "--github-token", help="GitHub access token", required=True, type=str
    )
    parser.add_argument(
        "--include-forks",
        help="Include repositories forked from elsewhere",
        action="store_true",
    )

    args = parser.parse_args()

    gitea_api_url = urllib.parse.urljoin(args.gitea_url, "/api/v1")

    try:
        mirror_all(
            gitea_url=gitea_api_url,
            gitea_token=args.gitea_token,
            github_user=args.github_user,
            github_token=args.github_token,
            include_forks=args.include_forks,
        )
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)
