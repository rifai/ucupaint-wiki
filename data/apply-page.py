
content = '''
# Contributors
{contributors}
# Wiki's Contributors
{wiki_contributors}
# Sponsors
'''


contributors = ''
wiki_contributors = ''


with open('contributors.csv', 'r') as f:
	lines = f.readlines()
	for line in lines:
		parts = line.strip().split(', ')
		if len(parts) == 3:
			login, url, pic = parts
			contributors += f'* [{login}]({url})\n'

with open('contributors-wiki.csv', 'r') as f:
	lines = f.readlines()
	for line in lines:
		parts = line.strip().split(', ')
		if len(parts) == 3:
			login, url, pic = parts
			wiki_contributors += f'* [{login}]({url})\n'

content = content.format(contributors=contributors, wiki_contributors=wiki_contributors)

with open('../docs/01.12.contributors.md', 'w') as f:
	f.write(content)