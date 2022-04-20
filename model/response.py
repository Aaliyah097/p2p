class Response:
    def __init__(self, _status, _description=None, _data=None):
        self.status = _status
        self.description = _description
        self.data = _data
