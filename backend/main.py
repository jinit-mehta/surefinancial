from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import upload, parse

app = FastAPI(title="Credit Card Statement Parser")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(parse.router, prefix="/parse", tags=["parse"])

@app.get("/")
def root():
    return {"service": "credit-card-statement-parser", "status": "ok"}
