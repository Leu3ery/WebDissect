class ApiError(Exception):
    """Domain error carrying a user-facing message and HTTP status code.

    Caught by a global handler (FA06) and rendered as an ApiResponse envelope.
    """

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class Unauthorized(ApiError):
    def __init__(self, message: str = "Not authenticated"):
        super().__init__(message, status_code=401)


class NotFound(ApiError):
    def __init__(self, message: str = "Not found"):
        super().__init__(message, status_code=404)
