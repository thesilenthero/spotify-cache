import webbrowser

import os
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = os.environ["SPOTIFY_APP_ID"]
APP_SECRET = os.environ["SPOTIFY_APP_SECRET"]
REDIRECT_URI = os.environ["REDIRECT_URI"]


def get_token():

    cache_path = os.path.join(os.path.split(__file__)[0], r"cached_data\auth_token.json")
    scopes = " ".join(["user-read-recently-played",
                       "user-top-read",
                       "user-library-modify",
                       "user-library-read",
                       "playlist-read-private",
                       "playlist-modify-private", ])

    oauth = SpotifyOAuth(CLIENT_ID, APP_SECRET, REDIRECT_URI,
                         cache_path=cache_path, scope=scopes)

    token = oauth.get_cached_token()

    if not token:
        authorization_url = oauth.get_authorize_url()

        webbrowser.open(authorization_url)

        authorization_response = input("Enter the full callback URL: ")
        code = oauth.parse_response_code(authorization_response)
        token = oauth.get_access_token(code)
        print("Authorization was successful!")

    return token


if __name__ == '__main__':
    get_token()
