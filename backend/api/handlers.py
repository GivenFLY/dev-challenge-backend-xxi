from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler
from rest_framework.response import Response as DRFResponse

from api.convert import exception_to_response_data


class APIExceptionExt(APIException):
    """An APIException with a response property that returns a DRFResponse.

    This is useful for returning a DRFResponse from a view that is not a DRF view."""

    def __init__(self, detail, code, extra_data=None):
        """Create a new APIExceptionExt.

        :param detail: The detail of the exception.
        :param code: The code of the exception."""
        super().__init__(detail, code)
        self.detail = detail or self.default_detail
        self.code = code or self.default_code
        self.extra_data = extra_data or None

    @property
    def response(self):
        """Return a DRFResponse that can be used in a view."""
        return DRFResponse(exception_to_response_data(self), status=self.status_code)

    def __call__(self, extra_data, *args, **kwargs):
        """Call to attach extra data to the exception."""
        self.extra_data = extra_data
        return self


def exception_handler_ext(exc, context):
    print("exception_handler_ext")
    response = exception_handler(exc, context)

    if response is not None:
        if isinstance(exc, APIException):
            response.data = exception_to_response_data(exc)
            response.status_code = (
                422 if response.status_code == 400 else response.status_code
            )

    return response
