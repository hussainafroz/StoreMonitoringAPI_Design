from fastapi import FastAPI
from config import SessionLocal, engine
import models
from router import store_router

models.Base.metadata.create_all(bind=engine)


app = FastAPI()


@app.get("/")
async def Home():
    return {"Welcome": "Sweet India"}

app.include_router(store_router, prefix="/store", tags=["store"])
