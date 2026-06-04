import os
from fastapi import FastAPI
from dotenv import load_dotenv

# 1. Load file .env yang sudah kita buat sebelumnya
load_dotenv()

# 2. Inisialisasi aplikasi FastAPI
app = FastAPI(title="justcallquant API", version="0.1.0")

@app.get("/")
def read_root():
    # Mengambil test variable dari .env untuk memastikan konfigurasi aman
    secret_check = os.getenv("SECRET_KEY", "File .env tidak terbaca atau kosong")
    
    return {
        "status": "success",
        "message": "FastAPI engine is running smoothly!",
        "env_check": secret_check
    }

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}