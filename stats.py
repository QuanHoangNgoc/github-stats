import os
import re
from datetime import datetime

import matplotlib.pyplot as plt
import requests

token = os.getenv("GITHUB_TOKEN")
username = os.getenv("GH_USERNAME")
headers = {"Authorization": f"token {token}"}

headers = {"Authorization": f"token {token}"}


# ----------------------------------------------------------------------------
# Fetch all repos (public + private)
repos = []
page = 1
while True:
    url = f"https://api.github.com/user/repos?per_page=100&page={page}"
    r = requests.get(url, headers=headers).json()
    if not r:
        break
    repos.extend(r)
    page += 1
    if page >= 10:
        break

# Filter: repos owned by me (not forks)
repos = [
    repo for repo in repos
    if repo["owner"]["login"] == username and not repo["fork"]
]
print(f"Fetched {len(repos)} repositories.")


# ----------------------------------------------------------------------------
# Sort repositories by last update time
repos.sort(key=lambda r: r["pushed_at"])   # ascending
# repo_names = [repo["name"] for repo in repos]


# ----------------------------------------------------------------------------
# Collect stats
stars, forks, commits, views = [], [], [], []
d = 0

for repo in repos:
    d += 1
    print(d, end=" ")
    stars.append(repo.get("stargazers_count", 0))
    forks.append(repo.get("forks_count", 0))

    # Commits count
    commits_url = repo['commits_url'].replace("{/sha}", "")
    commits_info = requests.get(commits_url, headers=headers, params={
                                "per_page": 1}).headers
    if 'Link' in commits_info:
        match = re.search(r'&page=(\d+)>; rel="last"', commits_info['Link'])
        commits.append(int(match.group(1)) if match else 0)
    else:
        commits.append(len(requests.get(commits_url, headers=headers).json()))

    # Views (last 14 days)
    views_url = f"https://api.github.com/repos/{username}/{repo['name']}/traffic/views"
    try:
        views_data = requests.get(views_url, headers=headers).json()
        views.append(views_data.get("count", 0))
    except:
        views.append(0)


# ----------------------------------------------------------------------------
# Plot 4 subplots (2x2 grid)
fig, axs = plt.subplots(2, 2, figsize=(12, 8), sharex=True)

acc_stars = [sum(stars[:i+1]) for i in range(len(stars))]
acc_commits = [sum(commits[:i+1]) for i in range(len(commits))]
acc_forks = [sum(forks[:i+1]) for i in range(len(forks))]
acc_views = [sum(views[:i+1]) for i in range(len(views))]


def plot_with_last(ax, data, color, title):
    ax.plot(data, color=color)
    ax.set_title(title)
    ax.grid(True, linestyle="--", alpha=0.5)
    if data:  # highlight last point
        ax.scatter(len(data)-1, data[-1], color=color, s=20, zorder=2)
        ax.text(len(data)-1, data[-1], f"{data[-1]}",
                ha="left", va="bottom", fontsize=9, color=color)


# Stars
plot_with_last(axs[0, 0], acc_stars, "gold", "Stars")

# Commits
plot_with_last(axs[0, 1], acc_commits, "steelblue", "Commits")

# Forks
plot_with_last(axs[1, 0], acc_forks, "orange", "Forks")

# Views
plot_with_last(axs[1, 1], acc_views, "green", "Views (last 14 days)")

# Common X/Y labels
for ax in axs.flat:
    ax.set_xlabel("Repositories")
    ax.set_ylabel("Count")
    ax.tick_params(axis="x", rotation=45)

# Overall title
plt.suptitle(f"GitHub Repository Stats (Owner)", fontsize=14)
plt.tight_layout(rect=[0, 0, 1, 0.96])

plt.savefig("github_repo_stats_subplots.png", dpi=300)
plt.show()
