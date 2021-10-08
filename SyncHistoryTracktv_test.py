import unittest

from movie import Movie
from show import Show
from netflix_items import NetflixItems


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


class TestShow(unittest.TestCase):
    """
    Test show class
    """

    def testValidShow(self):
        show_name = "this is a show title"
        episode_name = "This is a show name"
        time = "6/28/21"
        show = Show(show_name, episode_name, time)
        self.assertEqual(show.title, episode_name, f"this should be {episode_name}")
        self.assertEqual(show.show_name, show_name, f"this should be {show_name}")
        self.assertEqual(show.type, "episode", "this should be Episode")
        self.assertEqual(show.type2, "episodes", "this should be Episodes")
        self.assertEqual(
            show.watched_at.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "2021-06-28T00:00:00.000Z",
            "this should be 2021-06-28T00:00:00.000Z",
        )


class TestItems(unittest.TestCase):
    def testItems(self):
        items = NetflixItems()
        items.load_csv(open("NetflixViewingHistory_test.csv", newline=""))
        self.assertEqual(len(items.items), 5, "this should be 5")
        self.assertTrue(items.isSeries("Brooklyn Nine-Nine: Season 6: Casecation"))

    def testDuplicateMovies(self):
        items = NetflixItems()
        item_watched = Movie("The Nice Guys", "12/13/17")
        items.load_csv(open("NetflixViewingHistory_test.csv", newline=""))

        item_found = {
            "type": "movie",
            "score": 1000,
            "movie": {
                "title": "The Nice Guys",
                "year": 2016,
                "ids": {"trakt": 187173, "slug": "the-nice-guys-2016", "imdb": "tt3799694", "tmdb": 290250},
            },
        }

        title = item_found["movie"]["title"]

        duplicates = {
            "episodes": {},
            "movies": {
                "The Nice Guys": [
                    {
                        "Imdb_id": "tt3799694",
                        "URL": " https://trakt.tv/movies/187173",
                        "title": "The Nice Guys",
                        "trakt": 187173,
                        "validated": "False",
                        "watched_at": "2017-12-13T00:00:00.000Z",
                        "year": "2016",
                    }
                ]
            },
        }

        items.addDuplicate(item_found, title, item_watched.type, item_watched.type2, item_watched.watched_at)
        self.assertEqual(items._duplicates, duplicates, "duplicates not equal")

    @unittest.skip("no shows duplicated so far")
    def testDuplicateShows(self):
        items = NetflixItems()
        items.load_csv(open("NetflixViewingHistory_test.csv", newline=""))
        item_watched = Show("Brooklyn Nine-Nine", "Casecation", "12/13/17")

        item_found = {
            "type": "episode",
            "score": 956.7663,
            "episode": {
                "season": 6,
                "number": 12,
                "title": "Casecation",
                "ids": {"trakt": 3399236, "tvdb": 7058443, "imdb": "tt8408792", "tmdb": 1738279, "tvrage": ""},
            },
            "show": {
                "title": "Brooklyn Nine-Nine",
                "year": 2013,
                "ids": {
                    "trakt": 48587,
                    "slug": "brooklyn-nine-nine",
                    "tvdb": 269586,
                    "imdb": "tt2467372",
                    "tmdb": 48891,
                    "tvrage": 35774,
                },
            },
        }

        title = item_found["show"]["title"]

        duplicates = {
            "title": "Casecation",
            "year": 2013,
            "Imdb_id": "tt2467372",
            "trakt": "48587",
            "URL": " https://trakt.tv/movies/48587",
            "watched_at": "2017-12-13T00:00:00.000Z",
            "validated": "False",
        }

        items.addDuplicate(item_found, title, item_watched.type, item_watched.type2, item_watched.watched_at)
        self.assertEqual(items._duplicates, duplicates, "duplicates not equal")


if __name__ == "__main__":
    unittest.main()
