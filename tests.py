import unittest
import os

import playlist


class PlaylistUpdaterTests(unittest.TestCase):

    plu = playlist.PlaylistUpdater('offline songs')

    def test_init(self):
        playlist_name = 'Offline Songs'
        plu = playlist.PlaylistUpdater(playlist_name)
        self.assertNotEqual(plu.api, None)
        self.assertNotEqual(plu.token_data, None)
        self.assertEqual(plu.playlist['name'].lower(), playlist_name.lower())

    def test_get_top_tracks(self):
        limit = 37
        result = self.plu.get_top_tracks(limit)
        self.assertEqual(len(result), limit)

    def test_get_recent_tracks(self):
        limit = 37
        result = self.plu.get_recent_tracks(limit)
        self.assertEqual(len(result), limit)

    def test_get_uris(self):
        sample_data =


if __name__ == '__main__':
    unittest.main()
