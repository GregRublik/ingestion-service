from fastapi import Request, status
from fastapi.responses import JSONResponse
from exceptions import APIException, DatabaseUnavailableException, ModelNotFoundException


async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.error
        }
    )


async def db_handler(request: Request, exc: DatabaseUnavailableException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.error
        },
    )


async def not_found_handler(request: Request, exc: ModelNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "success": False,
            "error": exc.detail
        },
    )
