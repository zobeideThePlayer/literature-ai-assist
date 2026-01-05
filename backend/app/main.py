from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import get_settings
from app.database import init_db
from app.routers import reviews_router, papers_router, analysis_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown (cleanup if needed)


app = FastAPI(
    title=settings.app_name,
    description="AI-powered literature review assistant for researchers",
    version="0.1.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(reviews_router)
app.include_router(papers_router)
app.include_router(analysis_router)


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
