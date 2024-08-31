import json
import os

import requests

# Your Blizzard API credentials
CLIENT_ID = os.getenv("WOW_CLIENT_ID")
CLIENT_SECRET = os.getenv("WOW_CLIENT_SECRET")
REGION = "eu"  # Change to your region if needed
REALM = 1329


# Function to get an OAuth token
def get_access_token():
    url = f"https://{REGION}.battle.net/oauth/token"
    response = requests.post(url, auth=(CLIENT_ID, CLIENT_SECRET), data={"grant_type": "client_credentials"})

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data['access_token']
        print("Access token fetched successfully!")
        return access_token
    else:
        print(f"Failed to fetch access token: {response.status_code}")
        return None


def fetch_wow_token_price(access_token):
    value = 0

    url = f"https://eu.api.blizzard.com/data/wow/token/?namespace=dynamic-eu"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    print(response.status_code)
    value = response.json()
    return value


def fetch_wow_realms(access_token):
    url = f"https://eu.api.blizzard.com/data/wow/token/?namespace=dynamic-eu"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    print(response.status_code)
    value = response.json()
    return value

# Function to fetch auction house data
def fetch_auction(access_token):
    # ravencrest realm is 1329
    auction_url = f"https://{REGION}.api.blizzard.com/data/wow/connected-realm/{REALM}/auctions?namespace=dynamic-eu"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(auction_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("Auction data fetched successfully!")
        return data
    else:
        print(f"Failed to fetch auction data. Code: {response.status_code} reason: {response.reason}")
        return None

def fetch_commodities(access_token):
    commodities_url = f"https://{REGION}.api.blizzard.com/data/wow/auctions/commodities?namespace=dynamic-eu"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(commodities_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("Commodity data fetched successfully!")
        return data
    else:
        print(f"Failed to fetch commodity data. Code: {response.status_code} reason: {response.reason}")
        return None

def search_item_by_name(access_token, item_name):
    search_url = f"https://{REGION}.api.blizzard.com/data/wow/search/item?namespace=static-{REGION}"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "name.en_US": item_name,
        "_pageSize": 1
    }

    response = requests.get(search_url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        if data.get('results'):
            item_id = data['results'][0]['data']['id']
            print(f"Item ID for '{item_name}' found: {item_id}")
            return item_id
        else:
            print(f"No item found for name: {item_name}")
            return None
    else:
        print(f"Failed to search for item. Code: {response.status_code} reason: {response.reason}")
        return None


def get_item_id(item_name):
    access_token = get_access_token()

    search_url = f"https://{REGION}.api.blizzard.com/data/wow/search/item?namespace=static-eu"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"name.en_US": item_name, "_pageSize": 1}

    response = requests.get(search_url, headers=headers, params=params)

    if response.status_code == 200:
        search_data = response.json()
        if search_data['results']:
            item_id = search_data['results'][0]['data']['id']
            return item_id
        else:
            print("Item not found.")
            return None
    else:
        print(f"Failed to search for item. Code: {response.status_code} reason: {response.reason}")
        return None


def fetch_item_prices(item_name, commodities=None):
    item_id = get_item_id(item_name)

    if item_id is None:
        return None

    if commodities is None:
        print("no commodities to search")
        return None

    prices = []

    for auction in commodities['auctions']:
        if auction['item']['id'] == item_id:
            prices.append(auction['unit_price'])

    if not prices:
        print(f"No auctions found for item ID {item_id}.")
        return None

    return prices


def get_commodities():
    path = 'data/commodities.json'

    if os.path.exists(path):
        with open(path, 'r') as file:
            commodities = json.load(file)
            return commodities
    else:
        token = get_access_token()
        commodities = fetch_commodities(token)

        if commodities:
            os.makedirs(os.path.dirname(path), exist_ok=True)

            with open(path, 'w') as file:
                json.dump(commodities, file, ensure_ascii=False)
            return commodities
        else:
            return None


if __name__ == "__main__":

    commodities = get_commodities()
    prices = fetch_item_prices('Bismuth', commodities)
    print("done")