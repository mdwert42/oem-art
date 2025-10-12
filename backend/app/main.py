from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import create_tables
from .routers import auth_router

# Create FastAPI application
app = FastAPI(
    title="Art.OEM API",
    description="Portfolio and e-commerce API for 3D printed and painted artwork",
    version="0.1.0"
)

# CORS middleware configuration
# TODO: Update allowed origins for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Event handler for startup
@app.on_event("startup")
async def startup_event():
    """
    Actions to perform on application startup.
    Creates database tables if they don't exist.
    """
    print("Starting up Art.OEM API...")
    create_tables()
    print("Database tables created/verified")


# Include routers
app.include_router(auth_router)


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint - API health check.
    """
    return {
        "message": "Art.OEM API",
        "version": "0.1.0",
        "status": "running"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {"status": "healthy"}
