# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from routers import upload_router, parse_router
from utils.database import engine
from models import Base
import os

# Create database tables
print("Initializing database...")
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Credit Card Statement Parser API",
    description="Parse credit card statements from HDFC, ICICI, SBI, Axis, and AMEX",
    version="1.0.0"
)

# CORS middleware - IMPORTANT for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload_router.router, prefix="/api", tags=["upload"])
app.include_router(parse_router.router, prefix="/api", tags=["parse"])

@app.on_event("startup")
async def startup_event():
    print("=" * 50)
    print("🚀 Credit Card Parser API Started")
    print("=" * 50)
    print(f"📂 Database location: {os.path.abspath('../data/database.db')}")
    print(f"🌐 API Docs: http://localhost:8000/docs")
    print(f"🎨 Frontend: Run 'streamlit run frontend/streamlit_app.py'")
    print("=" * 50)

@app.get("/")
async def root():
    return {
        "message": "Credit Card Statement Parser API",
        "version": "1.0.0",
        "frontend": "http://localhost:8501",
        "docs": "http://localhost:8000/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "CC Parser API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)