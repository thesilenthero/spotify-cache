import spotipy
import pickle
import os
from dateparser import parse as dtparse

from .authorization import get_token


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


class PlaylistUpdater(object):

    def __init__(self, playlist_name, cached_data_path=None):
        if cached_data_path is None:
            cached_data_path = os.path.join(os.path.split(__file__)[0], "cached_data")

        self.cached_data_path = cached_data_path
        self.token_data = get_token(os.path.join(self.cached_data_path, "auth_token.json"))
        self.api = spotipy.Spotify(self.token_data["access_token"])

        self.playlist = [pl for pl in self.api.current_user_playlists()["items"]
                         if pl["name"].lower() == playlist_name.lower()][0]
        self.user = self.api.current_user()

    def to_pickle(self, path=None):
        if not path:
            path = os.path.join(self.cached_data_path,
                                self.user['display_name'] + ".pickle")

        with open(path, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def from_pickle(cls, path):
        with open(path, "rb") as f:
            return pickle.load(f)

    def get_playlist_tracks(self, limit=50):
        results = self.api.user_playlist_tracks(self.user["id"],
                                                self.playlist["id"])
        tracks = results["items"]
        while results["next"]:
            results = self.api.next(results)
            tracks.extend(results["items"])
        return tracks

    def _walk(self, key, data):
        try:
            return data[key]
        except KeyError:
            for value in data.values():
                if isinstance(value, dict):
                    return self._walk(key, value)

        raise KeyError

    def get_uris(self, raw_song_data):
        # uris = [self._walk("uri", track) for track in raw_song_data]
        uris = []
        for track in raw_song_data:
            try:
                uris.append(track["track"]["uri"])
            except KeyError:
                uris.append(track["uri"])

        return uris

    def get_artist(self, track):
        try:
            return track["album"]["artists"][0]["name"]
        except KeyError:
            return track["track"]["album"]["artists"][0]["name"]

    def get_top_tracks(self, limit=50, time_range='short_term'):
        results = self.api.current_user_top_tracks(limit=20, time_range=time_range)

        tracks = results["items"]
        while results["next"]:
            results = self.api.next(results)
            for track in results['items']:
                if len(tracks) >= limit:
                    break
                else:
                    tracks.append(track)

        return tracks

    def get_recent_tracks(self, limit=20):
        """Default = 20, max = 50"""
        results = self.api._get("me/player/recently-played", limit=limit)

        tracks = results["items"]
        while results["next"]:
            results = self.api.next(results)
            for track in results['items']:
                if len(tracks) >= limit:
                    break
                else:
                    tracks.append(track)

        return tracks

    def get_songs(self):
        new_songs = []
        new_songs.extend(self.get_recent_tracks())
        new_songs.extend(self.get_top_tracks())

        return new_songs

    def _duplicate_track(self):
        pass
        # return deduplicated_tracks

    def update_playlist(self, limit=200):

        song_uris = self.get_uris(self.get_songs())

        # de-duplicate
        existing_playlist_uris = self.get_uris(self.get_playlist_tracks())

        new_song_uris = list(set([uri for uri in song_uris
                                  if uri not in existing_playlist_uris]))

        for chunk in chunks(new_song_uris, 50):
            self.api.user_playlist_add_tracks(self.user["id"], self.playlist["id"], chunk)

        # # trim playlist to limit
        playlist_songs = self.get_playlist_tracks()
        songs_to_remove = sorted(playlist_songs, key=lambda p: dtparse(p["added_at"]))[limit:]

        if songs_to_remove:
            uris_to_remove = self.get_uris(songs_to_remove)

            for chunk in chunks(songs_to_remove, 50):
                uris_to_remove = self.get_uris(chunk)
                self.api.user_playlist_remove_all_occurrences_of_tracks(self.user["id"], self.playlist["id"], uris_to_remove)

        return self.get_playlist_tracks()
