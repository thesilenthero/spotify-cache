from playlist.main import PlaylistUpdater


if __name__ == "__main__":
    pl = PlaylistUpdater("offline songs")
    pl.update_playlist()
