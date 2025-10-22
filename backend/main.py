from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from routers import upload_router, parse_router
from utils.database import engine, init_db
from models import Base
import os

# Create database tables
print("Initializing database...")
Base.metadata.create_all(bind=engine)

# Set permissions on the database file
db_path = "database.db"
if os.path.exists(db_path):
    try:
        os.chmod(db_path, 0o666)
        print(f"✓ Database file permissions set: {db_path}")
    except Exception as e:
        print(f"⚠ Could not set permissions: {e}")

# Initialize FastAPI app
app = FastAPI(
    title="Credit Card Statement Parser API",
    description="Parse credit card statements from HDFC, ICICI, SBI, Axis, and AMEX",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    print(f"📂 Database location: {os.path.abspath('database.db')}")
    print(f"🌐 API Docs: http://localhost:8000/docs")
    print("=" * 50)

@app.get("/")
async def root():
    return {
        "message": "Credit Card Statement Parser API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/api/upload",
            "parse": "/api/parse",
            "history": "/api/history",
            "export": "/api/export/{statement_id}"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "CC Parser API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)