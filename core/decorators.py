import logging

from django.http import JsonResponse

from core.exceptions import AppException

logger = logging.getLogger(__name__)


def handler_api_errors(func):
    """Decorator for handling API errors."""

    def wrapper(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except AppException as e:
            logger.error(
                f"Business error: {e.message} (status_code={e.status_code}, details={e.details})")

            return JsonResponse({
                "success": False,
                "error": {
                    "message": e.message,
                    "status_code": e.status_code,
                    "details": e.details,
                }
            }, status=e.status_code)
        except Exception as e:
            logger.critical(f"Unexpected error: {str(e)}", exc_info=True)
            return JsonResponse({
                "error":
                    {
                        "message": "Internal server error",
                        "status_code": 500,
                        "details": str(e),
                    }
            }, status=500)

    return wrapper
