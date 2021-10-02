import datetime

from item import Item


class Show(Item):
    type = "episode"
    type2 = "episodes"

    def __init__(self, show_name, episode_name, time) -> None:
        self.show_name = show_name
        self.episode_name = episode_name
        self.watched_at = datetime.datetime.strptime(time, "%m/%d/%y")
