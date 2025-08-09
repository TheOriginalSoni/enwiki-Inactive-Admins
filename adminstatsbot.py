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

ua = 'SoniBot (User:Soni).'
site = mwclient.Site('en.wikipedia.org', clients_useragent=ua)
site.login(settings.username, settings.password)
#page = site.pages['User:JamesR/AdminStats']
start_time = datetime.datetime.now()

conn = MySQLdb.connect(host='enwiki.analytics.db.svc.wikimedia.cloud', db='enwiki_p',
                       read_default_file='/data/project/adminstats/replica.my.cnf', use_unicode=True)
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
    {'name': 'Deletions', 'short_name': 'DL',
        'type': 'delete', 'action': 'delete'},
    {'name': 'Undeletions', 'short_name': 'UD',
        'type': 'delete', 'action': 'restore'},
    {'name': 'Revision deletions', 'short_name': 'RD',
        'type': 'delete', 'action': 'revision'},
    {'name': 'Protections', 'short_name': 'PT',
        'type': 'protect', 'action': 'protect'},
    {'name': 'Unprotections', 'short_name': 'UP',
        'type': 'protect', 'action': 'unprotect'},
    {'name': 'Protection modifications', 'short_name': 'PM',
        'type': 'protect', 'action': 'modify'},
    {'name': 'Blocks', 'short_name': 'BL', 'type': 'block', 'action': 'block'},
    {'name': 'Unblocks', 'short_name': 'UB', 'type': 'block', 'action': 'unblock'},
    {'name': 'Block modifications', 'short_name': 'BM',
        'type': 'block', 'action': 'reblock'},
    {'name': 'User renames', 'short_name': 'UR',
        'type': 'renameuser', 'action': 'renameuser'},
    {'name': 'User rights modifications', 'short_name': 'RM',
        'type': 'rights', 'action': 'rights'},
    {'name': 'Whitelistings', 'short_name': 'WL',
        'type': 'gblblock', 'action': 'whitelist'},
    {'name': 'De-whitelistings', 'short_name': 'DW',
        'type': 'gblblock', 'action': 'dwhitelist'},
    {'name': 'Page history merges', 'short_name': 'HM',
        'type': 'merge', 'action': 'merge'},
    {'name': 'Inter-wiki imports', 'short_name': 'IM',
        'type': 'import', 'action': 'interwiki'}
]
user_stats = {}

for query in query_list:
    stats_query = get_stats(query['type'], query['action'])
    query['len'] = len(stats_query)
    for row in stats_query:
        user = row[0]
        count = row[1]
        if user not in user_stats:
            user_stats[user] = {query['name']: count}
        else:
            user_stats[user][query['name']] = count

output = u''

report_template = u'{{User:JamesR/AdminStats/header}}\n%s'

table_template = u'''
<div class="NavFrame collapsed" style="text-align:left">
  <div class="NavHead" style="font-size: 10pt;">&nbsp;%s</div>
  <div class="NavContent">
<div style="text-align: left;">
{| class="wikitable sortable" style="width:23em;"
|- style="white-space:nowrap;"
! No.
! User
! Count
|-
%s
|}
</div>\n
</div>\n
</div>\n
</div>\n
'''

for query in query_list:
    stat_dict = {}
    for user, stats in user_stats.items():
        if query['name'] in stats:
            stat_dict[user] = stats[query['name']]
    stats = sorted(stat_dict.items(),
                   key=operator.itemgetter(1), reverse=True)[0:100]
    rows = []
    i = 1
    for user, count in stats:
        user_str = user.decode() if isinstance(user, bytes) else user
        count_str = count.decode() if isinstance(count, bytes) else count
        rows.append(u'''|| %d || %s || %s\n|-''' % (i, user_str, count_str))
        i += 1
    output += table_template % (query['name'], '\n'.join(rows))
    if query['len'] > 100:
        output += ""


master_table_template = u'''
<div class="NavFrame collapsed" style="text-align:left">
  <div class="NavHead" style="font-size: 10pt;">&nbsp;All Totals</div>
  <div class="NavContent">
<div style="text-align: left;">
Hover over the abbreviations to see the full action name.

{| class="wikitable sortable" style="width:100%%; margin:auto;"
|- style="white-space:nowrap;"
! No.
! User
%s
! Total
|-
%s class="sortbottom"
! colspan="2" | Totals
%s
|}\n
</div>\n
</div>\n
</div>\n
[[Category:Wikipedia statistics]]
'''

new_query_list = []

for query in query_list:
    if query['len'] > 100:
        new_query_list.append(query)

query_list = new_query_list

rows = []
totals = dict([(query['name'], 0) for query in query_list])
totals['total'] = 0
i = 1
user_stats_sorted = sorted(user_stats.items(), key=operator.itemgetter(0))
for user, stats in user_stats_sorted:
    row = []
    total = 0
    row.append(str(i))
    row.append(user)
    for query in query_list:
        if query['name'] in stats:
            row.append(str(stats[query['name']]))
            total += stats[query['name']]
            totals[query['name']] += stats[query['name']]
            totals['total'] += stats[query['name']]
        else:
            row.append('0')
    row.append(str(total))
    rows.append('|| %s \n|-' % (' || '.join([item.decode() if isinstance(item, bytes) else item for item in row])))
    i += 1

output += master_table_template % (
    '\n'.join(['! <span title="%s">%s</span>' %
              (query['name'], query['short_name']) for query in query_list]),
    '\n'.join(rows),
    '\n'.join([u'! style="text-align:left;" | %d' % totals[query['name']]
              for query in query_list]) + u'\n! style="text-align:left;" | %d' % totals['total']
)

end_time = datetime.datetime.now()
output += f'\n\nQuery started at: {start_time}\nQuery ended at: {end_time}\n'

final_output = report_template % (output)
final_output = final_output.encode('utf-8')
#page.edit(final_output, summary='Updating statistics (BOT).', bot=True)
print(final_output)

cursor.close()
conn.close()