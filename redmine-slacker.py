#!/usr/bin/env python
# coding: utf-8
from bs4 import BeautifulSoup
import os
import urllib.parse
import urllib.request
import yaml

dirpath = os.path.abspath(os.path.dirname(__file__))
conf = yaml.load(open(dirpath + '/conf.yml').read())


def main():
    url = conf['atom_url']
    atom = urllib.request.urlopen(url).read().decode('utf-8')
    soup = BeautifulSoup(atom, 'lxml')
    current_atom_updated_time = soup.find('feed').find('updated').string

    # get last_atom_updated_time
    try:
        f = open(dirpath + '/latest.txt', 'r')
        last_atom_updated_time = f.read().strip()
        f.close()
    except IOError:
        last_atom_updated_time = current_atom_updated_time

    entries = soup.find('feed').find_all('entry')
    for entry in entries:
        if entry.find('updated').string > last_atom_updated_time:
            params = urllib.parse.urlencode({
              'attachements': [
                  {
                      'color': '#d11a1f',
                      'author_name': entry.find('author').find('name').string.encode('utf-8'),
                      'title': entry.find('title').string.encode('utf-8'),
                      'title_link': entry.find('id').string,
                      'text': BeautifulSoup(entry.find('content').string, 'html').get_text()[:40].encode('utf-8'),
                      'footer': 'Redmine_Slacker'
                  }
              ],
              'channel': conf['channel'].encode('utf-8'),
            })
            params = params.encode('ascii')
            slack_url = conf['webhook_url']
            req = urllib.request.Request(slack_url, params, {'Content-type': 'application/x-www-form-urlencoded'})
            urllib.urlopen(req)

    # update latest_atom_update_time
    f = open(dirpath + '/latest.txt', 'w')
    f.write(current_atom_updated_time)
    f.close()


if __name__ == "__main__":
    main()