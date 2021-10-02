import unittest

import SyncHistoryTracktv as sh
from movie import Movie
from show import Show


class TestSum(unittest.TestCase):
    """def test_list_int(self):
    data = [1, 2, 3]
    result = sum(data)
    self.assertEqual(result, 6)"""

    pass


class TestMovie(unittest.TestCase):
    """
    Test movie class
    """

    def testValidMovie(self):
        title = "titulo 1"
        time = "6/28/21"
        movie = Movie(title, time)
        self.assertEqual(movie.title, title, f"This should be {title}")
        self.assertEqual(movie.type, "movie", f"This should be movie")
        self.assertEqual(movie.type2, "movies", f"This should be movie")
        self.assertEqual(
            movie.watched_at.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "2021-06-28T00:00:00.000Z",
            "this should be 2021-06-28T00:00:00.000Z",
        )

    def testValidShow(self):
        show_name = "this is a show title"
        episode_name = "This is a show name"
        time = "6/28/21"
        show = Show(show_name, episode_name, time)
        self.assertEqual(show.episode_name, episode_name, f"this should be {episode_name}")
        self.assertEqual(show.show_name, show_name, f"this should be {show_name}")
        self.assertEqual(show.type, "episode", "this should be Episode")
        self.assertEqual(show.type2, "episodes", "this should be Episodes")
        self.assertEqual(
            show.watched_at.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "2021-06-28T00:00:00.000Z",
            "this should be 2021-06-28T00:00:00.000Z",
        )


if __name__ == "__main__":
    unittest.main()
