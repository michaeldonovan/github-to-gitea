# github-to-gitea

A python script to create Gitea mirrors for all GitHub repositories owned by a user. Inspired by [this post by Jan-Piet Mens](https://jpmens.net/2019/04/15/i-mirror-my-github-repositories-to-gitea/)

# Usage
```
usage: github-to-gitea.py [-h] --gitea-url GITEA_URL --gitea-token GITEA_TOKEN
                          --github-user GITHUB_USER --github-token GITHUB_TOKEN
                          [--include-forks]

Creates Gitea mirrors for all Github repositories owned by a user

optional arguments:
  -h, --help            show this help message and exit
  --gitea-url GITEA_URL
                        Gitea instance URL
  --gitea-token GITEA_TOKEN
                        Gitea access token
  --github-user GITHUB_USER
                        GitHub username
  --github-token GITHUB_TOKEN
                        GitHub access token
  --include-forks       Include repositories forked from elsewhere
``` 
