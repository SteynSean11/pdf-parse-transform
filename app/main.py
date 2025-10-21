"""FastAPI application main entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app import __version__

# Create FastAPI app
app = FastAPI(
    title="PDF Parse Transform",
    description="A FastAPI service for parsing and transforming PDF documents",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router, prefix="/api/v1", tags=["PDF Processing"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "PDF Parse Transform",
        "version": __version__,
        "docs": "/docs",
        "api": "/api/v1"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
