import webbrowser

import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint

CLIENT_ID = os.environ["SPOTIFY_APP_ID"]
APP_SECRET = os.environ["SPOTIFY_APP_SECRET"]
REDIRECT_URI = os.environ["REDIRECT_URI"]


def get_token():

    cache_path = os.path.join(os.path.split(__file__)[0], "auth_token.json")
    scopes = " ".join(["user-read-recently-played",
                       "user-top-read",
                       "user-library-modify",
                       "user-library-read",
                       "playlist-read-private",
                       "playlist-modify-public",
                       "playlist-modify-private",
                       "playlist-read-collaborative", ])

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


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def update_playlist():

    token = get_token()

    spotify = spotipy.Spotify(auth=token["access_token"])

    playlists = spotify.current_user_playlists()["items"]
    playlist = [pl for pl in playlists if pl["name"].lower() == "offline songs"][0]
    user = spotify.current_user()

    songs_raw = []

    songs_raw.extend(spotify.current_user_top_tracks(limit=50, time_range="short_term")["items"])
    songs_raw.extend(spotify.current_user_top_tracks(limit=50, time_range="medium_term")["items"])
    recently_played = spotify._get("me/player/recently-played", limit=50)["items"]
    songs_raw.extend([x["track"] for x in recently_played])

    def artist_key(track):
        return track["album"]["artists"][0]["name"]

    uris = list(set(track["uri"] for track in sorted(songs_raw, key=artist_key)))
    song_info = list(set([track["album"]["artists"][0]["name"] + " - " + track["name"] for
                          track in sorted(songs_raw, key=artist_key)]))

    for i, chunk in enumerate(chunks(uris, 50)):
        if i == 0:
            spotify.user_playlist_replace_tracks(user["id"], playlist["id"], chunk)
        else:
            spotify.user_playlist_add_tracks(user["id"], playlist["id"], chunk)

    print(f"Added {len(song_info)} to {playlist["name"]} playlist:\n")
    for song in song_info:
        print(song)
    input("\nPress enter to exit")


if __name__ == "__main__":
    try:
        update_playlist()
    except Exception as e:
        input(e)
