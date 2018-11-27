from functions import *
import sqlite3
from pathlib import Path
from datetime import datetime

db_file = Path('database.db')
token = 'FILLTHIS!!!!!!!!!!!!!!!'
username='decred'


if not db_file.is_file():
    first_time = True
    conn = sqlite3.connect('database.db')
    conn.execute('''CREATE TABLE contributors
             (ID INTEGER PRIMARY KEY     AUTOINCREMENT,
             LOGIN           TEXT    NOT NULL,
             REPO           TEXT    NOT NULL,
             FIRSTSEEN           DATE    NOT NULL)''')
    conn.close()
else:
    first_time = False



list_of_repos=get_all_repo(username,token)




conn = sqlite3.connect('database.db')
cursor = conn.cursor()

for repo in list_of_repos:
    contributors = (get_all_contributors(username, repo,token))
    for c in contributors:
        cursor.execute('''SELECT ID FROM contributors WHERE LOGIN=? AND REPO=?''', (c,repo))
        if not cursor.fetchone():
            if first_time:
                date_value = "UNKNOWN"
            else:
                date_value = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
            cursor.execute('''INSERT INTO contributors(LOGIN, REPO, FIRSTSEEN)
                          VALUES(?,?,?)''', (c,repo,date_value))

conn.commit()
conn.close()
