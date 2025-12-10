from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, users, operations, supervision, audit, context, training

app = FastAPI(title="Bluegrid OCR API", version="6.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(operations.router, prefix="/api/v1")
app.include_router(training.router, prefix="/api/v1")
# Incluir los demás igual...

@app.get("/")
def home():
    return {"status": "online", "system": "Bluegrid OCR v6.0"}