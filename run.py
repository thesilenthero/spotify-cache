from playlist.main import PlaylistUpdater


if __name__ == "__main__":
    try:
        pl = PlaylistUpdater("offline songs")
        pl.update_playlist()
        input("\nPress any key to exit...")
    except Exception as e:
        input(e)

