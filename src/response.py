from schemas.response import APIResponse
from fastapi.routing import APIRoute
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


class UnifiedResponseRoute(APIRoute):
    def get_route_handler(self):
        original_handler = super().get_route_handler()

        async def custom_route_handler(request):
            response = await original_handler(request)

            # если это уже JSONResponse (например HTTPException) — не трогаем
            if isinstance(response, JSONResponse):
                return response

            return JSONResponse(
                content={
                    "success": True,
                    "data": jsonable_encoder(response)
                }
            )

        return custom_route_handler


def ok(data):
    return APIResponse(success=True, data=data)
