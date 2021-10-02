import datetime


class Movie:
    def __init__(self, title, time) -> None:
        self.title = title
        self.watched_at = datetime.datetime.strptime(time, "%m/%d/%y")
        self.type = "movie"
        self.type2 = "movies"
