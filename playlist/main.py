import spotipy
from dateparser import parse as dtparse
from pprint import pprint

from .authorization import get_token


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


class PlaylistUpdater(object):

    def __init__(self, playlist_name, token_path="cached_data/auth_token.json"):
        self.api = spotipy.Spotify(auth=get_token(token_path)["access_token"])
        self.playlist = [pl for pl in self.api.current_user_playlists()["items"]
                         if pl["name"].lower() == playlist_name.lower()][0]
        self.user = self.api.current_user()

    def get_playlist_tracks(self):
        results = self.api.user_playlist_tracks(self.user["id"],
                                                self.playlist["id"])
        tracks = results["items"]
        while results["next"]:
            results = self.api.next(results)
            tracks.extend(results["items"])
        return tracks

    def _walk(self, key, data):
        print(data)
        try:
            return data[key]
        except KeyError:
            for value in data.values():
                if isinstance(value, dict):
                    return self._walk(key, value)

    def get_uris(self, raw_song_data):
        uris = [self._walk("uri", track) for track in raw_song_data]
        # for track in raw_song_data:
        #     try:
        #         uris.append(track["track"]["uri"])
        #     except KeyError:
        #         uris.append(track["uri"])

        return uris

    def get_artist(self, track):
        try:
            return track["album"]["artists"][0]["name"]
        except KeyError:
            return track["track"]["album"]["artists"][0]["name"]

    def get_songs(self):
        new_songs = []
        new_songs.extend(self.api.current_user_top_tracks(limit=50, time_range="short_term")["items"])
        new_songs.extend([x["track"] for x in self.api._get("me/player/recently-played", limit=50)["items"]])
        return new_songs

    def update_playlist(self, limit=200):

        for chunk in chunks(new_songs, 50):
            uris = self.get_uris(chunk)
            self.api.user_playlist_add_tracks(self.user["id"], self.playlist["id"], uris)

        all_songs = sorted(self.get_playlist_tracks(), key=lambda p: dtparse(p['added_at']))

        uris_to_remove = all_uris[limit:]

        if uris_to_remove:
            for chunk in chunks(uris_to_remove, 50):
                self.api.user_playlist_remove_all_occurrences_of_tracks(self.user["id"], self.playlist["id"], chunk)

        return self.get_playlist_tracks()
