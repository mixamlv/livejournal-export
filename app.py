import json
import os
import re
import urllib.request

from bs4 import BeautifulSoup


def save_to_dir(parsed_entry):
    folder = re.sub(r'\W+', '', parsed_entry['title'])
    directory = './out/' + folder
    os.makedirs(directory)

    with open(directory + '/body.html', 'w', encoding='utf8') as f:
        f.write(parsed_entry['html'])

    with open(directory + '/meta.json', 'w', encoding='utf8') as outfile:
        json.dump(parsed_entry, outfile, ensure_ascii=False)


def print_tags(url):
    response = urllib.request.urlopen(url).read()
    html = BeautifulSoup(response, 'html.parser')
    tag_list_ul = html.find("ul", class_="ljtaglist")
    for li in tag_list_ul.contents:
        print(li.contents[0].contents[0])


def parse_entry(url):
    print('reading from: ' + url)
    response = urllib.request.urlopen(url).read()
    html = BeautifulSoup(response, 'html.parser')

    tags_div = html.find("div", class_="ljtags")
    tags = []
    if tags_div is not None:
        tags = [k.text for k in tags_div.find_all("a")]
        tags_div.extract()

    parsed_entry = {
        'url': url,
        'title': html.find("div", class_="subject").text.strip(),
        'html': html.find("div", class_="entry_text").prettify(),
        'tags': tags
    }

    return parsed_entry


def read_entries(url):
    entries = {}
    skip = 0
    while True:
        page_entries = parse_page(urllib.request.urlopen(url + '?skip=' + str(skip)).read())
        for page_entry in page_entries:
            entries[page_entry['url']] = page_entry
        skip += 10
        print('skip = ' + str(skip))
        if len(page_entries) == 0:
            break
    return entries


def parse_page(response):
    html = BeautifulSoup(response, 'html.parser')
    entries = html.find_all("div", class_="subject")
    parsed_entries = []
    for div in entries:
        parsed_entries.append(parse_entry(div.contents[0]['href']))
    return parsed_entries


journal_url = "http://mixam-lv.livejournal.com"
tags_path = "/tags"
# print_tags(journal_url+tags)

for entry in read_entries(journal_url).values():
    save_to_dir(entry)
