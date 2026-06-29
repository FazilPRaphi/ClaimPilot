from app.schemas.response import APIResponse


def success_response(
    message: str,
    data=None,
):
    return APIResponse(
        success=True,
        message=message,
        data=data,
    )


def error_response(
    message: str,
    errors=None,
):
    return APIResponse(
        success=False,
        message=message,
        errors=errors,
    )