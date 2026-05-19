from fastapi import FastAPI
from api.v1.endpoints import document, normalization, chunk, embedding, health
import uvicorn
from config import settings
from exceptions import APIException, DatabaseUnavailableException
from exception_handlers import api_exception_handler, db_handler

app = FastAPI()

app.include_router(health.router, tags=["health"])
app.include_router(document.router, tags=["documents"])
app.include_router(normalization.router, tags=["normalization"])
app.include_router(chunk.router, tags=["chunk"])
app.include_router(embedding.router, tags=["embedding"])

app.add_exception_handler(APIException, api_exception_handler)
# app.add_exception_handler(DatabaseUnavailableException, db_handler)

if __name__ == '__main__':
    uvicorn.run(app, host=settings.host, port=settings.port)
