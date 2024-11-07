import requests
import base64
import urllib.parse

# Yahoo OAuth2 credentials
CLIENT_ID = 'dj0yJmk9MWNqYzFIaVhrSGs4JmQ9WVdrOVpWb3dXVEJWV1VNbWNHbzlNQT09JnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTEz'
CLIENT_SECRET = 'a117ab9505ae9ea5c62d42a1274e84c95a8579ad'
REDIRECT_URI = 'https://localhost:8080'  # Must match the redirect URI registered on Yahoo Developer Network
AUTHORIZE_URL = 'https://api.login.yahoo.com/oauth2/request_auth'
TOKEN_URL = 'https://api.login.yahoo.com/oauth2/get_token'
SEARCH_URL = "https://api.search.yahoo.com/content/v2/search"

# Step 1: Get Authorization Code
def get_authorization_url():
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': 'openid',
        'state': 'random_state_string',
        'nonce': 'random_nonce_string'
    }
    auth_url = f"{AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"
    print(f"Visit this URL to authorize the app: {auth_url}")

# Step 2: Get Access Token
def get_access_token(auth_code):
    headers = {
        'Authorization': f'Basic {base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI,
        'code': auth_code
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data)
    if response.status_code == 200:
        tokens = response.json()
        return tokens['access_token']
    else:
        print("Failed to get access token:", response.json())
        return None

# Step 3: Search Yahoo
def yahoo_search(query, access_token):
    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    params = {
        'q': query,
        'format': 'json'
    }

    response = requests.get(SEARCH_URL, headers=headers, params=params)
    if response.status_code == 200:
        try:
            results = response.json()
            return results
        except ValueError:
            print("Failed to parse JSON response")
            return None
    else:
        print("Failed to retrieve search results:", response.status_code, response.text)
        return None

# Uncomment the following line to get the authorization URL
get_authorization_url()

# Replace with the authorization code obtained from Step 1
# access_token = get_access_token('YOUR_NEW_AUTHORIZATION_CODE_HERE')  # Replace this with the new code
# if access_token:
#     search_results = yahoo_search("what is negative emotions", access_token)
#     print(search_results)  # Uncomment to view search results
