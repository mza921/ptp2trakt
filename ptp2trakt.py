# -*- coding: UTF-8 -*-
import logging
import os
import re
import sys
import config
from trakt import Trakt
from pprint import pprint

config_file = 'config.yml'
# from ruamel.yaml.util import load_yaml_guess_indent
# config, ind, bsi = load_yaml_guess_indent(open(config_file))

config.TraktClient(config_file)
with open(sys.argv[1], 'r', encoding='utf8') as f:
    movie_list = f.read().splitlines()
list_name = sys.argv[2]
title_match = []
title_year_match = []
alias_match = []
alias_year_match = []
no_match = []
for m in movie_list:
    m = m.replace('&amp;', '&')
    title, alias, year = re.match('(?P<title>.*?)\s(?:AKA\s(?P<alias>.*)\s)?\[(?P<year>\d{4})\]', m).groups()
    # Title search
    print(title, year)
    # result = Trakt['search'].query(query=title, media='movie', fields='title, alias', pagination=False)
    result = Trakt['search'].query(query=title, media='movie', fields='title, alias', pagination=True)
    if len(result) == 1:
        # print('Easy match for title %s' % title)
        title_match += result
    elif len(result) > 1:
        # More than one result
        # print("---Multiple results found for title %s, trying year search" % title)
        title_year_result = [x for x in result if x.year == int(year)]
        if len(title_year_result) == 1:
            # print('Match found (title/year) for title %s' % title)
            title_year_match += title_year_result
    elif alias:
        # Try alias
        alias_result = Trakt['search'].query(query=alias, media='movie', fields='title, alias', pagination=False)
        if len(alias_result) == 1:
            # print('Easy match for %s' % title)
            alias_match += result
        elif len(alias_result) > 1:
            # More than one result
            # print("---Multiple results found for alias %s, trying year search" % alias)
            alias_year_result = [x for x in result if x.year == int(year)]
            if len(alias_year_result) == 1:
                # print('Match found (title/year) for alias %s' % alias)
                alias_year_match += alias_year_result
    else:
        # Nothing found
        no_match.append(m)
        print("No match for %s" % title)
all_match = title_match + title_year_match + alias_match + alias_year_match
post = {}
post['movies'] = [{'ids': item.to_dict()['ids']} for item in all_match]
t = Trakt['/users/me/lists'].create(list_name)
t.add(post)