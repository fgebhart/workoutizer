
class Parser:
    def __init__(self, path_to_file):
        self.path = path_to_file
        self.title = None
        self.sport = None
        self.duration = None
        self.distance = None
        self.date = None
        self.coordinates = []
        self.altitude = []

        # run parser
        self.parse_metadata()
        self.parse_coordinates()

    def parse_metadata(self):
        raise NotImplementedError

    def parse_coordinates(self):
        raise NotImplementedError
