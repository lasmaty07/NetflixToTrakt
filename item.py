import datetime


class Item:
    def __init__(self, title, time) -> None:
        self.title = title
        self.watched_at = datetime.datetime.strptime(time, "%m/%d/%y")

    def setIds(self, trakt_id, imdb_id):
        self.trakt_id = trakt_id
        self.imdb_id = imdb_id
