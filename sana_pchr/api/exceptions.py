from restless.exceptions import HttpError


class ValidationError(HttpError):
    status = 412

    def __init__(self, errors):
        msg = errors.__repr__()
        self.data = errors
        if hasattr(self.data, "error_dict"):
            self.data = {k: [list(x) for x in v] for k, v in self.data.error_dict.items()}
        super(ValidationError, self).__init__(msg)
