import requests, os, logging, requests, csv, json, sys
from pathlib import Path
from movie import Movie
from show import Show

try:
    from dotenv import load_dotenv
except:
    sys.exit("please run: pip install -r requirements.txt")

basepath = Path()
basedir = str(basepath.cwd())
envars = basepath.cwd() / "SECRETS.env"
load_dotenv(envars)


class NetflixItems:
    _baseurl = "https://api.trakt.tv"
    _final_request = {"movies": [], "episodes": []}
    _duplicates = {"movies": {}, "episodes": {}}

    _headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Tratk importer",
        "Connection": "Keep-Alive",
        "trakt-api-version": "2",
        "trakt-api-key": os.getenv("TRATK_API_KEY"),
        "Authorization": "Bearer " + os.getenv("TOKEN"),
    }

    def __init__(self):
        self.duplicates = {"movies": {}, "episodes": {}}
        self.items = {}

    def load_csv(self, fileName):
        try:
            reader = csv.reader(fileName, delimiter=",")
            next(reader)  # ignore header
            logging.debug(f"loaded csv file {fileName}")
            self.items = dict(reader)
        except IOError as e:
            logging.error(f"failed to load: {fileName}", e)

    def isSeries(self, text) -> bool:
        return text.find(":") > 0

    def search_items(self):
        """
        Search movies or tv shows and find it's trakt id
        """
        global _final_request
        m = {}
        for item_to_search in self.items:

            if self.isSeries(item_to_search):
                pos1 = item_to_search.find(":")
                pos2 = item_to_search[item_to_search.find(":") + 2 :].find(":")
                show_title = item_to_search[:pos1]
                title = item_to_search[pos1 + pos2 + 2 + 2 :]

                item_watched = Show(show_title, title, self.items[item_to_search])

            else:
                title = item_to_search
                item_watched = Movie(item_to_search, self.items[item_to_search])

            try:
                response = requests.get(
                    self._baseurl + "/search/" + item_watched.type + "?query=" + item_watched.title.replace(" ", "%20"),
                    headers=self._headers,
                )
            except Exception as e:
                logging.error("Error in get", e)

            if response:
                json_data = json.loads(response.text)
                i = 0
                item_found_prev = {item_watched.type: {}}
                for item_found in json_data:

                    if item_found[item_watched.type]["title"].lower() == title.lower() and (
                        item_watched.type == "movie" or item_found["show"]["title"] == show_title
                    ):

                        m = {
                            "watched_at": item_watched.watched_at.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                            "title": item_found[item_watched.type]["title"],
                            "ids": {
                                "trakt": item_found[item_watched.type]["ids"]["trakt"],
                                "imdb": item_found[item_watched.type]["ids"]["imdb"],
                            },
                        }

                        if (
                            i != 0
                            and item_found[item_watched.type]["title"].lower()
                            == item_found_prev[item_watched.type]["title"].lower()
                        ):
                            self.addDuplicate(
                                item_found, item_to_search, item_watched.type, item_watched.type2, item_watched.watched_at
                            )

                        item_found_prev = item_found
                        i = i + 1
                else:
                    if m != {} and i == 1:
                        self._final_request[item_watched.type2].append(m)

    def addDuplicate(self, item_found, item_to_search, type, type2, watched_at):
        global _duplicates

        item = {
            "title": item_found[type]["title"],
            "year": str(item_found[type]["year"]),
            "Imdb_id": (item_found[type]["ids"]["imdb"] if item_found[type]["ids"]["imdb"] else "null"),
            "trakt": item_found[type]["ids"]["trakt"],
            "URL": " https://trakt.tv/movies/" + str(item_found[type]["ids"]["trakt"]),
            "watched_at": watched_at.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "validated": "False",
        }

        if item_to_search in self._duplicates[type2]:
            self._duplicates[type2][item_to_search].append(item)
        else:
            self._duplicates[type2][item_to_search] = []
            self._duplicates[type2][item_to_search].append(item)
