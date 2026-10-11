
from fastapi import HTTPException, status


class APIError(HTTPException):
    """An application-level API error with a chosen HTTP status."""

    def __init__(
        self,
        status_code: int,
        detail: str,
    ) -> None:
        super().__init__(
            status_code=status_code,
            detail=detail,
        )


def resource_not_found(detail: str = "Resource not found") -> APIError:
    """Create a standard 404 API error."""
    return APIError(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail,
    )
