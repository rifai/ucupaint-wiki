import sys
import argparse
import json

import http.client

conn = http.client.HTTPSConnection("api.github.com")
payload = ''

parser = argparse.ArgumentParser()
parser.add_argument('--token', required=True)
args = parser.parse_args()
token = args.token

print("Using token:", token)

headers = {
	'Authorization': f'token {token}',
	'X-GitHub-Api-Version': '2022-11-28',
	'User-Agent': 'ucupaint-wiki-script' 
}      

def retrieve_contributors(owner:str, repo:str, filename:str):

    conn.request("GET", f"/repos/{owner}/{repo}/contributors", payload, headers)
    res = conn.getresponse()

    # check if response is 200 OK
    if res.status != 200:
        print(f"Error: {res.status} {res.reason}")
        sys.exit(1)
    data = res.read()
    content = data.decode("utf-8")

    # Parse JSON content
    csv_content = ''
    try:
        json_content = json.loads(content)
        for user in json_content:
            if user["type"] == "Bot":
                continue

            print("login=", user['login'])
            print("url=", user['html_url'])
            print("pic=", user['avatar_url'])
            csv_content += f"{user['login']}, {user['html_url']}, {user['avatar_url']}\n"
        # print(json.dumps(json_content, indent=2))
    except json.JSONDecodeError:
        print("Failed to parse JSON response:")
        print(content)

    print(csv_content)
    # Save to file
    with open(filename, 'w') as f:
        f.write(csv_content)

retrieve_contributors('ucupumar', 'ucupaint', 'contributors.csv')
retrieve_contributors('ucupumar', 'ucupaint-wiki', 'contributors-wiki.csv')