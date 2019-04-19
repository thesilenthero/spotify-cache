import spotipy
from dateparser import parse as dtparse

from .authorization import get_token


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


class PlaylistUpdater(object):

    def __init__(self, playlist_name):
        self.api = spotipy.Spotify(auth=get_token()["access_token"])
        self.playlist = [pl for pl in self.api.current_user_playlists()["items"]
                         if pl["name"].lower() == playlist_name.lower()][0]
        self.user = self.api.current_user()

    def get_playlist_tracks(self):
        results = self.api.user_playlist_tracks(self.user['id'],
                                                self.playlist['id'])
        tracks = results["items"]
        while results["next"]:
            results = self.api.next(results)
            tracks.extend(results["items"])
        return tracks

    def trim_playlist(self, limit=100):
        # remove songs on a first in, first out basis
        return sorted(self.playlist, lambda s: s["added_at"])[:limit]

    def get_uris(self, raw_song_data):
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

    def update_playlist(self, limit=200):

        existing_uris = self.get_uris(self.get_playlist_tracks())

        new_songs = []
        new_songs.extend(self.api.current_user_top_tracks(limit=50, time_range="short_term")["items"])
        new_songs.extend([x["track"] for x in self.api._get("me/player/recently-played", limit=50)["items"]])

        new_uris = [uri for uri in set(self.get_uris(new_songs))
                    if uri not in existing_uris]

        for chunk in chunks(new_uris, 50):
            self.api.user_playlist_add_tracks(self.user["id"], self.playlist["id"], chunk)

        # trim playlist to limit
        playlist_songs = self.get_playlist_tracks()
        songs_to_remove = sorted(playlist_songs, key=lambda p: dtparse(p["added_at"]))[limit:]

        if songs_to_remove:
            for chunk in chunks(songs_to_remove, 50):
                uris_to_remove = self.get_uris(songs_to_remove)
                self.api.user_playlist_remove_all_occurrences_of_tracks(self.user["id"], self.playlist["id"], uris_to_remove)

        print("Updated playlist:\n\n")
        for song in self.get_playlist_tracks():
            print(self.get_artist(song) + " - " + song["track"]["name"])
