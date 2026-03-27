from fastapi import FastAPI
from api.v1.endpoints.document import router
import uvicorn
from config import settings

app = FastAPI()

app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(app, host=settings.host, port=settings.port)
