from fastapi import FastAPI
from api.v1.endpoints import document, normalization
import uvicorn
from config import settings
from exceptions import APIException
from exception_handlers import api_exception_handler

app = FastAPI()

app.include_router(document.router, tags=["document"])
app.include_router(normalization.router, tags=["normalization"])

app.add_exception_handler(APIException, api_exception_handler)

if __name__ == '__main__':
    uvicorn.run(app, host=settings.host, port=settings.port)
