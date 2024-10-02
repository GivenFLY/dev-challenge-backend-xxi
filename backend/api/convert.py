def exception_to_response_data(exception) -> dict:
    """Convert an APIException to a dict that can be used as response data.

    :param exception: The APIExceptionExt to convert.
    :return: A dict that can be used as response data.
    """
    if not hasattr(exception, "extra_data"):
        return {
            "detail": exception.detail,
        }

    return {
        "detail": exception.detail,
        **exception.extra_data,
    }
