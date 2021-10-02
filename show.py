import datetime


class Show:
    def __init__(self, show_name, episode_name, time) -> None:
        self.show_name = show_name
        self.episode_name = episode_name
        self.watched_at = datetime.datetime.strptime(time, "%m/%d/%y")
        self.type = "episode"
        self.type2 = "episodes"
