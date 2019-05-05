from playlist import PlaylistUpdater


if __name__ == "__main__":
    pl = PlaylistUpdater("offline songs")
    updated_playlist = pl.update_playlist(250)

    print(f"Updated playlist - {len(updated_playlist)} songs:\n\n")
    for song in sorted(updated_playlist, key=lambda s: pl.get_artist(s)):
        print(pl.get_artist(song) + " - " + song["track"]["name"])

    input("\nPress any key to exit...")
