import webbrowser

import os
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = os.environ["SPOTIFY_APP_ID"]
APP_SECRET = os.environ["SPOTIFY_APP_SECRET"]
REDIRECT_URI = os.environ["REDIRECT_URI"]

CACHE_PATH = os.path.join(os.path.split(__file__)[0], "cached_data/auth_token.json")
SCOPES = " ".join(["user-read-recently-played",
                   "user-top-read",
                   "user-library-modify",
                   "user-library-read",
                   "playlist-read-private",
                   "playlist-modify-private", ])


def authorize_application(token_path, scopes):

    cached_data_path = os.path.join(os.path.split(__file__)[0], 'cached_data')
    if not os.path.isdir(cached_data_path):
        os.mkdir(cached_data_path)

    oauth = SpotifyOAuth(CLIENT_ID, APP_SECRET, REDIRECT_URI,
                         cache_path=token_path, scope=scopes)
    authorization_url = oauth.get_authorize_url()

    webbrowser.open(authorization_url)

    authorization_response = input("Enter the full callback URL: ")
    code = oauth.parse_response_code(authorization_response)
    token = oauth.get_access_token(code)
    print("Authorization was successful!")
    return token


def get_token(token_path="cached_data/auth_token.json"):

    oauth = SpotifyOAuth(CLIENT_ID, APP_SECRET, REDIRECT_URI,
                         cache_path=CACHE_PATH, scope=SCOPES)

    token = oauth.get_cached_token()

    if not token:
        token = authorize_application(CACHE_PATH, SCOPES)

    return token


if __name__ == "__main__":
    authorize_application(CACHE_PATH, SCOPES)
