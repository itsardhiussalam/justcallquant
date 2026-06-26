from fastapi import FastAPI
from dotenv import load_dotenv

from routers import macro
from routers import sentiment

load_dotenv()

app = FastAPI(
    title="justcallquant API",
    description="Backend Core Engine untuk Analisis Finansial & AI Agent",
    version="0.1.0",
)

app.include_router(macro.router)
app.include_router(sentiment.router)
# app.include_router(technical.router)
# app.include_router(fundamental.router)
# app.include_router(sentiment.router)


@app.get("/")
def read_root():
    return {
        "status": "success",
        "message": "FastAPI engine is running smoothly!",
    }