
class Parser:
    def __init__(self, path_to_file):
        self.path = path_to_file
        self.name = None
        self.sport = None
        self.duration = None
        self.distance = None
        self.date = None
        self.coordinates = []
        self.altitude = []
        self.heart_rate = None

        # run parser
        self._parse_metadata()
        self._parse_coordinates()

    def _parse_metadata(self):
        raise NotImplementedError

    def _parse_coordinates(self):
        raise NotImplementedError
