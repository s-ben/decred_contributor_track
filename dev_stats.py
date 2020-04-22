from database import Base, engine, session
import csv
from config import *
from functions import *
from classes import *
import pickle

start_date = datetime.datetime.strptime(start, '%Y-%m-%d')
end_date = datetime.datetime.strptime(end, '%Y-%m-%d')

# Get list of repositories in database
r = session.execute('SELECT * FROM repository_list;')

additions_total = 0
deletions_total = 0
commits_total = 0
active_prs_total = 0
merged_prs_total = 0
repos_total = 0

repos = []
active_prs = []
additions_v = []
deletions_v = []
open_prs_v = []
active_prs_v = []
merged_prs_v = []
commits_v = []

# For each repo, calculate dev stats
for repo in r:

    repos.append(repo["name"])

    # Query commits and calculate # commits, additions/deletions
    check_limit_wait(token) # Check to see if over API rate limit

    # fetch commits
    c = session.query(Event).filter(Event.type_id==1, Event.repo_id==repo["id"], Event.datetime >  start, Event.datetime < end).all()

    additions = 0
    deletions = 0
    commits = 0

    repos_total += 1
    for commit in c:
        # Fetch commit from github from commit hash
        commit = requests.get("https://api.github.com/repos/"+repo["organization"]+"/"+repo["name"]+"/commits/"+commit.sha, auth=(repo["organization"],token))
        additions += commit.json()['stats']['additions']
        deletions += commit.json()['stats']['deletions']
        commits += 1

        print(repo)
        print("additions: " + str(additions))
        print("deletions: " + str(deletions))

    additions_v.append(additions)
    deletions_v.append(deletions)
    commits_v.append(commits)

    commits_total =+ commits
    additions_total =+ additions
    deletions_total =+ deletions

    check_limit_wait(token) # Check to see if over API rate limit

    # Query PRs and calculate # active
    p = session.query(Event).filter(Event.type_id==3, Event.repo_id==repo["id"]).all()

    active_prs = 0
    merged_prs = 0

    for pr in p:
        created_date = pr.datetime


        if (created_date >= start_date and created_date <= end_date):
            active_prs += 1

        # print(str(pr))
        # break
        # if pr.state == 'open' and pr.datetime:
        #     if (created_date >= start_date and created_date <= end_date):
        #         active_prs += 1

        # if pr.state == 'closed' and pr.merged_at:
        #     merged_at = pr.merged_at

        #     if (merged_at >= start_date and merged_at <= end_date):
        #         merged_prs += 1
    # break
    active_prs_total += active_prs
    active_prs_v.append(active_prs)
    merged_prs_total += merged_prs
    merged_prs_v.append(merged_prs)


# Calculate stat totals

i = 0
total_additions = 0
total_deletions = 0
total_active_prs = 0
total_merged_prs = 0
total_commits = 0

for i, repo in enumerate(repos):

    print("repo: "+ repo)
    print("additions: " + str(additions_v[i]))
    print("deletions: " + str(deletions_v[i]))
    print("total changes: " + str(additions_v[i]+deletions_v[i]))
    print("commits master: " + str(commits_v[i]))
    # print("merged PRs: " + str(merged_prs_v[i]))
    print("active PRs: " + str(active_prs_v[i])+"\n")

    total_additions += additions_v[i]
    total_deletions += deletions_v[i]
    # total_merged_prs += merged_prs_v[i]
    total_active_prs += active_prs_v[i]
    total_commits += commits_v[i]

print("total additions (all repos): " + str(total_additions))
print("total deletions (all repos): " + str(total_deletions))
print("total commits (all repos): " + str(total_commits))
# print("total merged PRs (all repos): " + str(total_merged_prs))
print("total active PRs (all repos): " + str(total_active_prs))
print("total repos: " + str(repos_total))
