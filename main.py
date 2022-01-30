from bs4 import BeautifulSoup

import requests
import csv
import re

import pandas as pd

url = "https://gravityfalls.fandom.com/wiki/Transcripts"
response = requests.get(url)

print(response)

# beautifulSoup
data = []
folder = "folder"

# with open(api_response.text as page)
soup = BeautifulSoup(response.text, "html.parser")
# print(soup)


links = []
for link in soup.find_all('a'):
    ref = link.get('href')
    if type(ref) is str and 'Transcript' in ref[-10:] and 'https' not in ref:
        print(ref)
        links.append(ref)

infos_columns = ['episode_number', 'season', 'title', 'writers', 'prod. code', 'url']

episode_infos_list = []
base_url = "https://gravityfalls.fandom.com"

wikitables = soup.find_all('table', id="sortable_table_id_0")
print(len(wikitables))

episode_tables = wikitables[:-2]

for i, table in enumerate(episode_tables):
    season = i + 1
    if season <= 2:
        season = str(season)
    else:
        season = "shorts"

    for row in table.tbody.find_all('tr')[1:]:
        infos = row.find_all('td')
        number = infos[0].text[:-1]
        # print("number:" + number)
        title = infos[2].b.a.text
        # print("title:" + title)
        reference = base_url + infos[2].b.a['href']
        # print("ref:" + reference)
        writers = infos[3].text[:-1]
        prod_code_part = infos[4]
        for sup in prod_code_part.find_all("sup", {'class': 'reference'}):
            sup.decompose()
        code_prod = infos[4].text[:-1]
        # print("writers:" + writers)
        # print("code_prod:" + code_prod)
        episode_infos_list.append([number, season, title, writers, code_prod, reference])

print(episode_infos_list)
data = []
regex_for_list = re.compile(r"""\s*,|\b\s*and\b\s*""")
for episode_info in episode_infos_list:
    print(episode_info[5])
    episode_page_request = requests.get(episode_info[5])
    soup = BeautifulSoup(episode_page_request.text, "html.parser")
    table = soup.find('table', {'class': 'wikitable'})
    for line_index, line in enumerate(table.find_all('tr')):
        character_string = line.find('th').text[:-1]
        if len(character_string) == 0:
            characters = ['scene description']
        else:
            characters = regex_for_list.split(character_string)

        for character in characters:
            sentence = line.td.text[:-1]
            dialogue_line = episode_info
            dialogue_line = dialogue_line + [character] + [sentence]
            escaped_dialogue_line = list(map(lambda x: x.replace("\n", " "),
                                             dialogue_line))  # removing eol because it mess up the csv
            escaped_dialogue_line += [line_index]  # after the map because line_index isn't a string
            data.append(escaped_dialogue_line)

infos_columns = ['episode_number', 'season', 'title', 'writers', 'prod. code', 'url', 'character', 'dialogue_line',
                 'line_index']
episode_infos = pd.DataFrame(columns=infos_columns, data=data)
episode_infos.to_csv('./gravity_falls_transcript.csv', index=False, escapechar='\\', quoting=csv.QUOTE_NONE)
# episode_infos.to_excel('./gravity_falls_transcript.xlsx')
