from ..LpmException import LpmException


class DownloadError(LpmException):
    pass

class VersionNotAvailableError(DownloadError):
    pass