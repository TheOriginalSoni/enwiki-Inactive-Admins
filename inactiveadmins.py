#!/usr/bin/env python3

# AdminStatsBot v3.0
# Updated 2023-04-05
# Updated by JamesR
# Rewrite of code to move to python3 with mwclient

# LICENSE: GPL-3.0+
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import time
import datetime
import operator
import MySQLdb
import mwclient
import settings
import os

ua = 'SoniBot (User:Soni).'
site = mwclient.Site('en.wikipedia.org', clients_useragent=ua)
site.login(settings.username, settings.password)
#page = site.pages['User:JamesR/AdminStats']
start_time = datetime.datetime.now()
cnf_path = os.path.join(os.path.dirname(__file__), 'replica.my.cnf')

#conn = MySQLdb.connect(host='enwiki.analytics.db.svc.wikimedia.cloud', db='enwiki_p',
#                       read_default_file='/data/project/adminstats/replica.my.cnf', use_unicode=True)
conn = MySQLdb.connect(host='127.0.0.1', db='enwiki_p',
                       read_default_file=cnf_path, use_unicode=True)
cursor = conn.cursor()

def get_stats(type, action):
    cursor.execute(u'''
        SELECT actor_name, COUNT(log_timestamp)
        FROM logging
        JOIN actor
        ON log_actor = actor_id
        WHERE log_type = "%s"
        AND log_action = "%s"
        GROUP BY actor_name;
    ''' % (type, action))
    return cursor.fetchall()

query_list = [
    {'name': 'Deletions', 'short_name': 'DL','type': 'delete', 'action': 'delete'},
    {'name': 'Undeletions', 'short_name': 'UD','type': 'delete', 'action': 'restore'},
    #{'name': 'Revision deletions', 'short_name': 'RD','type': 'delete', 'action': 'revision'},
    {'name': 'Protections', 'short_name': 'PT','type': 'protect', 'action': 'protect'},
    {'name': 'Unprotections', 'short_name': 'UP','type': 'protect', 'action': 'unprotect'},
    {'name': 'Protection modifications', 'short_name': 'PM','type': 'protect', 'action': 'modify'},
    {'name': 'Blocks', 'short_name': 'BL', 'type': 'block', 'action': 'block'},
    {'name': 'Reblocks', 'short_name': 'RB', 'type': 'block', 'action': 'reblock'},
    {'name': 'Unblocks', 'short_name': 'UB', 'type': 'block', 'action': 'unblock'},
    {'name': 'Block modifications', 'short_name': 'BM','type': 'block', 'action': 'reblock'},
    {'name': 'User renames', 'short_name': 'UR','type': 'renameuser', 'action': 'renameuser'},
    {'name': 'User rights modifications', 'short_name': 'RM','type': 'rights', 'action': 'rights'},
    {'name': 'Whitelistings', 'short_name': 'WL','type': 'gblblock', 'action': 'whitelist'},
    {'name': 'De-whitelistings', 'short_name': 'DW','type': 'gblblock', 'action': 'dwhitelist'},
    {'name': 'Page history merges', 'short_name': 'HM','type': 'merge', 'action': 'merge'},
    {'name': 'Inter-wiki imports', 'short_name': 'IM','type': 'import', 'action': 'interwiki'}
]

adminslist = settings.admins
print(adminslist)

query = {'name': 'Deletions', 'short_name': 'DL', 'type': 'delete', 'action': 'delete'}
stats_query = get_stats(query['type'], query['action'])
query['len'] = len(stats_query)

print(stats_query)
print(query['len'])
print(query)

'''
user_stats = {}

for query in query_list:
    stats_query = get_stats(query['type'], query['action'])
    query['len'] = len(stats_query)
    for row in stats_query:
        user = row[0]
        count = row[1]
        #print(user)
        if user in adminslist:
            print(f"{user} - yes")
        else:
            print(f"{user} - no")
        if user not in user_stats:
            user_stats[user] = {query['name']: count}
        else:
            user_stats[user][query['name']] = count
'''

cursor.close()
conn.close()
