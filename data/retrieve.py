import sys, argparse, json, requests

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

            csv_content += f"{user['login']}, {user['html_url']}, {user['avatar_url']}\n"
        # print(json.dumps(json_content, indent=2))
    except json.JSONDecodeError:
        print("Failed to parse JSON response:")
        print(content)

    print(csv_content)
    # Save to file
    with open(filename, 'w') as f:
        f.write(csv_content)

API_URL = "https://api.github.com/graphql"
HEADERS = {"Authorization": f"bearer {token}"}

QUERY = """
query($login:String!, $first:Int!, $after:String) {
  user(login:$login) {
    sponsorshipsAsMaintainer(first:$first, after:$after, includePrivate:false) {
      pageInfo { hasNextPage endCursor }
      nodes {
        createdAt
        sponsorEntity {
          __typename
          ... on User { id login name url avatarUrl }
          ... on Organization { id login name url avatarUrl }
        }
        tier {
          name
          monthlyPriceInDollars
          isOneTime
        }
      }
    }
  }
}
"""

def fetch_public_sponsors(login: str, page_size: int = 100):
    sponsors = []
    after = None
    while True:
        variables = {"login": login, "first": page_size, "after": after}
        resp = requests.post(API_URL, json={"query": QUERY, "variables": variables}, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()

        conn = data["data"]["user"]["sponsorshipsAsMaintainer"]
        for node in conn["nodes"]:
            sponsor = node["sponsorEntity"]
            sponsors.append({
                "id": sponsor.get("id"),
                "login": sponsor.get("login"),
                "name": sponsor.get("name"),
                "profile": sponsor.get("url"),
                "avatar_url": sponsor.get("avatarUrl"),
                "tier": node["tier"]["name"] if node["tier"] else None,
                "price_usd": node["tier"]["monthlyPriceInDollars"] if node["tier"] else None,
                "is_one_time": node["tier"]["isOneTime"] if node["tier"] else None,
                "since": node["createdAt"],
            })

        if conn["pageInfo"]["hasNextPage"]:
            after = conn["pageInfo"]["endCursor"]
        else:
            break
    return sponsors

def sponsor_sort_key(s):
    # Monthly sponsors: sort by price_usd descending
    if s["price_usd"]:
        return (-s["price_usd"], 0)
    # One-time sponsors: sort after monthly
    if s["is_one_time"]:
        return (float('inf'), 1)
    # Others: sort last
    return (float('inf'), 2)

def retrieve_sponsors(owner:str, filename:str):
    sponsors = fetch_public_sponsors(owner)
    sponsors.sort(key=sponsor_sort_key)

    csv_content = ''

    for s in sponsors:
       csv_content += f"{s['login']}, {s['profile']}, {s['avatar_url']}\n"

    print(csv_content)
    with open(filename, 'w') as f:
        f.write(csv_content)

retrieve_contributors('ucupumar', 'ucupaint', 'contributors.csv')
retrieve_contributors('ucupumar', 'ucupaint-wiki', 'contributors-wiki.csv')
retrieve_sponsors('ucupumar', 'sponsors.csv')