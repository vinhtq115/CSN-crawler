class Error(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class InvalidQualityError(Error):
    def __init__(self, quality):
        super().__init__(f'Invalid quality "{quality}". Supported: 0 (FLAC), 1 (M4A 500kbps), 2 (MP3 320kbps), 3 (MP3 128kbps), 4 (M4A 32kbps).')

class NetworkError(Error):
    def __init__(self):
        super().__init__('There was an issue when trying to connect to chiasenhac.vn.')

class NotFoundError(Error):
    def __init__(self, message: str):
        super().__init__(message)
