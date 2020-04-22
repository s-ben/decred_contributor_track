import datetime
from sqlalchemy import exc, select
from database import Base, engine, session
from classes import *
from functions import *
from config import *
import pickle

# Create tables in db
Base.metadata.create_all(engine)

# ----------- Set session variables ---------------

for user in allRepos:
    print(user)
    for repo in allRepos[user]:
        repo_entry = Repo()
        repo_entry.name = repo
        repo_entry.organization = user
        try:
            session.add(repo_entry)
            session.commit()
        except exc.IntegrityError as err:
            session.rollback()

# ------------- Set event types into db -----------

event_types = ['commit', 'issue', 'pull_request', 'comment', 'review']

for event in event_types:
    event_type = Event_type()
    event_type.event_type = event
    try:
        session.add(event_type)
        session.commit()
    except exc.IntegrityError as err:
        session.rollback()

# --------------Load events from DB into a dictionary------------------------

select_event = select([Event_type])
event_result = session.execute(select_event)

event_dict = {}

for event_rows in event_result:
    event_dict[event_rows['event_type']] = event_rows['id']

# --------------- Fetch all repo from database--------------------------

select_repo = select([Repo])
repo_result = session.execute(select_repo)

# --------- Loop through fetched repos--------------

for repo_row in repo_result:
    repo_name = repo_row['name']
    repo_organization = repo_row['organization']
    repo_id = repo_row['id']
    print("Doing Repo " + repo_name)

    # ----------- Fetch commits repo -----------
    check_limit_wait(token)
    print('fetching commits ...')
    check_limit_wait(token)
    all_commits = get_commits_repo(repo_organization, repo_name, token)
    #Save commits in db
    for commit in all_commits:
        commit_event = Event()
        commit_event.type_id = event_dict['commit']
        commit_event.repo_id = repo_id
        commit_event.github_username = commit['commit']['author']['name']
        commit_event.datetime = datetime.datetime.strptime(commit['commit']['committer']['date'], "%Y-%m-%dT%H:%M:%SZ")
        commit_event.github_url = commit['html_url']  # Note: this is the HTML url (can also do API call)
        commit_event.sha = commit['sha']
        try:
            session.add(commit_event)
            session.commit()
        except exc.IntegrityError as err:
            session.rollback()

    # ----------- Fetch PRs repo -----------
    state = 'all'  # (open, closed, all (default = open))
    check_limit_wait(token)
    print('fetching PRs...')
    all_pull_requests = get_pull_requests_repo(repo_organization, repo_name, state, token)
    # save PRs in db
    for pull_request in all_pull_requests:

        pr = Event()
        pr.type_id = event_dict['pull_request']
        pr.repo_id = repo_id
        pr.github_username = pull_request['user']['login']


        
        pr.datetime = datetime.datetime.strptime(pull_request['updated_at'],
                                                 "%Y-%m-%dT%H:%M:%SZ")  # NOTE: using "created at" (can also do last modified)
        # pr.datetime = datetime.datetime.strptime(pull_request['created_at'],
        #                                          "%Y-%m-%dT%H:%M:%SZ")  # NOTE: using "created at" (can also do last modified)
        pr.github_url = pull_request['html_url']  # Note: this is the HTML url (can also do API call)
        if pull_request['merged_at']:
            pr.merged_at = datetime.datetime.strptime(pull_request['merged_at'],
                                                 "%Y-%m-%dT%H:%M:%SZ")
        pr.state = pull_request['state']
        try:
            session.add(pr)
            session.commit()
        except exc.IntegrityError as err:
            session.rollback()

    # ----------- Fetch Issues repo -----------

    check_limit_wait(token)
    state = 'all'  # (open, closed, all (default = open))
    print('fetching Issues...')
    all_issues = get_issues_repo(repo_organization, repo_name, state, token)
    # save issues in db
    for issue in all_issues:

        issue_event = Event()
        issue_event.type_id = event_dict['issue']
        issue_event.repo_id = repo_id
        issue_event.github_username = issue['user']['login']
        issue_event.datetime = datetime.datetime.strptime(issue['created_at'],
                                                          "%Y-%m-%dT%H:%M:%SZ")  # NOTE: using "created at" (can also do last modified)
        issue_event.github_url = issue['html_url']  # Note: this is the HTML url (can also do API call)
        try:
            session.add(issue_event)
            session.commit()
        except exc.IntegrityError as err:
            session.rollback()

    # ----------- Fetch comments on Issues -----------

    # state = 'all'  # (open, closed, all (default = open))
    check_limit_wait(token)
    print('fetching comments...')
    all_comments = get_comments_repo(repo_organization,repo_name,token)

    # save issues in db
    for comment in all_comments:

        comment_event = Event()
        comment_event.type_id = event_dict['comment']
        comment_event.repo_id = repo_id
        comment_event.github_username = comment['user']['login']
        comment_event.datetime = datetime.datetime.strptime(comment['created_at'] , "%Y-%m-%dT%H:%M:%SZ")  #NOTE: using "created at" (can also do last modified)
        comment_event.github_url = comment['html_url']  # Note: this is the HTML url (can also do API call)

        try:
            session.add(comment_event)
            session.commit()
        except exc.IntegrityError as err:
            session.rollback()

    # ----------- Fetch comments on PRs (reviews) -----------

    # state = 'all'  # (open, closed, all (default = open))
    check_limit_wait(token)
    print('fetching comments PRs (reviews)...')
    all_comments = get_comments_prs_repo(repo_organization,repo_name,token)

    # save issues in db
    for comment in all_comments:

        comment_event = Event()
        comment_event.type_id = event_dict['review']
        comment_event.repo_id = repo_id
        comment_event.github_username = comment['user']['login']
        comment_event.datetime = datetime.datetime.strptime(comment['created_at'] , "%Y-%m-%dT%H:%M:%SZ")  #NOTE: using "created at" (can also do last modified)
        comment_event.github_url = comment['html_url']  # Note: this is the HTML url (can also do API call)
        try:
            session.add(comment_event)
            session.commit()
        except exc.IntegrityError as err:
            session.rollback()
