class S3Error(Exception):
    pass

class S3KeyNotFound(S3Error):
    pass
