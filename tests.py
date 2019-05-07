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

    def test_get_uri(self):
        test_data = [
            {'track': {'uri': 'uri1'}},
            {'uri': 'uri2'},
        ]
        correct = ['uri1', 'uri2']

        self.assertEqual(correct, self.plu.get_uris(test_data))

    def test_get_uri_bad_data(self):
        test_data = [
            {'track': {'not_uri_key': 'uri1'}},
        ]

        with self.assertRaises(KeyError):
            self.plu.get_uris(test_data)


if __name__ == '__main__':
    unittest.main()
